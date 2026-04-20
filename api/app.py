from flask import Flask
from flask_compress import Compress
from api.config import get_config
from api.extensions import cors, limiter
from api.routes import register_routes
from api.utils.analytics import before_request, after_request

compress = Compress()


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.json.sort_keys = False
    app.url_map.strict_slashes = False
    compress.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    limiter.init_app(app)

    register_routes(app)
    app.before_request(before_request)
    app.after_request(after_request)

    @app.route("/", methods=["GET"])
    def health():
        return {"status": "ok"}

    return app
