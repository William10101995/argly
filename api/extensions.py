from flask import request
from flask_cors import CORS
from flask_limiter import Limiter

cors = CORS()


def get_real_client_ip():
    """
    Con CloudFront delante de API Gateway, request.remote_addr deja de ser
    la IP del cliente real. X-Forwarded-For tiene la IP real como primer elemento.
    """
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


limiter = Limiter(key_func=get_real_client_ip)