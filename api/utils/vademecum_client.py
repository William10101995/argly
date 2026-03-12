import requests

VADEMECUM_URL = "https://cnpm.msal.gov.ar/api/vademecum"


def buscar_medicamentos(nombre):
    response = requests.post(
        VADEMECUM_URL,
        headers={"Content-Type": "application/json"},
        json={"searchdata": nombre},
        timeout=10,
    )

    response.raise_for_status()

    return response.json()
