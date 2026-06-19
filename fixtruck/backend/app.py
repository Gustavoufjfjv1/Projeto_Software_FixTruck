"""
Aplicação Flask principal - FixTruck
Sistema de Gestão de Ocorrências Mecânicas para Frotas Rodoviárias
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from config import config

# Carregar variáveis de ambiente do arquivo .env do backend
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Inicializar extensões
db = SQLAlchemy()

def create_app(config_name=None):
    """Factory pattern para criar a aplicação Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Carregar configuração
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Criar pasta de uploads se não existir
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Registrar blueprints
    from controllers.auth_controller import auth_bp
    from controllers.usuario_controller import usuario_bp
    from controllers.veiculo_controller import veiculo_bp
    from controllers.ocorrencia_controller import ocorrencia_bp
    from controllers.oficina_controller import oficina_bp
    from controllers.orcamento_controller import orcamento_bp
    from controllers.chat_controller import chat_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    app.register_blueprint(veiculo_bp, url_prefix='/api/veiculos')
    app.register_blueprint(ocorrencia_bp, url_prefix='/api/ocorrencias')
    app.register_blueprint(oficina_bp, url_prefix='/api/oficinas')
    app.register_blueprint(orcamento_bp, url_prefix='/api/orcamentos')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # Criar tabelas no banco de dados
    with app.app_context():
        try:
            db.create_all()
        except Exception as error:
            app.logger.error(
                'Falha ao inicializar o banco de dados. Verifique DATABASE_URL e credenciais MySQL. %s',
                error
            )
            raise RuntimeError(
                'Não foi possível conectar ao banco de dados. Verifique o valor de DATABASE_URL em backend/.env ou nas variáveis de ambiente. '
                'Exemplo: mysql+pymysql://root:password@localhost:3306/fixtruck'
            ) from error
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'FixTruck API is running'}, 200
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
