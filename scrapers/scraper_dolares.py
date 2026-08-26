"""
Scraper Dólares — combina múltiples fuentes con roles distintos:

  1. AMBITO       -> fuente primaria, cobertura completa (oficial, blue,
                      mayorista, bolsa/MEP, contadoconliqui/CCL, cripto,
                      tarjeta).
  2. BNA          -> fuente AUTORITATIVA exclusiva del tipo "oficial"
                      (pisa el valor de Ámbito si responde OK).
  3. DOLARHOY     -> fallback de disponibilidad. Sólo llena tipos que
                      Ámbito no haya podido traer.
  4. FINANZAS ARGY -> auditoría no bloqueante. Nunca escribe datos, sólo
                      genera alertas de divergencia en el log.

Mismo patrón que el resto de los scrapers del repo: guarda
data/dolares/latest.json + data/dolares/YYYY-MM-DD.json vía
save_dataset_json(). El histórico intradía NO se preserva (igual que UVA/
CER/UVI, que también corren varias veces por día): cada corrida sobrescribe
por completo el snapshot del día. Si en el futuro se quiere serie intradía,
habría que versionar por timestamp en vez de por fecha — evaluar cuando
haya demanda real de ese caso de uso.
"""

from utils import save_dataset_json, upload_json_to_s3
from sources import ambito_dolar, bna_dolar, dolarhoy_dolar, finanzasargy_dolar

UMBRAL_DIVERGENCIA = 0.03  # 3% — por encima de esto se loguea una alerta


def combinar_fuentes() -> dict:
    resultado = {}
    fuentes_ok = []
    fuentes_fail = []

    # 1. Ámbito: fuente primaria
    try:
        ambito_data = ambito_dolar.obtener_todos()
        if ambito_data:
            for tipo, valores in ambito_data.items():
                resultado[tipo] = {**valores, "fuente": "ambito.com"}
            fuentes_ok.append("ambito")
        else:
            fuentes_fail.append("ambito")
    except Exception as e:
        print(f"⚠ Error inesperado consultando Ámbito: {e}")
        fuentes_fail.append("ambito")

    # 2. DolarHoy: fallback — sólo completa lo que falte
    try:
        dolarhoy_data = dolarhoy_dolar.obtener_todos()
        if dolarhoy_data:
            fuentes_ok.append("dolarhoy")
            for tipo, valores in dolarhoy_data.items():
                if tipo not in resultado:
                    resultado[tipo] = {**valores, "fuente": "dolarhoy.com"}
        else:
            fuentes_fail.append("dolarhoy")
    except Exception as e:
        print(f"⚠ Error inesperado consultando DolarHoy: {e}")
        fuentes_fail.append("dolarhoy")

    # 3. BNA: pisa "oficial" porque es la fuente autoritativa real
    try:
        bna_oficial = bna_dolar.obtener_oficial()
        if bna_oficial:
            resultado["oficial"] = {**bna_oficial, "fuente": "bna.com.ar"}
            fuentes_ok.append("bna")
        else:
            fuentes_fail.append("bna")
    except Exception as e:
        print(f"⚠ Error inesperado consultando BNA: {e}")
        fuentes_fail.append("bna")

    # 4. Finanzas Argy: auditoría no bloqueante
    try:
        fa_data = finanzasargy_dolar.obtener_todos()
        if fa_data:
            fuentes_ok.append("finanzasargy")
            _auditar_divergencias(resultado, fa_data)
    except Exception as e:
        print(f"ℹ Finanzas Argy no disponible (no bloqueante): {e}")

    resultado["_meta"] = {
        "fuentes_consultadas": fuentes_ok,
        "fuentes_fallidas": fuentes_fail,
    }

    return resultado


def _auditar_divergencias(resultado: dict, fa_data: dict) -> None:
    """
    Compara el valor de 'venta' combinado contra Finanzas Argy y loguea
    (sin bloquear ni modificar nada) si la diferencia supera el umbral.
    Útil para detectar de forma temprana si una fuente empezó a devolver
    datos corruptos o desactualizados.
    """
    for tipo, valores_fa in fa_data.items():
        actual = resultado.get(tipo)
        if not actual or not actual.get("venta") or not valores_fa.get("venta"):
            continue

        venta_actual = actual["venta"]
        venta_fa = valores_fa["venta"]
        divergencia = abs(venta_actual - venta_fa) / venta_actual

        if divergencia > UMBRAL_DIVERGENCIA:
            print(
                f"🔶 Divergencia [{tipo}]: combinado=${venta_actual} "
                f"vs finanzasargy=${venta_fa} ({divergencia:.1%}) — revisar"
            )


def hay_datos_utiles(data: dict) -> bool:
    """Al menos un tipo de cambio real, más allá de _meta."""
    return any(k != "_meta" for k in data)


if __name__ == "__main__":
    combinado = combinar_fuentes()

    if not hay_datos_utiles(combinado):
        print("❌ Ninguna fuente respondió con datos útiles. No se guarda nada.")
        exit(1)

    fuentes_fail = combinado["_meta"]["fuentes_fallidas"]
    if fuentes_fail:
        print(f"⚠ Fuentes fallidas este ciclo: {', '.join(fuentes_fail)}")

    print(f"✔ Cotizaciones combinadas: {[k for k in combinado if k != '_meta']}")
    save_dataset_json(dataset="dolares", data=[combinado])
    upload_json_to_s3(dataset="dolares", data=[combinado])
