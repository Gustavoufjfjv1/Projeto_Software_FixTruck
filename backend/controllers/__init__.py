from .gestor_controller import gestor_bp
from .motorista_controller import motorista_bp
from .oficina_controller import oficina_bp
from .empresa_controller import empresa_bp
from .veiculo_controller import veiculo_bp
from .ocorrencia_controller import ocorrencia_bp
from .orcamento_controller import orcamento_bp
from .mensagem_chat_controller import chat_bp

def registrar_blueprints(app):
    app.register_blueprint(gestor_bp)
    app.register_blueprint(motorista_bp)
    app.register_blueprint(oficina_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(veiculo_bp)
    app.register_blueprint(ocorrencia_bp)
    app.register_blueprint(orcamento_bp)
    app.register_blueprint(chat_bp)