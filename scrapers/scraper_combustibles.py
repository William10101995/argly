import requests
from bs4 import BeautifulSoup
import time
import json
import re
from pathlib import Path
from utils import save_dataset_json

# CONFIGURACIÓN

PROVINCIAS = [
    "chaco",
    "corrientes",
    "buenos-aires",
    "capital-federal-caba",
    "catamarca",
    "chubut",
    "cordoba",
    "entre-rios",
    "formosa",
    "jujuy",
    "la-pampa",
    "la-rioja",
    "mendoza",
    "misiones",
    "neuquen",
    "rio-negro",
    "salta",
    "san-juan",
    "san-luis",
    "santa-cruz",
    "santa-fe",
    "santiago-del-estero",
    "tierra-del-fuego",
    "tucuman",
]

BASE_URL = "https://combustibles.ar/precios"

HEADERS = {"User-Agent": "Mozilla/5.0 (FuelScraper/1.0)"}


# HELPERS


def text_from_a(td):
    """Devuelve solo el texto del <a>, si existe"""
    a = td.find("a")
    return a.get_text(strip=True) if a else td.get_text(strip=True)


def parse_direccion(td):
    """Elimina el span 'Dirección:' y devuelve solo la dirección"""
    span = td.find("span")
    if span:
        span.extract()
    return td.get_text(strip=True)


def parse_precio(precio_raw):
    """
    Convierte:
    "$1.899 (Día)$1.899 (Noche)"
    en:
    { "dia": 1899, "noche": 1899 }
    """
    precios = {}

    matches = re.findall(r"\$([\d\.]+)\s*\((Día|Noche)\)", precio_raw)
    for valor, horario in matches:
        precios[horario.lower()] = int(valor.replace(".", ""))

    return precios


def make_key(provincia, empresa, localidad, direccion, combustible):
    """Clave única lógica para evitar duplicados"""
    return (
        provincia,
        empresa,
        localidad,
        direccion,
        combustible,
    )


# SCRAPER

resultados = {}
resultados.clear()  # IMPORTANTE para entornos persistentes

for provincia in PROVINCIAS:
    print(f"\n=== PROVINCIA: {provincia.upper()} ===")
    page = 1

    while True:
        if page == 1:
            url = f"{BASE_URL}/{provincia}"
        else:
            url = f"{BASE_URL}/{provincia}/pagina/{page}"

        print(f"Scrapeando: {url}")

        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table tbody tr")

        if not rows:
            break

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            empresa = text_from_a(cols[0])
            localidad = text_from_a(cols[1])
            direccion = parse_direccion(cols[2])
            combustible = text_from_a(cols[3])

            precio_raw = cols[4].get_text(strip=True).replace("Precio:", "")
            precios = parse_precio(precio_raw)

            vigencia = cols[5].get_text(strip=True).replace("Fecha:", "")

            key = make_key(
                provincia,
                empresa,
                localidad,
                direccion,
                combustible,
            )

            resultados[key] = {
                "provincia": provincia,
                "empresa": empresa,
                "localidad": localidad,
                "direccion": direccion,
                "combustible": combustible,
                "precios": precios,
                "vigencia": vigencia,
            }

        page += 1
        time.sleep(1)  # para no saturar el sitio

# EXPORTAR JSON (REEMPLAZA SIEMPRE)

save_dataset_json(dataset="combustibles", data=list(resultados.values()))
