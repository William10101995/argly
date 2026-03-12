from flask import Blueprint
from api.services.data_loader import get_provincias
from api.utils.responses import success, error

provincias_bp = Blueprint("provincias", __name__, url_prefix="/api/provincias")


@provincias_bp.route("/", methods=["GET"])
def obtener_provincias():
    data = get_provincias()

    if not data:
        return error("No hay datos geográficos disponibles", 404)

    return success(data)
