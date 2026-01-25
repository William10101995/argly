from flask import Blueprint, request
from api.services.data_loader import (
    get_rios,
    get_rio_by_nombre,
)
from api.utils.responses import success, error

rios_bp = Blueprint("rios", __name__, url_prefix="/api/rios")


@rios_bp.route("/", methods=["GET"])
def obtener_rios():
    data = get_rios()
    if not data:
        return error("No hay datos de ríos disponibles", 404)
    return success(data)


@rios_bp.route("/rio/<nombre>", methods=["GET"])
def obtener_rio(nombre):
    data = get_rio_by_nombre(nombre)
    if not data:
        return error("Río no encontrado", 404)
    return success(data)
