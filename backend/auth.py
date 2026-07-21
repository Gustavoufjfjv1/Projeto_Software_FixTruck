from functools import wraps
from flask import request, jsonify, g, current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


def _serializer():
    return URLSafeTimedSerializer(current_app.secret_key, salt='fixtruck-auth')


def gerar_token(empresa_id, empresa_nome):
    return _serializer().dumps({'empresa_id': empresa_id, 'empresa_nome': empresa_nome})


def validar_token(token, max_age=60 * 60 * 24 * 7):
    try:
        return _serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        token = auth[7:] if auth.startswith('Bearer ') else None
        if not token:
            token = request.cookies.get('fixtruck_token')
        data = validar_token(token) if token else None
        if not data:
            return jsonify({'erro': 'Não autenticado'}), 401
        g.empresa_id = data['empresa_id']
        g.empresa_nome = data['empresa_nome']
        return f(*args, **kwargs)
    return decorated
