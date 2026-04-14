"""
Scraper: Personas Desaparecidas y Extraviadas - SIFEBU
Fuente: https://www.argentina.gob.ar/seguridad/personasextraviadas
Organismo: Ministerio de Seguridad de la Nación
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

from bs4 import BeautifulSoup

BASE_URL = "https://www.argentina.gob.ar"
LIST_URL = f"{BASE_URL}/seguridad/personasextraviadas"
DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "personas_desaparecidas"
)

CURL_HEADERS = [
    "-A",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "-H",
    "Accept-Language: es-AR,es;q=0.9",
]


# ---------------------------------------------------------------------------
# Helpers de red
# ---------------------------------------------------------------------------


def _fetch(url: str, retries: int = 3, delay: float = 1.5) -> bytes:
    """GET con reintentos y delay cortés."""
    for attempt in range(retries):
        result = subprocess.run(
            ["curl", "-s", "-L", *CURL_HEADERS, url],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
        time.sleep(delay)
    raise ConnectionError(f"No se pudo obtener: {url} (intentos: {retries})")


# ---------------------------------------------------------------------------
# Scraping del listado paginado
# ---------------------------------------------------------------------------


def _get_total_pages() -> int:
    """Determina cuántas páginas tiene el listado."""
    html = _fetch(LIST_URL)
    soup = BeautifulSoup(html, "html.parser")

    # Los links de paginación tienen el patrón ?page=N
    page_links = soup.select("a[href*='page=']")
    max_page = 0
    for a in page_links:
        m = re.search(r"page=(\d+)", a["href"])
        if m:
            max_page = max(max_page, int(m.group(1)))

    # max_page es 0-indexed, total = max_page + 1
    return max_page + 1


def _parse_list_page(html: bytes) -> list[dict]:
    """
    Extrae los slugs y nombres de una página del listado.
    Devuelve lista de {"nombre": str, "url": str, "slug": str}
    """
    soup = BeautifulSoup(html, "html.parser")
    personas = []

    for a in soup.select("a[href^='/persona-buscada/']"):
        nombre = a.get_text(strip=True)
        href = a["href"]
        slug = href.split("/persona-buscada/")[-1].strip("/")
        if nombre and slug:
            personas.append(
                {
                    "nombre": nombre,
                    "url": BASE_URL + href,
                    "slug": slug,
                }
            )

    return personas


def _scrape_all_slugs() -> list[dict]:
    """Recorre todas las páginas del listado y devuelve los stubs."""
    total = _get_total_pages()
    print(f"      Total de páginas detectadas: {total}")

    all_personas = []
    for page in range(total):
        url = LIST_URL if page == 0 else f"{LIST_URL}?page={page}"
        html = _fetch(url)
        personas = _parse_list_page(html)
        all_personas.extend(personas)
        print(f"      Página {page + 1}/{total}: {len(personas)} personas")
        time.sleep(0.8)  # cortesía al servidor

    return all_personas


# ---------------------------------------------------------------------------
# Scraping del detalle de cada persona
# ---------------------------------------------------------------------------

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

# Años razonables para una desaparición (excluye fechas de nacimiento históricas, etc.)
_ANIO_MIN_DESAPARICION = 1970
_ANIO_MAX_DESAPARICION = datetime.today().year


def _anio_valido(y: int) -> bool:
    return _ANIO_MIN_DESAPARICION <= y <= _ANIO_MAX_DESAPARICION


def _normalizar_fecha_numerica(texto: str) -> str:
    """Elimina espacios internos en fechas numéricas: '01/ 08/ 2016' → '01/08/2016'."""
    return re.sub(r"(\d)\s*/\s*(\d)", r"\1/\2", texto)


def _fecha_numerica_a_iso(
    texto: str, buscar_despues_de: str | None = None
) -> str | None:
    """
    Formatos numéricos soportados:
      - DD/MM/YYYY o DD-MM-YYYY        → estándar
      - DD/MM/YY                       → año de 2 dígitos (ej: 03/09/19 → 2019)
      - DD/MMYYYY                      → mes y año pegados (ej: 23/102024)
      - Con espacios: DD/ MM/ YYYY     → normalizado antes de parsear

    Si se pasa `buscar_despues_de`, solo considera fechas que aparecen
    DESPUÉS de esa subcadena en el texto (para evitar tomar fechas de nacimiento
    cuando la línea contiene múltiples fechas).
    """
    texto_norm = _normalizar_fecha_numerica(texto)

    # Si hay un segmento de referencia, recortar el texto desde ahí
    if buscar_despues_de:
        idx = texto_norm.lower().find(buscar_despues_de.lower())
        if idx != -1:
            texto_norm = texto_norm[idx:]

    # DD/MM/YYYY o DD-MM-YYYY
    m = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", texto_norm)
    if m:
        d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), int(m.group(3))
        if 1 <= int(mo) <= 12 and _anio_valido(y):
            return f"{y}-{mo}-{d}"

    # DD/MM/YY — año de 2 dígitos, expandir al siglo correcto
    m = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2})\b", texto_norm)
    if m:
        d, mo = m.group(1).zfill(2), m.group(2).zfill(2)
        yy = int(m.group(3))
        # 00-29 → 2000-2029, 30-99 → 1930-1999
        y = 2000 + yy if yy <= 29 else 1900 + yy
        if 1 <= int(mo) <= 12 and _anio_valido(y):
            return f"{y}-{mo}-{d}"

    # DD/MMYYYY — mes y año pegados sin separador
    m = re.search(r"(\d{1,2})/(\d{1,2})(\d{4})\b", texto_norm)
    if m:
        d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), int(m.group(3))
        if 1 <= int(mo) <= 12 and _anio_valido(y):
            return f"{y}-{mo}-{d}"

    return None


def _fecha_textual_a_iso(
    texto: str, buscar_despues_de: str | None = None
) -> str | None:
    """
    Fechas en español. Variantes cubiertas:
      - "18 de septiembre de 2006"
      - "18 de septiembre del 2006"
      - "18 de septiembre del año 2006"
      - "18 de septiembre 2006"
      - Mes con mayúscula: "8 de Marzo de 2014"

    Si se pasa `buscar_despues_de`, solo busca después de esa subcadena.
    """
    if buscar_despues_de:
        idx = texto.lower().find(buscar_despues_de.lower())
        if idx != -1:
            texto = texto[idx:]

    m = re.search(
        r"(\d{1,2})\s+de\s+(\w+?)(?:\s+del?\s+(?:a[ñn]o\s+)?|\s+)(\d{4})\b",
        texto,
        re.IGNORECASE,
    )
    if m:
        d = m.group(1).zfill(2)
        mes_str = m.group(2).lower()
        y = int(m.group(3))
        if mes_str in MESES_ES and _anio_valido(y):
            return f"{y}-{MESES_ES[mes_str]}-{d}"
    return None


def _extraer_fecha_de_linea(
    linea: str, buscar_despues_de: str | None = None
) -> str | None:
    """Intenta todos los formatos conocidos sobre una línea."""
    return _fecha_numerica_a_iso(linea, buscar_despues_de) or _fecha_textual_a_iso(
        linea, buscar_despues_de
    )


# ---------------------------------------------------------------------------
# Señales textuales que indican que una línea contiene la fecha de desaparición.
# Cada entrada es (regex_etiqueta, subcadena_ancla_opcional).
# La ancla se pasa a _extraer_fecha_de_linea para que busque la fecha DESPUÉS
# de esa subcadena — necesario cuando la línea tiene múltiples fechas.
# ---------------------------------------------------------------------------
_ETIQUETAS_DESAPARICION: list[tuple[re.Pattern, str | None]] = [
    # Campos estructurados — anclar después de la etiqueta para evitar tomar nacimiento
    (re.compile(r"fecha\s+de\s+desaparici[oó]n\s*:", re.I), "desaparici"),
    (re.compile(r"fecha\s+de\s+ausencia\s*:", re.I), "ausencia:"),
    (re.compile(r"vista?\s+por\s+[uú]ltima\s+vez\s*:", re.I), None),
    (re.compile(r"visto\s+por\s+[uú]ltima\s+vez\s*:", re.I), None),
    (re.compile(r"[uú]ltima\s+vez\s+visto\s*:", re.I), None),
    # "Desaparecida/o/ido/ida desde el"
    (re.compile(r"desapareci[dao]+\s+desde\s+el\b", re.I), "desde el"),
    # "Ausente desde el"
    (re.compile(r"ausente\s+desde\s+el\b", re.I), "desde el"),
    # "Vista/Visto por última vez el día"
    (re.compile(r"vista?\s+por\s+[uú]ltima\s+vez\s+el\s+d[ií]a\b", re.I), "el día"),
    (re.compile(r"visto\s+por\s+[uú]ltima\s+vez\s+el\s+d[ií]a\b", re.I), "el día"),
    (
        re.compile(r"fue\s+vista?\s+por\s+[uú]ltima\s+vez\s+el\s+d[ií]a\b", re.I),
        "el día",
    ),
    (
        re.compile(r"fue\s+visto\s+por\s+[uú]ltima\s+vez\s+el\s+d[ií]a\b", re.I),
        "el día",
    ),
    # "Vista/Visto por última vez el" (sin "día")
    (re.compile(r"fue\s+vista?\s+por\s+[uú]ltima\s+vez\s+el\b", re.I), "el"),
    (re.compile(r"fue\s+visto\s+por\s+[uú]ltima\s+vez\s+el\b", re.I), "el"),
    (re.compile(r"vista?\s+por\s+[uú]ltima\s+vez\s+el\b", re.I), "el"),
    # Verbos de desaparición
    (re.compile(r"desapareci[oó]\s+el\s+d[ií]a\b", re.I), "el día"),
    (re.compile(r"desapareciera\s+el\s+d[ií]a\b", re.I), "el día"),
    (re.compile(r"desapareci[oó]\s+el\b", re.I), "el"),
    # "tuviera lugar el día" / "ausentara ... el día"
    (re.compile(r"tuviera\s+lugar\s+el\s+d[ií]a\b", re.I), "el día"),
    (re.compile(r"ausentar[oa]\s+.{0,30}el\s+d[ií]a\b", re.I), "el día"),
    # "al momento de (la|su) ausencia"
    (re.compile(r"al\s+momento\s+de\s+(?:la|su)\s+ausencia", re.I), None),
    # "años de su ausencia" / "años al momento de la ausencia"
    (
        re.compile(
            r"a[ñn]os\s+(?:de\s+su|al\s+momento\s+de(?:\s+la)?)\s+ausencia", re.I
        ),
        None,
    ),
    # "se perdió el rastro"
    (re.compile(r"se\s+perdi[oó]\s+el\s+rastro.{0,30}el\s+d[ií]a\b", re.I), "el día"),
    (re.compile(r"se\s+perdi[oó]\s+el\s+rastro", re.I), None),
    # "se lo/la vio por última vez"
    (re.compile(r"se\s+lo\s+vio\s+por\s+[uú]ltima\s+vez", re.I), None),
    (re.compile(r"se\s+la\s+vio\s+por\s+[uú]ltima\s+vez", re.I), None),
]

# Etiquetas que jamás deben usarse como fuente de fecha de desaparición
_ETIQUETAS_IGNORAR = re.compile(r"fecha\s+de\s+nacimiento\s*:", re.I)


def _extraer_fecha_desaparicion(soup: BeautifulSoup) -> str | None:
    """
    Estrategia en capas, de más a menos específica:

    CAPA 1 — Etiqueta detectada en la línea, fecha en la misma línea
              (con ancla opcional para saltar fechas de nacimiento en la misma línea)
    CAPA 2 — Etiqueta en la línea, fecha en la línea siguiente

    Nunca extrae fechas de líneas con "Fecha de nacimiento".
    """
    lines = [l.strip() for l in soup.get_text("\n").splitlines() if l.strip()]

    for etiqueta, ancla in _ETIQUETAS_DESAPARICION:
        for i, line in enumerate(lines):
            if not etiqueta.search(line):
                continue
            if _ETIQUETAS_IGNORAR.search(line) and not re.search(
                r"fecha\s+de\s+desaparici", line, re.I
            ):
                continue

            # Capa 1: fecha en la misma línea (usando ancla si la hay)
            fecha = _extraer_fecha_de_linea(line, ancla)
            if fecha:
                return fecha

            # Capa 2: fecha en la línea siguiente
            if i + 1 < len(lines):
                fecha = _extraer_fecha_de_linea(lines[i + 1])
                if fecha:
                    return fecha

    return None


def _extraer_recompensa(soup: BeautifulSoup) -> dict:
    """
    Extrae si hay recompensa y su monto.

    El HTML tiene el monto en: <p class="recompensa"><b>Recompensa: $ 5.000.000</b></p>
    Apuntamos directo a ese selector. Como fallback también buscamos en get_text()
    para cubrir variantes de estructura.
    """
    # Selector exacto según HTML inspeccionado
    nodo = soup.select_one("p.recompensa")
    if nodo:
        texto = nodo.get_text(" ", strip=True).replace("\xa0", " ")
        m = re.search(r"\$\s*([\d.,]+)", texto)
        if m:
            numero = re.sub(r"\s+", "", m.group(1))
            return {"tiene_recompensa": True, "monto": f"${numero}"}
        return {"tiene_recompensa": True, "monto": None}

    return {"tiene_recompensa": False, "monto": None}


def _extraer_descripcion(soup: BeautifulSoup) -> str | None:
    """
    Extrae el texto de la ficha desde el nodo exacto que lo contiene:
      div.field-name-body > div.field-items > div.field-item

    Ese div puede contener uno o más <p> con el texto del caso.
    Se concatenan y limpian nbsp y espacios múltiples.
    """
    field_body = soup.select_one(
        "div.field-name-body div.field-item, "
        "div.field-type-text-with-summary div.field-item"
    )
    if field_body:
        texto = field_body.get_text(" ", strip=True)
        texto = re.sub(r"\s+", " ", texto.replace("\xa0", " ")).strip()
        if texto:
            return texto
    return None


def _scrape_detalle(stub: dict) -> dict:
    """
    Visita la página individual de una persona y extrae:
      - fecha_desaparicion (YYYY-MM-DD | None)
      - anio_desaparicion (int | None)
      - recompensa: {"tiene_recompensa": bool, "monto": str | None}
      - descripcion (str | None)
      - foto_url (str | None)
    """
    fallback = {
        **stub,
        "fecha_desaparicion": None,
        "anio_desaparicion": None,
        "recompensa": {"tiene_recompensa": False, "monto": None},
        "descripcion": None,
        "foto_url": None,
    }

    try:
        html = _fetch(stub["url"])
    except ConnectionError:
        return fallback

    soup = BeautifulSoup(html, "html.parser")

    fecha = _extraer_fecha_desaparicion(soup)
    anio = int(fecha[:4]) if fecha else None
    recompensa = _extraer_recompensa(soup)
    descripcion = _extraer_descripcion(soup)

    # Foto principal: primera imagen que no sea logo ni ícono del sitio
    foto_url = None
    SKIP_FOTO = ["logo", "denuncia_134", "busqueda_personas", "argentinagobar", ".svg"]
    for img in soup.select("img[src]"):
        src = img["src"]
        if any(skip in src for skip in SKIP_FOTO):
            continue
        if src.endswith((".jpg", ".jpeg", ".png", ".webp")):
            foto_url = src if src.startswith("http") else BASE_URL + src
            break

    return {
        **stub,
        "fecha_desaparicion": fecha,
        "anio_desaparicion": anio,
        "recompensa": recompensa,
        "descripcion": descripcion,
        "foto_url": foto_url,
    }


# ---------------------------------------------------------------------------
# Construcción del dataset
# ---------------------------------------------------------------------------


def _build_dataset(personas: list[dict]) -> dict:
    """
    Construye el JSON final agrupado por año y con resumen estadístico.
    """
    # Agrupar por año
    por_anio: dict[str, list] = {}
    sin_fecha = []

    for p in personas:
        anio = p.get("anio_desaparicion")
        entry = {
            "nombre": p["nombre"],
            "slug": p["slug"],
            "url": p["url"],
            "fecha_desaparicion": p.get("fecha_desaparicion"),
            "recompensa": p.get(
                "recompensa", {"tiene_recompensa": False, "monto": None}
            ),
            "descripcion": p.get("descripcion"),
            "foto_url": p.get("foto_url"),
        }
        if anio:
            key = str(anio)
            por_anio.setdefault(key, []).append(entry)
        else:
            sin_fecha.append(entry)

    # Resumen
    resumen = {str(k): len(v) for k, v in sorted(por_anio.items())}
    if sin_fecha:
        resumen["sin_fecha"] = len(sin_fecha)

    return {
        "fuente": "SIFEBU - Ministerio de Seguridad de la Nación",
        "url_fuente": LIST_URL,
        "total": len(personas),
        "resumen_por_anio": resumen,
        "por_anio": {
            k: sorted(v, key=lambda x: x["fecha_desaparicion"] or "")
            for k, v in sorted(por_anio.items())
        },
        "sin_fecha": sin_fecha,
    }


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------


def _save(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)

    today = datetime.today().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"{today}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado: data/personas_desaparecidas/{today}.json")

    latest_path = os.path.join(DATA_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[OK] Actualizado: data/personas_desaparecidas/latest.json")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run():
    print("[START] Scraper Personas Desaparecidas SIFEBU")

    try:
        print("[1/4] Relevando páginas del listado...")
        stubs = _scrape_all_slugs()
        print(f"      Total de personas encontradas: {len(stubs)}")

        print("[2/4] Scrapeando detalle de cada persona...")
        personas = []
        for i, stub in enumerate(stubs, 1):
            detalle = _scrape_detalle(stub)
            personas.append(detalle)
            if i % 10 == 0:
                print(f"      Procesadas: {i}/{len(stubs)}")
            time.sleep(0.5)

        print("[3/4] Construyendo dataset...")
        data = _build_dataset(personas)
        print(f"      Total: {data['total']}")
        print(f"      Años con datos: {list(data['resumen_por_anio'].keys())}")

        print("[4/4] Guardando JSONs...")
        _save(data)

        print("[DONE]")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
