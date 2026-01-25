import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collections import defaultdict
import urllib3
from utils import save_dataset_json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import subprocess
import sys


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://contenidosweb.prefecturanaval.gob.ar/alturas/"


def fetch_html():
    """
    Usa curl del sistema para evitar bloqueos TLS de requests
    """
    try:
        html = subprocess.check_output(
            [
                "curl",
                "-L",
                "--silent",
                "--show-error",
                "--max-time",
                "30",
                "--connect-timeout",
                "10",
                "-A",
                "Mozilla/5.0 (X11; Linux x86_64)",
                URL,
            ],
            text=True,
        )
        if not html or len(html) < 500:
            return None
        return html

    except subprocess.CalledProcessError as e:
        print("❌ curl error:", e, file=sys.stderr)
        return None


def _session():
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def _to_float(text):
    try:
        text = text.strip()
        if text.upper() in ("S/E", "-", ""):
            return None
        return float(text.replace(",", "."))
    except Exception:
        return None


MONTHS = {
    "JAN": "01",
    "FEB": "02",
    "MAR": "03",
    "APR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AUG": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DEC": "12",
}


def parse_fecha_hora(raw):
    """
    Ej: '25/JAN/26 - 0900'
    -> ('2026-01-25', '09:00')
    """
    if not raw or "-" not in raw:
        return None, None

    try:
        date_part, time_part = [p.strip() for p in raw.split("-")]

        day, mon, year = date_part.split("/")
        month = MONTHS.get(mon.upper())
        full_year = f"20{year}"

        fecha = f"{full_year}-{month}-{day.zfill(2)}"
        hora = f"{time_part[:2]}:{time_part[2:]}"

        return fecha, hora
    except Exception:
        return None, None


def normalizar_estado(raw):
    raw = raw.strip().upper()

    if raw == "CRECE":
        return "crece"
    if raw == "BAJA":
        return "baja"
    if raw.startswith("ESTAC"):
        return "estac"
    if raw in ("S/E", "SE"):
        return "s/e"

    return "desconocido"


def obtener_estado_rios():
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120 Safari/537.36"}

    # res = requests.get(URL, headers=headers, verify=False)
    html = fetch_html()
    if not html:
        print("⚠ No se pudo obtener HTML desde Prefectura")
        return None

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")

    if not table:
        return None

    rios = defaultdict(list)

    for row in table.find("tbody").find_all("tr"):
        th = row.find("th")  # Puerto
        cols = row.find_all("td")

        if not th or len(cols) < 6:
            continue

        puerto = th.get_text(strip=True)
        rio = cols[0].get_text(strip=True)

        altura = _to_float(cols[1].get_text(strip=True))
        variacion = _to_float(cols[2].get_text(strip=True))
        periodo = cols[3].get_text(strip=True)

        fecha_hora_raw = cols[4].get_text(strip=True)
        fecha, hora = parse_fecha_hora(fecha_hora_raw)

        estado = normalizar_estado(cols[5].get_text(strip=True))

        rios[rio].append(
            {
                "nombre": puerto,
                "altura_m": altura,
                "variacion_m": variacion,
                "periodo": periodo,
                "estado": estado,
                "fecha": fecha,
                "hora": hora,
            }
        )

    resultado = {
        "source": "prefectura_naval_argentina",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "rios": [],
    }

    for rio, puertos in rios.items():
        alturas = [
            p["altura_m"] for p in puertos if isinstance(p["altura_m"], (int, float))
        ]

        resumen = {
            "puertos_total": len(puertos),
            "crece": sum(1 for p in puertos if p["estado"] == "crece"),
            "baja": sum(1 for p in puertos if p["estado"] == "baja"),
            "estac": sum(1 for p in puertos if p["estado"] == "estac"),
            "s/e": sum(1 for p in puertos if p["estado"] == "s/e"),
            "altura_promedio_m": (
                round(sum(alturas) / len(alturas), 2) if alturas else None
            ),
            "altura_max_m": max(alturas) if alturas else None,
            "altura_min_m": min(alturas) if alturas else None,
        }

        # estado general: ignora s/e
        estados_validos = ["baja", "estac", "crece"]
        estado_general = max(
            estados_validos,
            key=lambda e: sum(1 for p in puertos if p["estado"] == e),
        )

        resultado["rios"].append(
            {
                "nombre": rio,
                "estado_general": estado_general,
                "puertos": puertos,
                "resumen": resumen,
            }
        )

    return resultado


if __name__ == "__main__":
    try:
        data = obtener_estado_rios()
        if data:
            save_dataset_json(dataset="rios", data=[data])
        else:
            print("⚠ No se pudo obtener data de rios")
    except Exception as e:
        print(f"❌ Error scraping rios: {e}")
