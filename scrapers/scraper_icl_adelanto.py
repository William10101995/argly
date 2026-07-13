import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from utils import save_dataset_json

BCRA_V4_URL = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/40"
TIMEOUT = 15
LATEST_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "icl_adelanto" / "latest.json"
)


def obtener_icl_adelanto():
    hoy = datetime.now().date()
    desde = hoy.strftime("%Y-%m-%d")
    hasta = (hoy + timedelta(days=20)).strftime("%Y-%m-%d")

    try:
        resp = requests.get(
            BCRA_V4_URL,
            params={"Desde": desde, "Hasta": hasta},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error consultando BCRA v4.0: {e}")
        return None

    resultados = data.get("results", [])
    if not resultados:
        print("⚠ Respuesta sin resultados")
        return None

    detalle = resultados[0].get("detalle", [])

    futuros = [
        {"fecha": item["fecha"], "valor": item["valor"]}
        for item in detalle
        if datetime.strptime(item["fecha"], "%Y-%m-%d").date() > hoy
    ]

    futuros.sort(key=lambda x: x["fecha"])
    return futuros


def cargar_fechas_existentes() -> set[str]:
    if not LATEST_PATH.exists():
        return set()
    try:
        with open(LATEST_PATH, "r", encoding="utf-8") as f:
            actual = json.load(f)
        return {item["fecha"] for item in actual}
    except Exception:
        return set()


if __name__ == "__main__":
    nuevos = obtener_icl_adelanto()

    if not nuevos:
        print("ℹ Sin proyección disponible todavía, no se actualiza")
        exit(0)

    fechas_nuevas = {item["fecha"] for item in nuevos}
    fechas_existentes = cargar_fechas_existentes()

    if fechas_nuevas <= fechas_existentes:
        print("ℹ No hay fechas nuevas en la proyección, se omite el guardado")
        exit(0)

    save_dataset_json(dataset="icl_adelanto", data=nuevos)
    print(
        f"✔ ICL adelanto actualizado: {len(nuevos)} valores futuros "
        f"({nuevos[0]['fecha']} a {nuevos[-1]['fecha']})"
    )
