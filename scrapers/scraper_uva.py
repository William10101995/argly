import requests
from bs4 import BeautifulSoup
import urllib3
from utils import save_dataset_json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def obtener_uva_actual():
    """
    Scrapea la web del BCRA y devuelve el valor actual de la UVA.
    """
    url = "https://www.bcra.gob.ar/estadisticas-indicadores/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        if not table:
            return None

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 3:
                descripcion = cols[0].get_text(strip=True)

                if (
                    "Unidad de Valor Adquisitivo" in descripcion
                    and "UVA" in descripcion
                ):
                    fecha = cols[1].get_text(strip=True)
                    valor_str = cols[2].get_text(strip=True)

                    try:
                        valor = float(valor_str.replace(".", "").replace(",", "."))
                    except ValueError:
                        valor = valor_str

                    return {
                        "fecha": fecha,
                        "valor": valor,
                        "descripcion": "Unidad de Valor Adquisitivo (UVA)",
                    }

        return None

    except Exception as e:
        print(f"Error scraping UVA: {e}")
        return None


def merge_uva(historico, nuevo):
    if not nuevo:
        return historico

    for item in historico:
        if item["fecha"] == nuevo["fecha"]:
            print(f"ℹ UVA {nuevo['fecha']} ya existe")
            return historico

    historico.append(nuevo)
    print(f"✔ UVA agregado: {nuevo['fecha']}")
    return historico


if __name__ == "__main__":
    historico = []
    uva_data = obtener_uva_actual()
    historico = merge_uva(historico, uva_data)
    save_dataset_json(dataset="uva", data=historico)
