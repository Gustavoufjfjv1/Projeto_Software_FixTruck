import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, g, request, send_from_directory
from database import db, init_db, DATABASE_PATH
from controllers import registrar_blueprints


def create_app(config=None):
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'),
        static_url_path='',
    )
    app.secret_key = os.environ.get('FIXTRUCK_SECRET', 'fixtruck-secret-2024')
    app.config['DATABASE_PATH'] = DATABASE_PATH
    if config:
        app.config.update(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['DATABASE_PATH']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        return response

    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            return ('', 204)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
        sqlite_db = g.pop('sqlite_db', None)
        if sqlite_db is not None:
            sqlite_db.close()

    @app.get('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'fixtruck-api'})

    registrar_blueprints(app)

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        resumo = init_db()
        print(f"Banco pronto em {resumo['caminho']} — {resumo['oficinas_ativas']} oficinas ativas.")
    app.run(debug=True, port=5000)
