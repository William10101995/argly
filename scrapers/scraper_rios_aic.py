"""
Scraper: Ríos Limay, Neuquén y Negro (Cuenca del Comahue)
Fuente: Autoridad Interjurisdiccional de Cuencas (AIC)
        https://www.aic.gob.ar/sitio/estaciones-detalle?a=<id>&z=<z>

Notas de implementación (confirmadas depurando con datos reales, no adivinadas):

  - El parámetro `z` de la URL de detalle es OBLIGATORIO. Sin él, la AIC
    responde 302 y redirige al listado (/sitio/estaciones). El `z` de cada
    estación se tomó del listado público y queda hardcodeado en ESTACIONES
    (no hay forma pública de derivarlo dinámicamente). Si en el futuro una
    estación empieza a redirigir (302), lo más probable es que ese `z`
    haya cambiado — hay que volver a sacarlo de /sitio/estaciones.

  - El sitio usa un TabContainer de AjaxControlToolkit (ASP.NET). Las
    "tabs" que se ven en el listado (Altura Río/Lago, Caudal Medio
    Diario, etc.) son solo selectores de gráfico, NO la fuente de los
    valores. Los valores reales están en
    <table><tbody id="..._grilla"><tr><td>Etiqueta</td><td>Valor</td></tr>.

  - Cada estación puede tener su propia nomenclatura de sensor (ej.
    "Altura Río/Lago" vs "Altura Hidrometrica del rio" vs "altura
    hidrometro medida con sensor (presión o flotante)" para lo que
    conceptualmente es lo mismo: altura del río). Por eso NO se descarta
    ninguna fila que no matchee un campo conocido: se guarda igual en
    `mediciones_originales` tal cual la reporta la AIC, y además se
    normaliza a un campo estándar (`altura_rio_m`, `caudal_m3s`, etc.)
    cuando la etiqueta es una ya mapeada en CAMPOS. Si aparece una
    etiqueta nueva no mapeada, se loguea con "ℹ" (no es un error, es
    información para ir ampliando CAMPOS con el tiempo).

  - Una estación puede estar "Fuera de Línea" (offline). Eso NO es un
    error del scraper: se guarda igual, con estado_estacion="fuera_de_linea"
    y los campos numéricos en SIN_DATO.

  - No todas las estaciones miden lo mismo. Los campos estándar que una
    estación no reporta quedan como el string SIN_DATO en vez de
    omitirse, para que la respuesta de la API tenga siempre las mismas
    claves. OJO al consumir la API: cada campo puede venir como número
    o como ese string — no asumir siempre `float`.

Mapeo estación -> río:
La AIC no publica a qué río pertenece cada estación. El diccionario
ESTACIONES se construyó cruzando la página oficial "Caudales Programados"
(nombra represas sobre el Limay y sobre el Neuquén), "Embalses", y fuentes
geográficas verificables (Wikipedia, prensa local). Cada estación tiene
"confianza" ("alta" | "media"). Estaciones sobre tributarios donde la
atribución era dudosa (Varvarco, Covunco, Traful, Zapala Met, etc.) se
dejaron AFUERA a propósito. Antes de sumar una estación nueva, confirmá
con la AIC: https://www.aic.gob.ar/sitio/contacto.aspx
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from utils import save_dataset_json

BASE_URL = "https://www.aic.gob.ar/sitio/estaciones-detalle"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
}
TIMEOUT = 15
SIN_DATO = "sin dato registrado"

ESTACIONES = {
    "limay": [
        {"id": 24, "z": 1237148288, "nombre": "Nahuel Huapi", "tipo": "lago_origen", "confianza": "alta"},
        {"id": 27, "z": 1070724129, "nombre": "Villa Llanquín", "tipo": "rio", "confianza": "alta"},
        {"id": 32, "z": 574057215, "nombre": "Corralito", "tipo": "rio", "confianza": "media"},
        {"id": 26, "z": 1702278334, "nombre": "Pichi Picún Leufú", "tipo": "dique", "confianza": "alta"},
        {"id": 25, "z": 855522465, "nombre": "Las Perlas", "tipo": "rio", "confianza": "alta"},
        {"id": 107, "z": 1556111886, "nombre": "Paseo de la Costa (Neuquén Capital)", "tipo": "rio", "confianza": "alta"},
    ],
    "neuquen": [
        {"id": 33, "z": 2096022048, "nombre": "Chos Malal", "tipo": "rio", "confianza": "alta"},
        {"id": 34, "z": 467605829, "nombre": "Andacollo (Puente)", "tipo": "rio", "confianza": "media"},
        {"id": 35, "z": 85980006, "nombre": "Rahueco", "tipo": "rio", "confianza": "media"},
        {"id": 36, "z": 932735875, "nombre": "Balsa Huitrín", "tipo": "rio", "confianza": "media"},
        {"id": 37, "z": 1840266588, "nombre": "Compensador El Chañar", "tipo": "dique", "confianza": "alta"},
        {"id": 126, "z": 1475110325, "nombre": "Portezuelo Grande", "tipo": "dique", "confianza": "alta"},
        {"id": 41, "z": 494871533, "nombre": "Cipolletti Toma", "tipo": "toma_riego", "confianza": "media"},
        {"id": 109, "z": 909660344, "nombre": "Canal Principal", "tipo": "canal_riego", "confianza": "media"},
    ],
    "negro": [
        {"id": 22, "z": 1343599674, "nombre": "Allen", "tipo": "rio", "confianza": "alta"},
        {"id": 21, "z": 496843805, "nombre": "Choele Choel (Bocatoma)", "tipo": "rio", "confianza": "alta"},
    ],
}

# Etiqueta tal como aparece en la grilla -> campo normalizado.
# Se van sumando sinónimos a medida que aparecen: cada estación de la AIC
# parece tener nomenclatura propia de sensor, no una taxonomía única.
CAMPOS = {
    "Altura Río/Lago": "altura_rio_m",
    "Altura Hidrometrica del rio": "altura_rio_m",
    "altura hidrometro medida con sensor (presión o flotante)": "altura_rio_m",
    "Caudal Medio Diario": "caudal_m3s",
    "Caudal Calculado curvaHQ": "caudal_m3s",
    "Humedad Relativa Media Diaria": "humedad_relativa_pct",
    "Precipitación Diaria": "precipitacion_mm",
    "Temperatura Mínima Diaria": "temperatura_minima_c",
    "Temperatura Máxima Diaria": "temperatura_maxima_c",
    "Temperatura media intervalo": "temperatura_media_c",
}

CAMPOS_ESTANDAR = {
    "altura_rio_m",
    "caudal_m3s",
    "humedad_relativa_pct",
    "precipitacion_mm",
    "temperatura_minima_c",
    "temperatura_maxima_c",
    "temperatura_media_c",
}


def _parse_numero(valor_raw: str):
    """'2.64 m' -> 2.64 | '210 m3/s' -> 210.0 | '----' -> None | '' -> None"""
    match = re.search(r"-?\d+(?:[.,]\d+)?", valor_raw or "")
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def obtener_estacion(estacion: dict) -> dict | None:
    url = f"{BASE_URL}?a={estacion['id']}&z={estacion['z']}"
    try:
        resp = requests.get(
            url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=False
        )
    except Exception as e:
        print(f"⚠ Estación {estacion['id']} ({estacion['nombre']}): error de red: {e}")
        return None

    if resp.status_code == 302:
        print(
            f"⚠ Estación {estacion['id']} ({estacion['nombre']}): redirigió a "
            f"{resp.headers.get('Location')} (z inválido o vencido, hay que "
            "revisar el listado /sitio/estaciones y actualizar ESTACIONES)"
        )
        return None

    if resp.status_code != 200:
        print(f"⚠ Estación {estacion['id']} ({estacion['nombre']}): HTTP {resp.status_code}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    valores = {campo: SIN_DATO for campo in CAMPOS_ESTANDAR}
    mediciones_originales = []  # todo lo que reportó la estación, sin filtrar
    filas_con_dato = 0

    for row in soup.find_all("tr"):
        cols = row.find_all(["td", "th"])
        if len(cols) != 2:
            continue

        etiqueta = cols[0].get_text(strip=True)
        valor_texto = cols[1].get_text(strip=True)

        if not etiqueta or etiqueta.startswith("("):
            # filas tipo "(última actualización...)" o "(Estación Fuera de Línea)"
            continue

        filas_con_dato += 1
        numero = _parse_numero(valor_texto)

        mediciones_originales.append(
            {
                "etiqueta_original": etiqueta,
                "valor": numero if numero is not None else (valor_texto or SIN_DATO),
            }
        )

        campo = CAMPOS.get(etiqueta)
        if campo:
            valores[campo] = numero if numero is not None else SIN_DATO

    texto_completo = soup.get_text(" ", strip=True)
    fuera_de_linea = (
        "Fuera de Línea" in texto_completo or "Fuera de Linea" in texto_completo
    )

    match_fecha = re.search(
        r"última actualización:\s*(\d{2}/\d{2}/\d{4})", texto_completo
    )
    fecha_actualizacion = match_fecha.group(1) if match_fecha else SIN_DATO

    if filas_con_dato == 0 and not fuera_de_linea:
        print(
            f"⚠ Estación {estacion['id']} ({estacion['nombre']}): "
            "200 OK pero no encontré ninguna fila de datos (¿cambió el HTML?)"
        )
        return None

    etiquetas_no_reconocidas = [
        m["etiqueta_original"]
        for m in mediciones_originales
        if CAMPOS.get(m["etiqueta_original"]) is None
    ]
    if etiquetas_no_reconocidas:
        print(
            f"ℹ Estación {estacion['id']} ({estacion['nombre']}): "
            f"etiquetas sin normalizar (revisar CAMPOS): {etiquetas_no_reconocidas}"
        )

    return {
        **valores,
        "mediciones_originales": mediciones_originales,
        "fecha_actualizacion": fecha_actualizacion,
        "estado_estacion": "fuera_de_linea" if fuera_de_linea else "operativa",
    }


def obtener_rios_aic() -> dict:
    resultado = {
        "fuente": "AIC - Autoridad Interjurisdiccional de Cuencas",
        "url_fuente": "https://www.aic.gob.ar/sitio/estaciones",
        "nota_metodologica": (
            "La AIC no publica el mapeo estación->río. Fue reconstruido "
            "manualmente cruzando las páginas oficiales de Embalses y "
            "Caudales Programados de la AIC más fuentes geográficas "
            "públicas. Ver el campo 'confianza' de cada estación. Los "
            f"campos sin medición figuran como '{SIN_DATO}'. Cada "
            "estación conserva además 'mediciones_originales' con las "
            "etiquetas y valores tal cual los reporta la AIC, por si su "
            "nomenclatura de sensor no coincide con los campos estándar."
        ),
        "rios": {},
    }

    for rio, estaciones in ESTACIONES.items():
        lista_rio = []
        for est in estaciones:
            datos = obtener_estacion(est)
            time.sleep(0.5)  # cortesía al servidor
            if datos is None:
                continue
            lista_rio.append(
                {
                    "nombre": est["nombre"],
                    "tipo": est["tipo"],
                    "confianza": est["confianza"],
                    "estacion_id": est["id"],
                    **datos,
                }
            )
        resultado["rios"][rio] = lista_rio

    return resultado


if __name__ == "__main__":
    data = obtener_rios_aic()
    total = sum(len(v) for v in data["rios"].values())
    if total == 0:
        print("❌ No se obtuvo ningún dato de ninguna estación, no se guarda")
        exit(1)
    save_dataset_json(dataset="rios_comahue", data=data)
    print(f"✔ Rios Comahue actualizado: {total} estaciones con datos")