# api/services/diputados_service.py
import json
import os
import unicodedata

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "diputados", "diputados.json"
)


def normalizar(texto):
    texto = (
        unicodedata.normalize("NFD", texto)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
    )
    return " ".join(texto.split())


def get_diputados(distrito=None, bloque=None):
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("No hay datos de diputados disponibles.")

    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    diputados = data["datos"]

    if distrito:
        distrito_normalizado = normalizar(distrito.replace("-", " "))
        diputados = [
            d for d in diputados if normalizar(d["distrito"]) == distrito_normalizado
        ]

    if bloque:
        bloque_normalizado = normalizar(bloque.replace("-", " "))
        diputados = [
            d
            for d in diputados
            if normalizar(d["bloque"].replace("-", " ")) == bloque_normalizado
        ]

    return {"total": len(diputados), "fuente": data["fuente"], "datos": diputados}
