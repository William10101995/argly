from flask import Blueprint, request
from api.utils.responses import success, error
from api.services.personas_service import get_resumen, get_all, get_por_anio

personas_desaparecidas_bp = Blueprint(
    "personas_desaparecidas", __name__, url_prefix="/api"
)


@personas_desaparecidas_bp.route("/personas-desaparecidas", methods=["GET"])
def personas_desaparecidas():
    """
    Lista de personas desaparecidas actualmente buscadas por el SIFEBU.

    Query params:
      - anio (int, opcional): filtra por año de desaparición. Ej: ?anio=2024
    """
    anio_param = request.args.get("anio")

    if anio_param is not None:
        try:
            anio = int(anio_param)
        except ValueError:
            return error("El parámetro 'anio' debe ser un número entero.", 400)
        if anio < 1990 or anio > 2100:
            return error("El parámetro 'anio' está fuera de rango.", 400)
    else:
        anio = None

    try:
        data = get_all(anio=anio)
        return success(data)
    except FileNotFoundError as e:
        return error(str(e), 503)
    except Exception as e:
        return error(f"Error interno: {e}", 500)
