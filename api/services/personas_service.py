import json
import os

DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "personas_desaparecidas"
)


def _load_latest() -> dict:
    path = os.path.join(DATA_DIR, "latest.json")
    if not os.path.exists(path):
        raise FileNotFoundError("No hay datos disponibles. Ejecutá el scraper primero.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_resumen() -> dict:
    """
    Devuelve el resumen estadístico: total y cantidad por año.
    """
    data = _load_latest()
    return {
        "fuente": data["fuente"],
        "url_fuente": data["url_fuente"],
        "total": data["total"],
        "resumen_por_anio": data["resumen_por_anio"],
    }


def get_all(anio: int | None = None) -> dict:
    """
    Devuelve la lista completa de personas desaparecidas.
    Si se provee `anio`, filtra solo ese año.
    """
    data = _load_latest()

    if anio is not None:
        key = str(anio)
        personas = data["por_anio"].get(key, [])
        return {
            "fuente": data["fuente"],
            "url_fuente": data["url_fuente"],
            "anio": anio,
            "total": len(personas),
            "personas": personas,
        }

    # Sin filtro: devolver todo aplanado con el año incluido
    todas = []
    for anio_key, lista in data["por_anio"].items():
        for p in lista:
            todas.append({**p, "anio_desaparicion": int(anio_key)})
    todas.extend({**p, "anio_desaparicion": None} for p in data.get("sin_fecha", []))

    return {
        "fuente": data["fuente"],
        "url_fuente": data["url_fuente"],
        "total": data["total"],
        "personas": todas,
    }


def get_por_anio() -> dict:
    """
    Devuelve la lista agrupada por año (útil para gráficos).
    """
    data = _load_latest()
    return {
        "fuente": data["fuente"],
        "url_fuente": data["url_fuente"],
        "total": data["total"],
        "resumen_por_anio": data["resumen_por_anio"],
        "por_anio": data["por_anio"],
    }
