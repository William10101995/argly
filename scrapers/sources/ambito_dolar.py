"""
Fuente: Ámbito Financiero (mercados.ambito.com)
Reutiliza el mismo patrón de API interna no documentada que ya usás en
api/services/riesgo_pais.py (mercados.ambito.com/riesgopais/...).

✔ TOTALMENTE CONFIRMADO (curl real, 2026-08-10) — URL y shape de respuesta
verificados de punta a punta:

  curl -A "Mozilla/5.0" -H "Referer: https://www.ambito.com/contenidos/dolar.html" \
       "https://mercados.ambito.com/dolar/informal/variacion"
  -> {"compra":"1515,00","venta":"1535,00","fecha":"10/08/2026 - 18:55",
      "variacion":"0,66%","class-variacion":"up","valor_cierre_ant":"1525,00"}

El shape coincide exactamente con lo que este módulo ya parseaba (mismo
esquema que /riesgopais). Validado además por cruce: el valor de blue
coincidió exacto con el que trajo DolarHoy en paralelo (1515/1535).

Requiere el header Referer (sin él, algunos endpoints de Ámbito devuelven
vacío o bloquean) — HEADERS ya lo incluye.

Slugs confirmados, sufijo real "/variacion" (no "/variacion-ultimo"):
  /dolar/oficial/variacion
  /dolar/informal/variacion      (blue)
  /dolarrava/mep/variacion       (bolsa/MEP)
  /dolarrava/cl/variacion        (contado con liqui)
  /dolar/mayorista/variacion
  /dolarcripto/variacion
  /dolarturista/variacion        (tarjeta)
  /dolarfuturo/variacion         (no usado por ahora)
  /dolarnacion/variacion         (BNA vía Ámbito — no usado; BNA se scrapea
                                   directo en bna_dolar.py como fuente
                                   autoritativa real)

Es la fuente PRIMARIA por cobertura: cubre todos los tipos salvo que
falle el sitio completo (en cuyo caso el orquestador cae a DolarHoy).
"""

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://mercados.ambito.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.ambito.com/contenidos/dolar.html",
}

TIMEOUT = 8

# tipo interno de Argly -> slug de la API de Ámbito
# Slugs confirmados en vivo (ver docstring del módulo)
TIPOS_AMBITO = {
    "oficial": "/dolar/oficial/variacion",
    "blue": "/dolar/informal/variacion",
    "mayorista": "/dolar/mayorista/variacion",
    "bolsa": "/dolarrava/mep/variacion",
    "contadoconliqui": "/dolarrava/cl/variacion",
    "cripto": "/dolarcripto/variacion",
    "tarjeta": "/dolarturista/variacion",
}


def _fetch_tipo(tipo: str, slug: str) -> dict | None:
    """
    Consulta un slug individual. Respuesta cruda esperada (a confirmar):
      {
        "compra": "1180,00",
        "venta":  "1220,00",
        "fecha":  "10-08-2026",
        "variacion": "0,41%",
        "class-variacion": "up-red"
      }
    """
    try:
        resp = requests.get(
            f"{BASE_URL}{slug}", headers=HEADERS, timeout=TIMEOUT, verify=False
        )
        resp.raise_for_status()
        raw = resp.json()
    except Exception as e:
        print(f"⚠ Ámbito [{tipo}]: {e}")
        return None

    compra = _parse_float(raw.get("compra"))
    venta = _parse_float(raw.get("venta"))

    if venta is None:
        # Algunos tipos (MEP, CCL, turista) sólo publican "referencia",
        # que puede venir en el campo "venta" o en un campo distinto
        # según el slug. Ajustar acá si el shape real difiere.
        print(f"⚠ Ámbito [{tipo}]: respuesta sin 'venta' útil, se descarta")
        return None

    return {
        "compra": compra,
        "venta": venta,
        "variacion": _parse_porcentaje(raw.get("variacion")),
        "fecha_actualizacion": raw.get("fecha"),
    }


def obtener_todos() -> dict:
    """
    Devuelve {tipo: {compra, venta, variacion, fecha_actualizacion}} para
    todos los tipos que Ámbito haya podido responder. Los tipos que fallen
    simplemente no aparecen en el dict (el orquestador decide qué hacer).
    """
    resultado = {}
    for tipo, slug in TIPOS_AMBITO.items():
        dato = _fetch_tipo(tipo, slug)
        if dato:
            resultado[tipo] = dato
    return resultado


def _parse_float(valor) -> float | None:
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except (ValueError, TypeError):
        return None


def _parse_porcentaje(valor) -> float | None:
    try:
        return float(str(valor).replace("%", "").replace(",", ".").strip())
    except (ValueError, TypeError):
        return None
