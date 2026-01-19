import json
from pathlib import Path
import unicodedata

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
    result.sort(key=lambda x: x["fecha"])
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
            nombre_mes = item.get("nombre_mes")

            if indice is None or mes is None:
                continue

            result.append(
                {
                    "mes": mes,
                    "nombre_mes": nombre_mes,
                    "valor": indice,
                }
            )

        except Exception:
            continue

    # ordenar por mes (opcional, útil si el histórico es anual)
    result.sort(key=lambda x: x["mes"])
    return result
