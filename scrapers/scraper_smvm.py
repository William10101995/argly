import requests
import csv
import json
from datetime import datetime
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

URL = "https://infra.datos.gob.ar/catalog/sspm/dataset/57/distribution/57.1/download/indice-salario-minimo-vital-movil-valores-mensuales-pesos-corrientes-desde-1988.csv"

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "smvm"
LATEST_FILE = DATA_DIR / "latest.json"

FUENTE = "https://www.argentina.gob.ar/trabajo/consejodelsalario"


# ------------------------
# REDONDEO FINANCIERO
# ------------------------
def a_dos_decimales(valor):
    return float(Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# ------------------------
# DESCARGAR CSV
# ------------------------
def descargar_csv():
    response = requests.get(URL, timeout=20)
    response.raise_for_status()
    return response.text


# ------------------------
# PARSEAR CSV
# ------------------------
def parsear_csv(texto_csv: str, hoy: datetime | None = None):
    """
    El CSV de datos.gob.ar publica con antelación valores que todavía no
    entraron en vigencia (el Consejo del Salario anuncia aumentos futuros
    con meses de anticipación). Por eso NO tomamos directamente el máximo
    de todo el archivo: filtramos primero por fecha <= hoy, y de esos
    registros ya vigentes tomamos el más reciente.

    Esto hace que el scraper se actualice solo mes a mes a medida que cada
    fecha de vigencia llega, y se autocorrige si alguna corrida mensual
    se salta (no depende de "avanzar un registro" respecto al guardado).
    """
    hoy = hoy or datetime.now()
    reader = csv.DictReader(texto_csv.splitlines())

    registros = []

    for row in reader:
        try:
            fecha_dt = datetime.strptime(row["indice_tiempo"], "%Y-%m-%d")

            # Descartar valores que el CSV ya publicó pero todavía no
            # entraron en vigencia.
            if fecha_dt > hoy:
                continue

            registros.append(
                {
                    "fecha_dt": fecha_dt,
                    "vigente_desde": fecha_dt.strftime("%d/%m/%Y"),
                    "smvm": a_dos_decimales(row["salario_minimo_vital_movil_mensual"]),
                    "smvm_dia": a_dos_decimales(
                        row["salario_minimo_vital_movil_diario"]
                    ),
                    "smvm_hora": a_dos_decimales(
                        row["salario_minimo_vital_movil_hora"]
                    ),
                }
            )
        except Exception:
            continue

    if not registros:
        raise ValueError("No se pudieron parsear registros vigentes del CSV")

    # ordenar por fecha descendente → el primero es el vigente hoy
    registros.sort(key=lambda x: x["fecha_dt"], reverse=True)

    return registros[0]


# ------------------------
# CARGAR LATEST
# ------------------------
def cargar_latest():
    if not LATEST_FILE.exists():
        return None

    try:
        with open(LATEST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            return data[0]
    except Exception:
        return None

    return None


# ------------------------
# GUARDAR JSON
# ------------------------
def guardar_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump([data], f, indent=2, ensure_ascii=False)


# ------------------------
# MAIN
# ------------------------
def main():
    print("⬇ Descargando dataset SMVM...")
    csv_text = descargar_csv()

    print("🔎 Procesando datos...")
    ultimo = parsear_csv(csv_text)

    # limpiar campo auxiliar
    ultimo.pop("fecha_dt")
    ultimo["fuente"] = FUENTE

    print("✔ Último SMVM vigente detectado:")
    print(f"   Fecha: {ultimo['vigente_desde']}")
    print(f"   Mensual: ${ultimo['smvm']:,.2f}")

    latest = cargar_latest()

    # ------------------------
    # CONTROL DE CAMBIO
    # ------------------------
    if latest:
        misma_fecha = latest.get("vigente_desde") == ultimo["vigente_desde"]
        mismo_valor = latest.get("smvm") == ultimo["smvm"]

        if misma_fecha and mismo_valor:
            print("ℹ No hay cambios, no se genera nueva versión")
            return

    # ------------------------
    # VERSIONADO
    # ------------------------
    fecha_file = datetime.strptime(ultimo["vigente_desde"], "%d/%m/%Y").strftime(
        "%Y-%m-%d"
    )

    version_file = DATA_DIR / f"{fecha_file}.json"

    guardar_json(version_file, ultimo)
    print(f"✔ Nuevo archivo versionado: {version_file.name}")

    # ------------------------
    # ACTUALIZAR LATEST
    # ------------------------
    guardar_json(LATEST_FILE, ultimo)
    print("✔ latest.json actualizado")


# ------------------------
# ENTRYPOINT
# ------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Error:", str(e))