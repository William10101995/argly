from .combustibles import combustibles_bp
from .icl import icl_bp
from .ipc import ipc_bp
from .uvi import uvi_bp
from .uva import uva_bp
from .cer import cer_bp
from .rios import rios_bp
from .construccion import construccion_bp
from .credit import credit_bp
from .medicamentos import medicamentos_bp
from .provincias import provincias_bp
from .canasta import canasta_bp


def register_routes(app):
    app.register_blueprint(combustibles_bp)
    app.register_blueprint(icl_bp)
    app.register_blueprint(ipc_bp)
    app.register_blueprint(uvi_bp)
    app.register_blueprint(uva_bp)
    app.register_blueprint(cer_bp)
    app.register_blueprint(rios_bp)
    app.register_blueprint(construccion_bp)
    app.register_blueprint(credit_bp)
    app.register_blueprint(medicamentos_bp)
    app.register_blueprint(provincias_bp)
    app.register_blueprint(canasta_bp)
