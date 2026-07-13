# api/routes/legacy/rios.py
from flask import Blueprint
from api.services.data_loader import get_rios, get_rio_by_nombre
from api.utils.responses import success, error

SUNSET_DATE = "Fri, 01 Jan 2027 00:00:00 GMT"
V1_BASE = "https://api.argly.com.ar/v1/rios"

rios_bp = Blueprint("rios", __name__, url_prefix="/api/rios")


@rios_bp.after_request
def add_deprecation_headers(response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = SUNSET_DATE
    response.headers["Link"] = f'<{V1_BASE}>; rel="successor-version"'
    return response


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
