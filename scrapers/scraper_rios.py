import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collections import defaultdict
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils import save_dataset_json

# Desactivar advertencias de SSL inseguro (necesario para gob.ar a veces)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://contenidosweb.prefecturanaval.gob.ar/alturas/"

# Configuración de headers para simular un navegador real en español
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.argentina.gob.ar/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def get_session():
    """
    Crea una sesión robusta con estrategia de reintentos y soporte de Proxy.
    """
    session = requests.Session()

    # Estrategia de reintentos: 3 intentos, con espera exponencial (backoff)
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,  # espera 2s, 4s, 8s...
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Checkear si hay un PROXY configurado en las variables de entorno
    proxy_str = os.environ.get("RIO_PROXY")
    if proxy_str:
        print(f"Usando Proxy configurado...")
        session.proxies = {"http": proxy_str, "https": proxy_str}

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
    session = get_session()

    try:
        # Timeout explícito de 30 segundos para evitar hang
        print(f"Conectando a {URL}...")
        res = session.get(URL, headers=HEADERS, verify=False, timeout=30)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error crítico al conectar: {e}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")

    if not table:
        print("No se encontró la tabla en el HTML")
        return None

    rios = defaultdict(list)

    tbody = table.find("tbody")
    if not tbody:
        return None

    for row in tbody.find_all("tr"):
        th = row.find("th")
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

        estados_validos = ["baja", "estac", "crece"]
        # Evitar crash si no hay estados válidos
        try:
            estado_general = max(
                estados_validos,
                key=lambda e: sum(1 for p in puertos if p["estado"] == e),
            )
        except ValueError:
            estado_general = "desconocido"

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
    data = obtener_estado_rios()
    if data:
        save_dataset_json(dataset="rios", data=[data])
    else:
        # Fallar el action si no hay datos para que te enteres
        exit(1)
