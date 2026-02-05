import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collections import defaultdict
import urllib3
from utils import save_dataset_json

# Desactivar advertencias, aunque ScraperAPI maneja el SSL, es buena práctica mantenerlo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL real a la que queremos acceder
TARGET_URL = "https://contenidosweb.prefecturanaval.gob.ar/alturas/"

# Obtenemos la key desde los secretos de GitHub
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY")


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
    if not raw:
        return "s/e", None

    raw_clean = raw.strip().upper()

    if raw_clean == "CRECE":
        return "crece", raw_clean
    if raw_clean == "BAJA":
        return "baja", raw_clean
    if raw_clean.startswith("ESTAC"):
        return "estac", raw_clean
    if raw_clean in ("S/E", "SE", "S / E", "S.E.", "S/E."):
        return "s/e", raw_clean

    # Estado inesperado
    return "s/e", raw_clean


def obtener_estado_rios():
    if not SCRAPERAPI_KEY:
        print("Error: No se encontró la variable SCRAPERAPI_KEY")
        return None

    # Configuración para ScraperAPI
    payload = {
        "api_key": SCRAPERAPI_KEY,
        "url": TARGET_URL,
        "keep_headers": "true",  # Mantiene nuestros headers (útil para simular navegador)
        "premium": "true",  # Usar plan pago si está disponible
        "country_code": "ar",  # Opcional: Si tienes plan pago, descomenta esto para forzar IP argentina
    }

    # Headers para "engañar" al sitio final (se pasan a través de ScraperAPI)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"Contactando a Prefectura vía ScraperAPI...")

    try:
        # Llamamos a ScraperAPI, no directamente a Prefectura
        res = requests.get(
            "http://api.scraperapi.com", params=payload, headers=headers, timeout=60
        )

        if res.status_code != 200:
            print(f"Error en la petición: Status {res.status_code}")
            print(res.text)  # Para ver qué error devuelve la API
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con ScraperAPI: {e}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")

    if not table:
        print("No se encontró la tabla en el HTML devuelto")
        # A veces devuelven un captcha o página de error si detectan algo raro
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
        estado, estado_raw = normalizar_estado(cols[5].get_text(strip=True))

        rios[rio].append(
            {
                "nombre": puerto,
                "altura_m": altura,
                "variacion_m": variacion,
                "periodo": periodo,
                "estado": estado,
                "estado_raw": estado_raw,
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
        try:
            estado_general = max(
                estados_validos,
                key=lambda e: sum(1 for p in puertos if p["estado"] == e),
            )
        except ValueError:
            estado_general = "s/e"

        if resumen["puertos_total"] > 0:
            ratio_sin_estado = resumen["s/e"] / resumen["puertos_total"]

            if ratio_sin_estado > 0.5:
                estado_general = "s/e"

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
        # Forzamos error para que GitHub Actions te avise
        exit(1)
