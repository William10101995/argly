import hashlib
import threading
import time
import logging
from flask import request, g
from supabase import create_client, Client
import os

logger = logging.getLogger(__name__)

# Cliente Supabase inicializado una sola vez
_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")  # usa service_role, no anon
        if not url or not key:
            raise RuntimeError("SUPABASE_URL o SUPABASE_SERVICE_KEY no configurados")
        _supabase = create_client(url, key)
    return _supabase


def _hash_ip(ip: str) -> str:
    """SHA-256 truncado a 16 chars. No reversible, cumple privacidad."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def _get_client_ip() -> str:
    """Vercel pone la IP real en X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _get_country() -> str | None:
    """Vercel agrega el país en el header x-vercel-ip-country."""
    return request.headers.get("X-Vercel-IP-Country")


def _insert_log(data: dict) -> None:
    """
    Ejecuta el insert en un thread separado para no bloquear el response.
    Si falla, solo loguea — nunca debe afectar al usuario.
    """
    try:
        get_supabase().table("api_logs").insert(data).execute()
    except Exception as exc:
        logger.warning("analytics insert failed: %s", exc)


def before_request() -> None:
    """Registra el timestamp de inicio en el contexto del request."""
    g.analytics_start = time.monotonic()


def after_request(response):
    """
    Captura los datos del request completado y los inserta en background.
    Siempre retorna el response sin modificarlo.
    """
    try:
        elapsed_ms = int(
            (time.monotonic() - g.get("analytics_start", time.monotonic())) * 1000
        )

        skip_prefixes = ("/static", "/favicon", "/_", "/health", "/api/admin")
        if request.path.startswith(skip_prefixes):
            return response

        ua = (request.headers.get("User-Agent") or "").lower()
        skip_agents = (
            "vercel-favicon",
            "bot",
            "crawler",
            "spider",
            "pingdom",
            "uptimerobot",
        )
        if any(agent in ua for agent in skip_agents):
            return response

        data = {
            "endpoint": request.path,
            "method": request.method,
            "status_code": response.status_code,
            "response_ms": elapsed_ms,
            "ip_hash": _hash_ip(_get_client_ip()),
            "user_agent": (request.headers.get("User-Agent") or "")[:255],
            "country": _get_country(),
        }

        t = threading.Thread(target=_insert_log, args=(data,), daemon=True)
        t.start()

    except Exception as exc:
        logger.warning("analytics middleware error: %s", exc)

    return response
