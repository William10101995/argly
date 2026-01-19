import requests
from bs4 import BeautifulSoup
import urllib3
from utils import save_dataset_json
import json
import os

# Deshabilitar advertencias de certificado SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def obtener_icl_actual():
    """
    Scrapea la web del BCRA y devuelve un diccionario con los datos del ICL.
    Retorna None si falla.
    """
    url = "https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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

                # Buscamos el ICL
                if "Locación" in descripcion and "ICL" in descripcion:
                    fecha = cols[1].get_text(strip=True)
                    valor_str = cols[2].get_text(strip=True)

                    # Limpiamos el valor para que sea un número flotante válido
                    # Reemplazamos coma por punto
                    try:
                        valor_num = float(valor_str.replace(".", "").replace(",", "."))
                    except ValueError:
                        valor_num = valor_str  # Si falla, guardamos el string original

                    # Retornamos el Objeto (diccionario)
                    return {
                        "fecha": fecha,
                        "valor": valor_num,
                        "descripcion": "ICL - Ley 27.551",
                    }
        return None

    except Exception as e:
        print(f"Error en el scraping: {e}")
        return None


def merge_icl(historico, nuevo_dato):
    if not nuevo_dato:
        return historico

    for item in historico:
        if item["fecha"] == nuevo_dato["fecha"]:
            print(f"ℹ ICL {nuevo_dato['fecha']} ya existe")
            return historico

    historico.append(nuevo_dato)
    print(f"✔ ICL agregado: {nuevo_dato['fecha']}")
    return historico


if __name__ == "__main__":

    historico = []
    icl_data = obtener_icl_actual()

    historico = merge_icl(historico, icl_data)

    save_dataset_json(dataset="icl", data=historico)
