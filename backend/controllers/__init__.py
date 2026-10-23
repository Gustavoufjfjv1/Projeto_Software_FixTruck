from .auth_controller import auth_bp
from .dashboard_controller import dashboard_bp
from .ocorrencia_controller import ocorrencia_bp
from .frota_controller import frota_bp
from .oficina_controller import oficina_bp
from .relatorio_controller import relatorio_bp
from .perfil_controller import perfil_bp
from .opcoes_controller import opcoes_bp


def registrar_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ocorrencia_bp)
    app.register_blueprint(frota_bp)
    app.register_blueprint(oficina_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(opcoes_bp)
