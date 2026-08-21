# api/routes/v1/rios_comahue.py
from flask import Blueprint, request
from api.services.rios_comahue_service import get_rios_comahue
from api.utils.responses import success, error

PARAMS_VALIDOS = {"rio"}

rios_comahue_v1_bp = Blueprint(
    "rios_comahue_v1", __name__, url_prefix="/v1/rios-comahue"
)


@rios_comahue_v1_bp.route("/", methods=["GET"])
def obtener_rios_comahue():
    params_recibidos = set(request.args.keys())
    params_invalidos = params_recibidos - PARAMS_VALIDOS

    if params_invalidos:
        return error(
            f"Parámetro(s) no reconocido(s): {', '.join(params_invalidos)}. "
            f"Parámetros válidos: {', '.join(PARAMS_VALIDOS)}",
            400,
        )

    rio = request.args.get("rio")

    try:
        data = get_rios_comahue(rio)
        return success(data)
    except ValueError as e:
        return error(str(e), 400)
    except FileNotFoundError as e:
        return error(str(e), 503)
    except Exception as e:
        return error(f"Error interno: {e}", 500)