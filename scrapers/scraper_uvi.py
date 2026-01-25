import requests
from bs4 import BeautifulSoup
import urllib3
from utils import save_dataset_json

# Deshabilitar advertencias de certificado SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def obtener_uvi_actual():
    """
    Scrapea la web del BCRA y devuelve un diccionario con los datos de la UVI.
    Retorna None si falla.
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

        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                descripcion = cols[0].get_text(strip=True)

                # Buscamos la UVI
                if "Unidad de Vivienda" in descripcion and "UVI" in descripcion:
                    fecha = cols[1].get_text(strip=True)
                    valor_str = cols[2].get_text(strip=True)

                    try:
                        valor_num = float(valor_str.replace(".", "").replace(",", "."))
                    except ValueError:
                        valor_num = valor_str

                    return {
                        "fecha": fecha,
                        "valor": valor_num,
                        "descripcion": "Unidad de Vivienda (UVI)",
                    }

        return None

    except Exception as e:
        print(f"Error en el scraping UVI: {e}")
        return None


def merge_uvi(historico, nuevo_dato):
    if not nuevo_dato:
        return historico

    for item in historico:
        if item["fecha"] == nuevo_dato["fecha"]:
            print(f"ℹ UVI {nuevo_dato['fecha']} ya existe")
            return historico

    historico.append(nuevo_dato)
    print(f"✔ UVI agregado: {nuevo_dato['fecha']}")
    return historico


if __name__ == "__main__":

    historico = []
    uvi_data = obtener_uvi_actual()

    historico = merge_uvi(historico, uvi_data)

    save_dataset_json(dataset="uvi", data=historico)
