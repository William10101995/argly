from flask import Blueprint, jsonify
from api.utils.analytics import get_supabase
from api.utils.responses import success
from api.extensions import limiter
from collections import defaultdict

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/estadisticas/resumen")
@limiter.limit("30 per minute")
def resumen():
    resultado = get_supabase().rpc("get_stats_overview").execute()
    return success(resultado.data)


@admin_bp.get("/estadisticas/serie-temporal")
@limiter.limit("30 per minute")
def serie_temporal():
    filas = (
        get_supabase()
        .table("api_logs_hourly")
        .select("hour, total_requests, error_count, avg_response_ms")
        .gte("hour", "now() - interval '72 hours'")
        .order("hour")
        .execute()
    )
    return success(filas.data)


@admin_bp.get("/estadisticas/endpoints")
@limiter.limit("30 per minute")
def endpoints():
    filas = (
        get_supabase()
        .table("api_logs_daily")
        .select(
            "endpoint, total_requests, error_count, unique_callers, avg_response_ms"
        )
        .gte("day", "now() - interval '30 days'")
        .order("total_requests", desc=True)
        .limit(20)
        .execute()
    )

    agg = defaultdict(
        lambda: {
            "total_requests": 0,
            "error_count": 0,
            "unique_callers": 0,
            "response_ms_sum": 0,
        }
    )
    for fila in filas.data:
        ep = fila["endpoint"]
        agg[ep]["total_requests"] += fila["total_requests"]
        agg[ep]["error_count"] += fila["error_count"]
        agg[ep]["unique_callers"] += fila["unique_callers"]
        agg[ep]["response_ms_sum"] += (fila["avg_response_ms"] or 0) * fila[
            "total_requests"
        ]

    resultado = []
    for ep, v in sorted(agg.items(), key=lambda x: -x[1]["total_requests"]):
        resultado.append(
            {
                "endpoint": ep,
                "total_requests": v["total_requests"],
                "cantidad_errores": v["error_count"],
                "tasa_error": round(
                    v["error_count"] / max(v["total_requests"], 1) * 100, 2
                ),
                "callers_unicos": v["unique_callers"],
                "latencia_promedio_ms": round(
                    v["response_ms_sum"] / max(v["total_requests"], 1)
                ),
            }
        )
    return success(resultado)


@admin_bp.get("/estadisticas/paises")
@limiter.limit("30 per minute")
def paises():
    filas = get_supabase().rpc("get_country_stats", {"days_back": 7}).execute()
    return success(filas.data)
