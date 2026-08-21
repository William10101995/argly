from pathlib import Path
import json

DATA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "rios_comahue" / "latest.json"
)

RIOS_VALIDOS = {"limay", "neuquen", "negro"}


def _load() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError("No hay datos de ríos Comahue disponibles.")
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_rios_comahue(rio: str | None = None) -> dict:
    data = _load()

    if rio:
        rio = rio.lower()
        if rio not in RIOS_VALIDOS:
            raise ValueError(
                f"Río inválido. Válidos: {', '.join(sorted(RIOS_VALIDOS))}"
            )
        return {
            "fuente": data["fuente"],
            "url_fuente": data["url_fuente"],
            "nota_metodologica": data["nota_metodologica"],
            "rio": rio,
            "estaciones": data["rios"].get(rio, []),
        }

    return data