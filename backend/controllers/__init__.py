from .auth_controller import auth_bp
from .dashboard_controller import dashboard_bp
from .ocorrencia_controller import ocorrencia_bp
from .orcamento_controller import orcamento_bp
from .frota_controller import frota_bp
from .oficina_controller import oficina_bp
from .relatorio_controller import relatorio_bp
from .perfil_controller import perfil_bp


def registrar_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ocorrencia_bp)
    app.register_blueprint(orcamento_bp)
    app.register_blueprint(frota_bp)
    app.register_blueprint(oficina_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(perfil_bp)
