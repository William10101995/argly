import requests


BCRA_ENDPOINT = "https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas/Historicas/"


def get_bcra_data(cuil: str):

    url = f"{BCRA_ENDPOINT}{cuil}"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error consultando BCRA")

    data = response.json()

    if "results" not in data:
        raise Exception("Respuesta inválida del BCRA")

    return data["results"]
