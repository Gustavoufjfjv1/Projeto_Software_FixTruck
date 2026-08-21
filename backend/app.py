import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from database import db, init_db, DATABASE_URI
from controllers import registrar_blueprints


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'),
        static_url_path='',
    )
    app.secret_key = os.environ.get('FIXTRUCK_SECRET', 'fixtruck-secret-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
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
        init_db()
    app.run(debug=True, port=5000)
