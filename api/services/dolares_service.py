import os
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "dolares"

TIPOS_VALIDOS = {
    "oficial",
    "blue",
    "bolsa",
    "contadoconliqui",
    "mayorista",
    "cripto",
    "tarjeta",
}

S3_BUCKET = os.environ.get("S3_DATA_BUCKET")
S3_KEY_LATEST = "dolares/latest.json"
# El bucket argly-data vive en us-east-1 (confirmado con aws s3api
# get-bucket-location), NO en sa-east-1 donde corre el Lambda. Se fija
# explicito para evitar que boto3 haga un redirect extra en cada
# request al asumir la region del Lambda.
S3_REGION = os.environ.get("S3_DATA_REGION", "us-east-1")
_CACHE_TTL_SECONDS = 300  # 5 min, menor al intervalo de scraping (20 min)

_cache = {"data": None, "fetched_at": 0.0}


def _load_latest_from_s3() -> dict:
    """
    Lee latest.json directo de S3. Cualquier fallo (bucket inexistente,
    permisos, timeout, red, JSON corrupto, lo que sea) se propaga como
    ConnectionError para que la ruta lo traduzca a 503 -- sin fallback
    silencioso en produccion, tal como se definio explicitamente para
    este dataset. Se captura Exception de forma amplia a proposito: un
    503 claro es preferible a que un error inesperado de boto3/red se
    cuele sin manejar y termine como un 500 generico de Flask.
    """
    try:
        import boto3

        s3 = boto3.client("s3", region_name=S3_REGION)
        resp = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY_LATEST)
        body = resp["Body"].read().decode("utf-8")
        data = json.loads(body)
        return data[0] if isinstance(data, list) and data else {}
    except Exception as e:
        raise ConnectionError(f"No se pudo leer dolares desde S3: {e}") from e


def _load_latest_from_disco() -> dict:
    """Solo para desarrollo local, cuando S3_DATA_BUCKET no esta configurado."""
    path = BASE_DATA_PATH / "latest.json"
    if not path.exists():
        raise FileNotFoundError("No hay datos de dolares disponibles en disco local.")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data[0] if isinstance(data, list) and data else {}


def _load_latest() -> dict:
    """
    En produccion (S3_DATA_BUCKET seteado): SIEMPRE lee de S3. Si S3 falla,
    propaga ConnectionError -- la ruta responde 503, sin devolver datos
    potencialmente viejos horneados en la imagen. Decision explicita de
    William: preferible fallar claro a servir datos desactualizados sin
    avisar.

    En desarrollo local (sin S3_DATA_BUCKET): lee de disco, comportamiento
    identico al resto de los datasets del proyecto.
    """
    now = time.time()
    if _cache["data"] is not None and (now - _cache["fetched_at"]) < _CACHE_TTL_SECONDS:
        return _cache["data"]

    if S3_BUCKET:
        data = _load_latest_from_s3()  # deja propagar ConnectionError
    else:
        data = _load_latest_from_disco()

    _cache["data"] = data
    _cache["fetched_at"] = now
    return data


def get_dolares() -> dict:
    """
    Devuelve todas las cotizaciones vigentes, sin el bloque interno _meta
    de fuentes consultadas/fallidas (ese detalle queda para uso interno /
    debugging, no para el consumidor publico).
    """
    data = _load_latest()
    return {tipo: valores for tipo, valores in data.items() if tipo != "_meta"}


def get_dolar_por_tipo(tipo: str) -> dict | None:
    tipo = tipo.lower()
    data = get_dolares()
    return data.get(tipo)


def get_dolares_history() -> list[dict]:
    """
    Recorre los archivos versionados por dia (excepto latest.json) y arma
    una serie historica. Sigue leyendo de disco local -- el historico no
    esta migrado a S3 en esta primera etapa (alcance acordado: solo
    latest.json va a S3 por ahora).
    """
    if not BASE_DATA_PATH.exists():
        return []

    archivos = [
        f
        for f in BASE_DATA_PATH.iterdir()
        if f.suffix == ".json" and f.name != "latest.json"
    ]

    resultado = []

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                continue

            item = data[0]
            fecha = archivo.stem  # YYYY-MM-DD

            resultado.append(
                {
                    "fecha": fecha,
                    "cotizaciones": {
                        tipo: valores
                        for tipo, valores in item.items()
                        if tipo != "_meta"
                    },
                }
            )
        except Exception:
            continue

    resultado.sort(key=lambda x: x["fecha"])
    return resultado


def get_dolares_range(desde: str, hasta: str) -> list[dict]:
    historico = get_dolares_history()

    try:
        d_desde = datetime.strptime(desde, "%Y-%m-%d").date()
        d_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        return []

    resultado = []
    for item in historico:
        fecha = datetime.strptime(item["fecha"], "%Y-%m-%d").date()
        if d_desde <= fecha <= d_hasta:
            resultado.append(item)

    return resultado
