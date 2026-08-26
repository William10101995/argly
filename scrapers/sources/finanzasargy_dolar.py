"""
Fuente: Finanzas Argy (finanzasargy.com)

Rol: AUDITORIA, no escritura. Esta fuente nunca pisa un dato del resultado
final - solo se usa para detectar y loguear divergencias grandes entre lo
que publican Ambito/DolarHoy/BNA y lo que publica un cuarto sitio
independiente.

CONFIRMADO (curl + grep, 2026-08-10): el sitio es una SPA hecha con Astro.
El HTML servido por el propio dominio (SSR) trae los datos embebidos en el
atributo `props` de <astro-island component-export="PanelGeneralClient">,
pero OJO: no es JSON plano. Astro serializa los props con un formato propio
(similar a "devalue"): cada valor viene envuelto como [tag, valor], donde
el tag indica el tipo:
    0 = objeto o primitivo tal cual
    1 = array (cada elemento tambien viene envuelto [tag, valor])
    2 = RegExp, 3 = Date, 4 = Map, 5 = Set, 6 = BigInt, 7 = URL, ...
Esto se confirmo leyendo el propio bootstrap JS que la pagina incluye
inline (la funcion `o=t=>{let[l,e]=t;return l in i?i[l](e):void 0}` es
literalmente el deserializador que el navegador ejecuta del lado cliente).
_deserializar() de abajo es el equivalente en Python de esa funcion,
limitado a los tags que nos importan (0 y 1 - no necesitamos RegExp/Date/
Map/Set/BigInt/URL para este caso).

Shape real ya deserializado (extracto):
    {
      "initialPanelData": {
        "panel": [
          {"titulo": "Dólar Blue", "venta": "1540", "compra": "1520", ...},
          {"titulo": "Dólar Oficial", "venta": "1520,49", "compra": "1469,22", ...},
          {"titulo": "Dólar Cripto", "venta": "1574.39", "compra": "1567.61", ...},
          ...
        ]
      }
    }

OJO con el formato numerico: la mayoria de los campos usan formato AR
(punto=miles, coma=decimal, ej "1520,49"), pero "Dolar Cripto" vino con
formato con punto decimal directo ("1574.39"). _parse_numero() maneja
ambos casos.

Probado end-to-end contra un fragmento real del HTML pegado por William
(ver conversacion) - el deserializador extrae correctamente los 7 tipos
publicados: Blue, Oficial, Tarjeta, Futuro, Cripto, MEP, CCL, Mayorista.

El sitio ademas expone su propio backend en AWS
(x2ozxj31bl.execute-api.sa-east-1.amazonaws.com, visible en el
<link rel="preconnect">), pero no se investigo esa API directamente:
parsear el HTML SSR ya es suficiente y mas simple.
"""

import html as html_lib
import json
import re
import requests

URL = "https://finanzasargy.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

TIMEOUT = 8

MAPEO_TITULOS = {
    "dolar blue": "blue",
    "dolar oficial": "oficial",
    "dolar tarjeta": "tarjeta",
    "dolar cripto": "cripto",
    "dolar mep": "bolsa",
    "dolar ccl": "contadoconliqui",
    "dolar mayorista": "mayorista",
}

# Busca el astro-island de PanelGeneralClient y captura su atributo props
_PROPS_RE = re.compile(
    r'component-export="PanelGeneralClient"[^>]*?\sprops="([^"]*)"',
    re.DOTALL,
)


def _deserializar(node):
    """
    Equivalente Python del deserializador de Astro (formato tipo 'devalue').
    node es siempre [tag, valor]. Solo soporta los tags que aparecen en
    este payload (0=objeto/primitivo, 1=array); cualquier otro tag se
    devuelve sin procesar (no los necesitamos para dolares).
    """
    if not (isinstance(node, list) and len(node) == 2):
        return node

    tag, valor = node

    if tag == 0:
        if isinstance(valor, dict):
            return {k: _deserializar(v) for k, v in valor.items()}
        return valor  # primitivo: string, numero, bool, None

    if tag == 1:
        if isinstance(valor, list):
            return [_deserializar(v) for v in valor]
        return valor

    # Tags no soportados (RegExp/Date/Map/Set/BigInt/URL/etc) - no aplica aca
    return valor


def obtener_todos() -> dict:
    """
    Devuelve {tipo: {compra, venta}} extraido del panel embebido en el SSR.
    Ante cualquier fallo devuelve {} (no bloqueante para el orquestador).
    """
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        html_text = resp.text
    except Exception as e:
        print(f"Finanzas Argy no disponible (no bloqueante): {e}")
        return {}

    return _parsear_html(html_text)


def _parsear_html(html_text: str) -> dict:
    match = _PROPS_RE.search(html_text)
    if not match:
        print("Finanzas Argy: no se encontro el bloque PanelGeneralClient "
              "- el sitio pudo haber cambiado de estructura")
        return {}

    try:
        props_json = html_lib.unescape(match.group(1))
        raw = json.loads(props_json)
        panel_data = _deserializar(raw.get("initialPanelData"))
        panel = panel_data.get("panel", []) if isinstance(panel_data, dict) else []
    except Exception as e:
        print(f"Finanzas Argy: error parseando el JSON embebido: {e}")
        return {}

    resultado = {}
    for item in panel:
        if not isinstance(item, dict):
            continue

        titulo = _normalizar(item.get("titulo", ""))
        tipo = MAPEO_TITULOS.get(titulo)
        if not tipo:
            continue

        venta = _parse_numero(item.get("venta"))
        compra = _parse_numero(item.get("compra"))

        if venta is not None:
            resultado[tipo] = {"compra": compra, "venta": venta}

    return resultado


def _normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        texto = texto.replace(a, b)
    return texto


def _parse_numero(valor) -> float | None:
    """
    Maneja los dos formatos vistos en el JSON real:
      "1520,49" (AR: coma decimal)      -> 1520.49
      "1574.39" (punto decimal directo) -> 1574.39
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto or texto == "-":
        return None
    try:
        if "," in texto:
            return float(texto.replace(".", "").replace(",", "."))
        return float(texto)
    except ValueError:
        return None
