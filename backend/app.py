import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, g, request, send_from_directory
from database import init_db
from controllers import registrar_blueprints


def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'), static_url_path='')
    app.secret_key = os.environ.get('FIXTRUCK_SECRET', 'fixtruck-secret-2024')

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
    def close_db(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

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
    init_db()
    app.run(debug=True, port=5000)
