"""
Scraper: Canasta Básica Alimentaria y Total - INDEC
Fuente: https://www.indec.gob.ar/indec/web/Nivel3-Tema-4-43
"""

import io
import json
import os
import re
import subprocess
import sys
import tempfile
from calendar import monthrange

import pdfplumber
from bs4 import BeautifulSoup

INDEC_PAGE = "https://www.indec.gob.ar/Nivel3/Tema/4/43"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "canasta")

MESES_ES = {
    "enero": "01",
    "febrero": "02",
    "marzo": "03",
    "abril": "04",
    "mayo": "05",
    "junio": "06",
    "julio": "07",
    "agosto": "08",
    "septiembre": "09",
    "octubre": "10",
    "noviembre": "11",
    "diciembre": "12",
}

HOGARES = {
    "hogar_1": {
        "integrantes": 3,
        "descripcion": "Mujer de 35 años, hijo de 18 años y madre de 61 años",
    },
    "hogar_2": {
        "integrantes": 4,
        "descripcion": "Varón de 35 años, mujer de 31 años, hijo de 6 años e hija de 8 años",
    },
    "hogar_3": {
        "integrantes": 5,
        "descripcion": "Varón y mujer de 30 años con hijos de 1, 3 y 5 años",
    },
}

ROW_RE = re.compile(
    r"(?:(\d{4})\s+)?"
    r"(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)\s+"
    r"([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+"
    r"(-?[\d,]+)\s+([\d,]+)\s+([\d,]+)",
    re.IGNORECASE,
)

# Prioridades de búsqueda de PDF, de más específica a menos
_PDF_PATTERNS = [
    # 1. Nombre exacto del informe que nos interesa (canasta básica, no crianza)
    lambda h: "canasta" in h and "crianza" not in h and h.endswith(".pdf"),
    # 2. Cualquier PDF que no sea de crianza (fallback)
    lambda h: h.endswith(".pdf") and "crianza" not in h,
]


def _parse_float(text: str) -> float:
    return float(text.strip().replace(".", "").replace(",", "."))


def _to_absolute_url(href: str) -> str:
    if href.startswith("http"):
        return href
    return "https://www.indec.gob.ar" + href


def _get_pdf_url() -> str:
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-L",
            "-A",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            INDEC_PAGE,
        ],
        capture_output=True,
        timeout=30,
    )
    soup = BeautifulSoup(result.stdout, "html.parser")
    hrefs = [a["href"] for a in soup.find_all("a", href=True)]

    for pattern in _PDF_PATTERNS:
        for href in hrefs:
            if pattern(href.lower()):
                url = _to_absolute_url(href)
                print(f"      PDF seleccionado: {href}")
                return url

    raise ValueError("No se encontró el PDF de Canasta Básica en la página del INDEC")


def _download_pdf(pdf_url: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmpdir:
        cookie_file = os.path.join(tmpdir, "cookies.txt")
        pdf_file = os.path.join(tmpdir, "canasta.pdf")

        # Paso 1: visitar la página para obtener cookies
        subprocess.run(
            [
                "curl",
                "-s",
                "-L",
                "-c",
                cookie_file,
                "-A",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "-H",
                "Accept-Language: es-AR,es;q=0.9",
                INDEC_PAGE,
            ],
            capture_output=True,
            timeout=30,
        )

        # Paso 2: descargar el PDF con las cookies obtenidas
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-L",
                "-b",
                cookie_file,
                "-c",
                cookie_file,
                "-A",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "-H",
                f"Referer: {INDEC_PAGE}",
                "-H",
                "Accept: application/pdf,*/*",
                "-o",
                pdf_file,
                "-w",
                "%{http_code}",
                pdf_url,
            ],
            capture_output=True,
            timeout=60,
        )

        http_code = result.stdout.decode().strip()
        if http_code != "200":
            raise ConnectionError(
                f"Error al descargar el PDF (HTTP {http_code}): {pdf_url}"
            )

        with open(pdf_file, "rb") as f:
            return f.read()


def _extract_pages(pdf) -> tuple:
    """
    Devuelve (page_fecha, page_cba, page_cbt) buscando por contenido
    en lugar de asumir índices fijos.
    """
    texts = [p.extract_text() or "" for p in pdf.pages]

    # La página de fecha tiene "Buenos Aires,"
    page_fecha = next(
        (t for t in texts if "Buenos Aires," in t),
        texts[2] if len(texts) > 2 else "",
    )

    # CBA: página que menciona "Alimentaria" y tiene filas de datos
    page_cba = next(
        (t for t in texts if "Alimentaria" in t and ROW_RE.search(t)),
        texts[3] if len(texts) > 3 else "",
    )

    # CBT: página que menciona "Básica Total" y tiene filas de datos
    page_cbt = next(
        (t for t in texts if "Básica Total" in t and ROW_RE.search(t)),
        texts[4] if len(texts) > 4 else "",
    )

    return page_fecha, page_cba, page_cbt


def _parse_pdf(pdf_bytes: bytes) -> dict:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_fecha, page_cba, page_cbt = _extract_pages(pdf)

    # Fecha de publicación
    fecha_pub = None
    match = re.search(
        r"Buenos Aires,\s+(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})",
        page_fecha,
        re.IGNORECASE,
    )
    if match:
        day = match.group(1).zfill(2)
        mes_str = match.group(2).lower()
        year = match.group(3)
        if mes_str in MESES_ES:
            fecha_pub = f"{year}-{MESES_ES[mes_str]}-{day}"

    cba_rows = ROW_RE.findall(page_cba)
    cbt_rows = ROW_RE.findall(page_cbt)

    if not cba_rows or not cbt_rows:
        print("[DEBUG] Primeros 500 chars de page_cba:")
        print(page_cba[:500])
        print("[DEBUG] Primeros 500 chars de page_cbt:")
        print(page_cbt[:500])
        raise ValueError(
            f"No se encontraron filas de datos en el PDF. "
            f"CBA rows: {len(cba_rows)}, CBT rows: {len(cbt_rows)}"
        )

    cba_last = cba_rows[-1]
    cbt_last = cbt_rows[-1]

    current_year = max(int(r[0]) for r in cba_rows if r[0])
    mes_str = cba_last[1].lower()
    mes_num = MESES_ES[mes_str]
    last_day = monthrange(current_year, int(mes_num))[1]

    def _build(row):
        _, _, adulto, h1, h2, h3, var_mens, var_acum, var_inter = row
        return {
            "variacion_mensual": _parse_float(var_mens),
            "variacion_acumulada_anio": _parse_float(var_acum),
            "variacion_interanual": _parse_float(var_inter),
            "adulto_equivalente": _parse_float(adulto),
            "hogares": {
                k: {**v, "valor": _parse_float(val)}
                for (k, v), val in zip(HOGARES.items(), [h1, h2, h3])
            },
        }

    return {
        "periodo": f"{current_year}-{mes_num}",
        "filename_date": f"{current_year}-{mes_num}-{last_day:02d}",
        "fecha_publicacion": fecha_pub,
        "fuente": "INDEC - Dirección Nacional de Estadísticas de Precios",
        "cba": _build(cba_last),
        "cbt": _build(cbt_last),
    }


def _save(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)

    filename_date = data.pop("filename_date")
    filepath = os.path.join(DATA_DIR, f"{filename_date}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado: data/canasta/{filename_date}.json")

    latest_path = os.path.join(DATA_DIR, "latest.json")
    should_update = True
    if os.path.exists(latest_path):
        with open(latest_path) as f:
            current = json.load(f)
        should_update = data["periodo"] >= current.get("periodo", "")

    if should_update:
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Actualizado: data/canasta/latest.json")


def run():
    print("[START] Scraper Canasta Básica INDEC")

    try:
        print("[1/4] Buscando URL del PDF...")
        pdf_url = _get_pdf_url()
        print(f"      {pdf_url}")

        print("[2/4] Descargando PDF...")
        pdf_bytes = _download_pdf(pdf_url)
        print(f"      {len(pdf_bytes) // 1024} KB")

        print("[3/4] Parseando PDF...")
        data = _parse_pdf(pdf_bytes)
        print(f"      Período:     {data['periodo']}")
        print(f"      Publicación: {data['fecha_publicacion']}")
        print(f"      CBA adulto:  ${data['cba']['adulto_equivalente']:,.2f}")
        print(f"      CBT adulto:  ${data['cbt']['adulto_equivalente']:,.2f}")

        print("[4/4] Guardando JSONs...")
        _save(data)

        print("[DONE]")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
