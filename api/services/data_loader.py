import json
from pathlib import Path
import unicodedata
from datetime import datetime


BASE_DATA_PATH = Path(__file__).resolve().parents[2] / "data"


def _load_latest(category: str):
    path = BASE_DATA_PATH / category / "latest.json"
    if not path.exists():
        raise FileNotFoundError(f"No existe latest.json para {category}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------- COMBUSTIBLES --------


def get_combustibles():
    return _load_latest("combustibles")


def get_combustibles_by_provincia(provincia: str):
    provincia = provincia.lower()
    return [
        c for c in get_combustibles() if c.get("provincia", "").lower() == provincia
    ]


def get_combustibles_by_empresa(empresa: str):
    empresa = empresa.lower()
    return [c for c in get_combustibles() if c.get("empresa", "").lower() == empresa]


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("-", " ")


def get_promedio_combustible(provincia: str, combustible: str):
    provincia_norm = _normalize(provincia)
    combustible_norm = _normalize(combustible)

    precios = []

    for item in get_combustibles():
        if _normalize(item.get("provincia", "")) != provincia_norm:
            continue

        if _normalize(item.get("combustible", "")) != combustible_norm:
            continue

        valores = item.get("precios", {})
        for v in valores.values():
            if isinstance(v, (int, float)):
                precios.append(v)

    if not precios:
        return None

    return round(sum(precios) / len(precios), 2)


# -------- ICL --------


def get_icl():
    data = _load_latest("icl")
    if not data:
        return None
    item = data[0]
    return {"fecha": item.get("fecha"), "valor": item.get("valor")}


def get_icl_history():
    icl_path = BASE_DATA_PATH / "icl"

    if not icl_path.exists():
        return []

    files = [
        f for f in icl_path.iterdir() if f.suffix == ".json" and f.name != "latest.json"
    ]

    result = []

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                continue

            item = data[0]
            result.append(
                {"fecha": item.get("fecha") or file.stem, "valor": item.get("valor")}
            )

        except Exception:
            continue

    # orden cronológico
    result.sort(key=lambda x: datetime.strptime(x["fecha"], "%d/%m/%Y"))
    return result


def get_icl_range(desde: str, hasta: str):
    historico = get_icl_history()

    try:
        d_desde = datetime.strptime(desde, "%Y-%m-%d").date()
        d_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        return []

    result = []

    for item in historico:
        fecha = datetime.strptime(item["fecha"], "%d/%m/%Y").date()

        if d_desde <= fecha <= d_hasta:
            result.append(item)

    return result


# -------- IPC --------


def get_ipc():
    data = _load_latest("ipc")
    return data[0] if data else None


def get_ipc_history():
    ipc_path = BASE_DATA_PATH / "ipc"

    if not ipc_path.exists():
        return []

    files = [
        f for f in ipc_path.iterdir() if f.suffix == ".json" and f.name != "latest.json"
    ]

    result = []

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                continue

            item = data[0]

            indice = item.get("indice_ipc")
            mes = item.get("mes")
            anio = item.get("anio")
            nombre_mes = item.get("nombre_mes")

            if indice is None or mes is None:
                continue

            result.append(
                {
                    "mes": mes,
                    "anio": anio,
                    "nombre_mes": nombre_mes,
                    "valor": indice,
                }
            )

        except Exception:
            continue

    # ordenar por anio y mes
    result.sort(key=lambda x: (x["anio"], x["mes"]))
    return result


def get_ipc_range(desde: str, hasta: str):
    historico = get_ipc_history()

    try:
        desde_dt = datetime.strptime(desde, "%Y-%m")
        hasta_dt = datetime.strptime(hasta, "%Y-%m")
    except ValueError:
        return []

    result = []

    for item in historico:
        anio = item.get("anio")
        mes = item.get("mes")

        if not anio or not mes:
            continue

        fecha_ipc = datetime(anio, mes, 1)

        if desde_dt <= fecha_ipc <= hasta_dt:
            result.append(item)

    # ya viene ordenado, pero por las dudas
    result.sort(key=lambda x: (x["anio"], x["mes"]))
    return result


# -------- UVI --------


def get_uvi():
    data = _load_latest("uvi")
    if not data:
        return None
    item = data[0]
    return {"fecha": item.get("fecha"), "valor": item.get("valor")}


def get_uvi_history():
    uvi_path = BASE_DATA_PATH / "uvi"

    if not uvi_path.exists():
        return []

    files = [
        f for f in uvi_path.iterdir() if f.suffix == ".json" and f.name != "latest.json"
    ]

    result = []

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                continue

            item = data[0]
            result.append(
                {
                    "fecha": item.get("fecha") or file.stem,
                    "valor": item.get("valor"),
                }
            )

        except Exception:
            continue

    # orden cronológico
    result.sort(key=lambda x: datetime.strptime(x["fecha"], "%d/%m/%Y"))
    return result


def get_uvi_range(desde: str, hasta: str):
    historico = get_uvi_history()

    try:
        d_desde = datetime.strptime(desde, "%Y-%m-%d").date()
        d_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        return []

    result = []

    for item in historico:
        fecha = datetime.strptime(item["fecha"], "%d/%m/%Y").date()

        if d_desde <= fecha <= d_hasta:
            result.append(item)

    return result


# -------- UVA --------


def get_uva():
    data = _load_latest("uva")
    if not data:
        return None
    item = data[0]
    return {"fecha": item.get("fecha"), "valor": item.get("valor")}


def get_uva_history():
    uva_path = BASE_DATA_PATH / "uva"

    if not uva_path.exists():
        return []

    files = [
        f for f in uva_path.iterdir() if f.suffix == ".json" and f.name != "latest.json"
    ]

    result = []

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                continue

            item = data[0]
            result.append(
                {
                    "fecha": item.get("fecha") or file.stem,
                    "valor": item.get("valor"),
                }
            )

        except Exception:
            continue

    result.sort(key=lambda x: datetime.strptime(x["fecha"], "%d/%m/%Y"))
    return result


def get_uva_range(desde: str, hasta: str):
    historico = get_uva_history()

    try:
        d_desde = datetime.strptime(desde, "%Y-%m-%d").date()
        d_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        return []

    result = []

    for item in historico:
        fecha = datetime.strptime(item["fecha"], "%d/%m/%Y").date()
        if d_desde <= fecha <= d_hasta:
            result.append(item)

    return result


# -------- RIOS --------


def get_rios():
    """
    Devuelve el snapshot completo de ríos
    """
    data = _load_latest("rios")
    if not data:
        return None
    return data[0]


def get_rio_by_nombre(nombre: str):
    data = get_rios()
    if not data:
        return None

    nombre_norm = _normalize(nombre)

    for rio in data.get("rios", []):
        if _normalize(rio.get("nombre", "")) == nombre_norm:
            return rio

    return None
