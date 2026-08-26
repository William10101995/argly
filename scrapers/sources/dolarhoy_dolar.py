"""
Fuente: DolarHoy (dolarhoy.com)

Rol: FALLBACK de disponibilidad. Solo se consulta si Ambito no devolvio
ningun tipo (falla total) o si a un tipo puntual le falta el dato porque
Ambito no lo cubrio ese ciclo. Nunca pisa un dato que Ambito si trajo.

CONFIRMADO (curl + grep, 2026-08-10): dos fuentes de datos dentro de la
misma pagina, con selectores reales:

1) Tabla "Cotizaciones" al pie de la home (mas confiable, sin sponsors
   mezclados, misma seccion que usa combustibles/canasta como referencia
   de "entidad"):

    <div class="tile cotizaciones_more">
      <div class="tile is-parent is-6 is-vertical entidad">
        <div class="tile is-child">
          <a href="/cotizaciondolarblue">
            <div class="title">Dolar Libre</div>
            <div class="compra">1515,00</div>
            <div class="venta">1535,00</div>
          </a>
        </div>
        ...

   Cubre: Dolar Libre (blue), Dolar Mayorista, Dolar MEP (bolsa),
   Contado con liqui.

2) Tarjetas compactas en la parte superior (con sponsors mezclados para
   MEP/cripto, por eso NO se usan para esos tipos, solo para Oficial y
   Tarjeta que no aparecen en la tabla del punto 1):

    <div class="tile is-child">
      <div class="title"><a class="titleText" href="...">Dolar Oficial</a></div>
      <div class="values">
        <div class="compra">...<div class="val">$1470</div></div>
        <div class="venta">...<div class="val">$1520</div></div>

DolarHoy no publica "cripto" en esta pagina (si aparece "Dolar Digital
USDC" es un producto patrocinado, no una cotizacion neutral, se descarta
a proposito).
"""

import re
import requests
from bs4 import BeautifulSoup

URL = "https://dolarhoy.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

TIMEOUT = 10

# Tabla "Cotizaciones" (fuente principal, sin sponsors)
MAPEO_TABLA = {
    "dolar libre": "blue",
    "dolar mayorista": "mayorista",
    "dolar mep": "bolsa",
    "contado con liqui": "contadoconliqui",
}

# Tarjetas compactas (solo para tipos que no estan en la tabla de arriba)
MAPEO_CARDS = {
    "dolar oficial": "oficial",
    "dolar tarjeta": "tarjeta",
}


def obtener_todos() -> dict:
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"DolarHoy: error de conexion: {e}")
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    resultado = {}

    # 1) Tabla "Cotizaciones"
    for item in soup.select("div.cotizaciones_more div.entidad div.tile.is-child"):
        title_el = item.select_one(".title")
        compra_el = item.select_one(".compra")
        venta_el = item.select_one(".venta")
        if not (title_el and compra_el and venta_el):
            continue

        tipo = MAPEO_TABLA.get(_normalizar(title_el.get_text(strip=True)))
        if not tipo:
            continue

        compra = _parse_float(compra_el.get_text(strip=True))
        venta = _parse_float(venta_el.get_text(strip=True))
        if compra is not None and venta is not None:
            resultado[tipo] = {"compra": compra, "venta": venta}

    # 2) Tarjetas compactas, solo para tipos que faltan (oficial, tarjeta)
    for card in soup.select("div.tile.is-child"):
        title_el = card.select_one(".title .titleText")
        if not title_el:
            continue

        tipo = MAPEO_CARDS.get(_normalizar(title_el.get_text(strip=True)))
        if not tipo or tipo in resultado:
            continue

        venta_el = card.select_one(".venta .val")
        compra_el = card.select_one(".compra .val")
        venta = _parse_float(venta_el.get_text(strip=True)) if venta_el else None
        compra = _parse_float(compra_el.get_text(strip=True)) if compra_el else None

        if venta is not None:
            resultado[tipo] = {"compra": compra, "venta": venta}

    if not resultado:
        print("DolarHoy: no se pudo extraer ningun tipo - revisar selectores")

    return resultado


def _normalizar(texto: str) -> str:
    """'Dólar Libre' -> 'dolar libre' (sin tildes, minuscula)."""
    texto = texto.lower().strip()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        texto = texto.replace(a, b)
    return texto


def _parse_float(valor: str) -> float | None:
    """
    Limpia '$1.515,00' o '1515,00' -> 1515.0
    Formato AR: punto = miles, coma = decimal.
    """
    limpio = re.sub(r"[^\d,.\-]", "", valor)
    try:
        return float(limpio.replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return None
