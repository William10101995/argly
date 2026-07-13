from bs4 import BeautifulSoup
import requests
import re
import json
import os
from datetime import datetime
from utils import save_dataset_json

# Configuración
URL = "https://www.indec.gob.ar/Nivel4/Tema/3/5/33"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DATASET_PATH = "data/construccion/latest.json"

# =========================
# UTILS
# =========================


def normalizar_fecha(fecha: str | None) -> str | None:
    if not fecha:
        return None
    try:
        partes = fecha.split("/")
        d, m, y = partes[0].zfill(2), partes[1].zfill(2), partes[2]
        if len(y) == 2:
            y = "20" + y
        return f"{d}/{m}/{y}"
    except Exception:
        return fecha


# =========================
# REQUEST & EXTRACCIÓN INDEC
# =========================

response = requests.get(URL, headers=HEADERS, timeout=20)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# 1. Periodo del dato (Mes vencido)
texto_pagina = soup.get_text()
match_pub = re.search(r"(\d{1,2}/\d{1,2}/\d{2})", texto_pagina)
fecha_pub_raw = match_pub.group(1) if match_pub else None

fecha_obj = datetime.strptime(fecha_pub_raw, "%d/%m/%y")
mes_dato = 12 if fecha_obj.month == 1 else fecha_obj.month - 1
anio_dato = fecha_obj.year - 1 if fecha_obj.month == 1 else fecha_obj.year

# =========================
# VALIDACIÓN DE PERIODO
# =========================

if os.path.exists(DATASET_PATH):
    with open(DATASET_PATH, "r") as f:
        data_existente = json.load(f)

    ultimo = data_existente[-1] if isinstance(data_existente, list) else data_existente

    if ultimo["mes"] == mes_dato and ultimo["anio"] == anio_dato:
        print(
            f"ℹ El INDEC aún no ha actualizado. Datos de {mes_dato}/{anio_dato} ya procesados."
        )
        exit()

# =========================
# EXTRACCIÓN DE CONTENIDO
# =========================

# Extraer Próximo Informe
fecha_prox_raw = None
for p in soup.find_all("p"):
    texto_p = p.get_text()
    if "Próximo informe técnico" in texto_p:
        match_p = re.search(r"(\d{1,2}/\d{1,2}/\d{2})", texto_p)
        fecha_prox_raw = match_p.group(1) if match_p else None
        break

# Extraer Variaciones
texto_limpio = " ".join(
    " ".join([p.get_text(" ", strip=True) for p in soup.find_all("p")]).split()
).replace("\xa0", " ")


def extraer_valor(pattern, texto):
    m = re.search(pattern, texto, re.IGNORECASE)
    return float(m.group(1).replace(",", ".")) if m else None


var_gen = extraer_valor(r"suba de ([\d,]+)%", texto_limpio)
var_mat = extraer_valor(r"([\d,]+)%\s+en\D+Materiales", texto_limpio)
var_mo = extraer_valor(r"([\d,]+)%\s+en\D+Mano de obra", texto_limpio)
var_gg = extraer_valor(r"([\d,]+)%\s+en\D+Gastos generales", texto_limpio)

# =========================
# CÁLCULO SOBRE BASE ANTERIOR
# =========================

p_mat_base = ultimo["precio_m2_actual"]["materiales"]
p_mo_base = ultimo["precio_m2_actual"]["mano_obra"]
p_gg_base = ultimo["precio_m2_actual"]["gastos_generales"]

p_mat_final = round(p_mat_base * (1 + (var_mat or 0) / 100), 2)
p_mo_final = round(p_mo_base * (1 + (var_mo or 0) / 100), 2)
p_gg_final = round(p_gg_base * (1 + (var_gg or 0) / 100), 2)
p_total_final = round(p_mat_final + p_mo_final + p_gg_final, 2)

# =========================
# GUARDADO ÚNICO
# =========================

nuevo_registro = {
    "fuente": "INDEC ICC",
    "mes": mes_dato,
    "anio": anio_dato,
    "fecha_publicacion": normalizar_fecha(fecha_pub_raw),
    "fecha_proximo_informe": normalizar_fecha(fecha_prox_raw),  # <-- Reintegrado
    "variaciones": {
        "general": var_gen,
        "materiales": var_mat,
        "mano_obra": var_mo,
        "gastos_generales": var_gg,
    },
    "precio_m2_actual": {
        "materiales": p_mat_final,
        "mano_obra": p_mo_final,
        "gastos_generales": p_gg_final,
        "total": p_total_final,
    },
}

save_dataset_json(dataset="construccion", data=[nuevo_registro])
print(
    f"✔ Nuevo periodo detectado y guardado: {mes_dato}/{anio_dato}. Total: ${p_total_final}"
)
