from curl_cffi import requests

BCRA_ENDPOINT = "https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas/Historicas/"


def get_bcra_data(cuil: str):
    url = f"{BCRA_ENDPOINT}{cuil}"

    try:
        response = requests.get(url, impersonate="chrome", timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise Exception("El BCRA no respondió a tiempo")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Error de conexión con el BCRA: {e}")
    except requests.exceptions.HTTPError:
        raise Exception(f"El BCRA devolvió error HTTP {response.status_code}")

    data = response.json()

    if "results" not in data:
        raise Exception("Respuesta inválida del BCRA")

    return data["results"]
