from bs4 import BeautifulSoup
import requests
import re
import json
import os
from utils import save_dataset_json

ARCHIVO_JSON = "ipc_historico.json"

URL = "https://www.indec.gob.ar/Nivel4/Tema/3/5/31"

HEADERS = {"User-Agent": "Mozilla/5.0"}

MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

# REQUEST

response = requests.get(URL, headers=HEADERS, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# FECHA DE PUBLICACIÓN

fecha_publicacion = None
anio_publicacion = None

titulo = soup.select_one(".card-titulo3")
if titulo:
    match = re.search(r"(\d{1,2}/\d{1,2}/\d{2})", titulo.get_text())
    if match:
        fecha_publicacion = match.group(1)
        anio_publicacion = 2000 + int(fecha_publicacion.split("/")[-1])

# TEXTO PRINCIPAL IPC

indice_ipc = None
mes_ipc = None
anio_ipc = None

texto_ipc = soup.select_one(".card-texto3 p")
if texto_ipc:
    texto = texto_ipc.get_text(" ", strip=True)

    # Índice IPC → float
    match_indice = re.search(r"variación de ([\d,]+)%", texto)
    if match_indice:
        indice_ipc = float(match_indice.group(1).replace(",", "."))

    # Mes IPC
    match_mes = re.search(r"registró en ([a-zA-Záéíóúñ]+)", texto, re.IGNORECASE)
    if match_mes:
        mes_ipc = match_mes.group(1).lower()

# AÑO IPC (MES VENCIDO)

if mes_ipc and anio_publicacion:
    if MESES.get(mes_ipc) == 12:
        anio_ipc = anio_publicacion - 1
    else:
        anio_ipc = anio_publicacion

# PRÓXIMO INFORME

fecha_proximo_informe = None

for p in soup.find_all("p"):
    if "Próximo informe técnico" in p.get_text():
        match = re.search(r"(\d{1,2}/\d{1,2}/\d{2})", p.get_text())
        if match:
            fecha_proximo_informe = match.group(1)
        break

# RESULTADO FINAL

resultado = {
    "indice_ipc": indice_ipc,
    "mes": mes_ipc,
    "anio": anio_ipc,
    "fecha_publicacion": fecha_publicacion,
    "fecha_proximo_informe": fecha_proximo_informe,
}

# CARGAR HISTÓRICO

historico = []

# EVITAR DUPLICADOS (mes + año)

ya_existe = any(
    item["mes"] == resultado["mes"] and item["anio"] == resultado["anio"]
    for item in historico
)

if not ya_existe:
    historico.append(resultado)
    print("✔ Nuevo registro agregado")
else:
    print("ℹ El registro ya existe, no se agregó")

# GUARDAR JSON

save_dataset_json(dataset="ipc", data=historico)
