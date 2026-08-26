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
from .personas_desaparecidas import personas_desaparecidas_bp
from .admin import admin_bp
from .v1.smvm import smvm_v1_bp
from .v1.ipc import ipc_v1_bp
from .v1.canasta import canasta_v1_bp
from .v1.cer import cer_v1_bp
from .v1.combustibles import combustibles_v1_bp
from .v1.construccion import construccion_v1_bp
from .v1.icl import icl_v1_bp
from .v1.uva import uva_v1_bp
from .v1.uvi import uvi_v1_bp
from .v1.rios import rios_v1_bp
from .v1.personas import personas_desaparecidas_v1_bp
from .v1.provincias import provincias_v1_bp
from .v1.medicamentos import medicamentos_v1_bp
from .v1.riesgo_pais import riesgo_pais_v1_bp
from .v1.diputados import diputados_v1_bp
from .v1.rios_comahue import rios_comahue_v1_bp
from .v1.dolares import dolares_v1_bp


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
    app.register_blueprint(personas_desaparecidas_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(smvm_v1_bp)
    app.register_blueprint(ipc_v1_bp)
    app.register_blueprint(canasta_v1_bp)
    app.register_blueprint(cer_v1_bp)
    app.register_blueprint(combustibles_v1_bp)
    app.register_blueprint(construccion_v1_bp)
    app.register_blueprint(icl_v1_bp)
    app.register_blueprint(uva_v1_bp)
    app.register_blueprint(uvi_v1_bp)
    app.register_blueprint(rios_v1_bp)
    app.register_blueprint(personas_desaparecidas_v1_bp)
    app.register_blueprint(provincias_v1_bp)
    app.register_blueprint(medicamentos_v1_bp)
    app.register_blueprint(riesgo_pais_v1_bp)
    app.register_blueprint(diputados_v1_bp)
    app.register_blueprint(rios_comahue_v1_bp)
    app.register_blueprint(dolares_v1_bp)