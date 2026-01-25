from .combustibles import combustibles_bp
from .icl import icl_bp
from .ipc import ipc_bp
from .uvi import uvi_bp
from .uva import uva_bp
from .rios import rios_bp


def register_routes(app):
    app.register_blueprint(combustibles_bp)
    app.register_blueprint(icl_bp)
    app.register_blueprint(ipc_bp)
    app.register_blueprint(uvi_bp)
    app.register_blueprint(uva_bp)
    app.register_blueprint(rios_bp)
