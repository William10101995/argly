from flask import Blueprint
from api.services.data_loader import get_icl, get_icl_history
from api.utils.responses import success, error

icl_bp = Blueprint("icl", __name__, url_prefix="/api/icl")


@icl_bp.route("/", methods=["GET"])
def obtener_icl():
    data = get_icl()
    if not data:
        return error("No hay datos de ICL disponibles", 404)
    return success(data)


@icl_bp.route("/history", methods=["GET"])
def obtener_icl_history():
    data = get_icl_history()
    if not data:
        return error("No hay historial de ICL disponible", 404)
    return success(data)
