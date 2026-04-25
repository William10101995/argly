from flask import Blueprint, jsonify
from api.services.medicamentos_service import obtener_medicamentos
from urllib.parse import unquote

medicamentos_bp = Blueprint("medicamentos", __name__, url_prefix="/api/medicamentos")


@medicamentos_bp.route("/<medicamento>", methods=["GET"])
def medicamentos(medicamento):

    try:
        nombre = unquote(medicamento)
        data = obtener_medicamentos(nombre)
        return jsonify(data)

    except Exception as e:
        return (
            jsonify({"error": "Error consultando medicamentos", "detalle": str(e)}),
            500,
        )

