from flask import Blueprint
from api.utils.analytics import get_supabase
from api.utils.responses import success
from api.extensions import limiter
from collections import defaultdict
from datetime import datetime, timezone, timedelta

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/estadisticas/resumen")
@limiter.limit("30 per minute")
def resumen():
    resultado = get_supabase().rpc("get_stats_overview").execute()
    return success(resultado.data)


@admin_bp.get("/estadisticas/serie-temporal")
@limiter.limit("30 per minute")
def serie_temporal():
    resultado = get_supabase().rpc("get_hourly_series", {"hours_back": 72}).execute()
    return success(resultado.data)


@admin_bp.get("/estadisticas/endpoints")
@limiter.limit("30 per minute")
def endpoints():
    resultado = get_supabase().rpc("get_endpoint_stats", {"days_back": 30}).execute()
    return success(resultado.data)


@admin_bp.get("/estadisticas/paises")
@limiter.limit("30 per minute")
def paises():
    filas = get_supabase().rpc("get_country_stats", {"days_back": 7}).execute()
    return success(filas.data)
