"""
Fuente: Banco de la Nacion Argentina (bna.com.ar/Personas)

Es la fuente AUTORITATIVA para el tipo "oficial" (no un tercero reportando
sobre el BNA, sino el BNA mismo) - pisa el dato de Ambito para ese tipo
especifico, siguiendo el principio ya aplicado con BCRA v4.0 en ICL/UVA/CER
(fuente oficial > scraping de terceros cuando esta disponible).

CONFIRMADO (curl + grep, 2026-08-10): la cotizacion SI esta en el HTML
crudo, no requiere JS. Estructura real:

    <div class="tab-pane fade in active" id="billetes">
      <table class="table cotizacion">
        <tbody>
          <tr>
          <td class="tit">Dolar U.S.A</td>
          <td>1470,00</td>   <- compra
          <td>1520,00</td>   <- venta
          </tr>
        </tbody>
      </table>

Hay dos tablas en la pagina: #billetes (cambio fisico/billete, la que
todo el mundo llama "dolar BNA") y #divisas (transferencia). Usamos
#billetes porque es la cotizacion de referencia habitual.

El sitio tambien expone (via AJAX, no usado aca):
  /Cotizador/MonedasHistorico
  /Cotizador/HistoricoPrincipales
Quedan documentados por si en el futuro se quiere historicos oficiales
del BNA en vez de reconstruirlos con los snapshots diarios propios.
"""

import requests
from bs4 import BeautifulSoup

URL = "https://www.bna.com.ar/Personas"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

TIMEOUT = 10


def obtener_oficial() -> dict | None:
    """
    Devuelve {"compra": float, "venta": float} del dolar oficial
    billete del BNA (tabla #billetes), o None si no se pudo obtener/parsear.
    """
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"BNA: error de conexion: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    tabla = soup.select_one("#billetes table.cotizacion tbody")
    if not tabla:
        print("BNA: no se encontro la tabla #billetes - la pagina pudo "
              "haber cambiado de estructura")
        return None

    for fila in tabla.find_all("tr"):
        celdas = fila.find_all("td")
        if len(celdas) < 3:
            continue

        nombre = celdas[0].get_text(strip=True).lower()
        if "dolar" not in nombre and "dólar" not in nombre:
            continue

        compra = _parse_float(celdas[1].get_text(strip=True))
        venta = _parse_float(celdas[2].get_text(strip=True))

        if compra is None or venta is None:
            print("BNA: fila de dolar encontrada pero no se pudo parsear "
                  "compra/venta")
            return None

        return {"compra": compra, "venta": venta}

    print("BNA: tabla #billetes encontrada pero sin fila 'Dolar U.S.A'")
    return None


def _parse_float(valor: str) -> float | None:
    try:
        return float(valor.replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return None
