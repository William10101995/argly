from flask import Blueprint, jsonify
from api.services.credit_scoring import calculate_credit_profile

credit_bp = Blueprint("credito", __name__, url_prefix="/api/credito")


@credit_bp.route("/<cuil>/<salary>/<tna>", methods=["GET"])
def credit_score(cuil, salary, tna):

    try:

        salary = float(salary)
        tna = float(tna)

        result = calculate_credit_profile(cuil, salary, tna)

        return jsonify(result)

    except Exception as e:

        return jsonify({"error": str(e)}), 500
