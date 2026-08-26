# api/routes/v1/dolares.py
import re
from flask import Blueprint, request
from api.services.dolares_service import (
    get_dolares,
    get_dolar_por_tipo,
    get_dolares_history,
    get_dolares_range,
    TIPOS_VALIDOS,
)
from api.utils.responses import success, error

PARAMS_VALIDOS = {"tipo", "desde", "hasta", "historico"}
FORMATO_FECHA = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")

dolares_v1_bp = Blueprint("dolares_v1", __name__, url_prefix="/v1/dolares")


def validar_fecha(valor, nombre):
    if not FORMATO_FECHA.match(valor):
        return error(
            f"El parametro '{nombre}' debe tener formato YYYY-MM-DD (ej: 2024-01-15)",
            400,
        )
    return None


@dolares_v1_bp.route("/", methods=["GET"])
def obtener_dolares():
    params_recibidos = set(request.args.keys())
    params_invalidos = params_recibidos - PARAMS_VALIDOS

    if params_invalidos:
        return error(
            f"Parametro(s) no reconocido(s): {', '.join(params_invalidos)}. "
            f"Parametros validos: {', '.join(PARAMS_VALIDOS)}",
            400,
        )

    tipo = request.args.get("tipo", "").lower().strip()
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    historico = request.args.get("historico", "").lower()

    if "historico" in params_recibidos:
        if historico != "true":
            return error(
                "El parametro 'historico' solo acepta el valor 'true' "
                "(ej: ?historico=true)",
                400,
            )
        data = get_dolares_history()
        if not data:
            return error("No hay historico de dolares disponible", 404)
        return success(data)

    if "desde" in params_recibidos or "hasta" in params_recibidos:
        if not desde or not hasta:
            return error(
                "Los parametros 'desde' y 'hasta' son requeridos en conjunto "
                "y no pueden estar vacios (formato: YYYY-MM-DD)",
                400,
            )

        err = validar_fecha(desde, "desde") or validar_fecha(hasta, "hasta")
        if err:
            return err

        data = get_dolares_range(desde, hasta)
        if not data:
            return error("No hay datos para el rango solicitado", 404)
        return success(data)

    if "tipo" in params_recibidos:
        if not tipo:
            return error(
                "El parametro 'tipo' no puede estar vacio (ej: ?tipo=blue)", 400
            )
        if tipo not in TIPOS_VALIDOS:
            return error(
                f"Tipo '{tipo}' no reconocido. Tipos validos: "
                f"{', '.join(sorted(TIPOS_VALIDOS))}",
                400,
            )
        try:
            data = get_dolar_por_tipo(tipo)
        except ConnectionError as e:
            return error(f"Error al conectar con la fuente de datos: {e}", 503)
        except FileNotFoundError as e:
            return error(str(e), 503)
        if not data:
            return error(f"No hay datos disponibles para '{tipo}'", 404)
        return success({tipo: data})

    try:
        data = get_dolares()
    except ConnectionError as e:
        return error(f"Error al conectar con la fuente de datos: {e}", 503)
    except FileNotFoundError as e:
        return error(str(e), 503)

    if not data:
        return error("No hay datos de dolares disponibles", 404)

    return success(data)
