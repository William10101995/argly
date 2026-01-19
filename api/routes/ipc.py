from flask import Blueprint
from api.services.data_loader import get_ipc, get_ipc_history
from api.utils.responses import success, error

ipc_bp = Blueprint("ipc", __name__, url_prefix="/api/ipc")


@ipc_bp.route("/", methods=["GET"])
def obtener_ipc():
    data = get_ipc()
    if not data:
        return error("No hay datos de IPC disponibles", 404)
    return success(data)


@ipc_bp.route("/history", methods=["GET"])
def obtener_ipc_historico():
    data = get_ipc_history()
    if not data:
        return error("No hay histórico de IPC disponible", 404)
    return success(data)
