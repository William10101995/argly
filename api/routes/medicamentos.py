from flask import Blueprint, jsonify
from api.services.medicamentos_service import obtener_medicamentos

medicamentos_bp = Blueprint("medicamentos", __name__, url_prefix="/api/medicamentos")


@medicamentos_bp.route("/<medicamento>", methods=["GET"])
def medicamentos(medicamento):

    try:
        data = obtener_medicamentos(medicamento)
        return jsonify(data)

    except Exception as e:
        return (
            jsonify({"error": "Error consultando medicamentos", "detalle": str(e)}),
            500,
        )
