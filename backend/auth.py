from functools import wraps
from flask import request, jsonify, g, current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

PAPEL_EMPRESA = 'empresa'
PAPEL_MOTORISTA = 'motorista'
VALIDADE_TOKEN = 60 * 60 * 24 * 7


def _serializer(papel=PAPEL_EMPRESA):
    # Salts diferentes: um token de motorista nunca é aceito como token de empresa (e vice-versa).
    salt = 'fixtruck-auth' if papel == PAPEL_EMPRESA else 'fixtruck-auth-motorista'
    return URLSafeTimedSerializer(current_app.secret_key, salt=salt)


def gerar_token(empresa_id, empresa_nome):
    return _serializer().dumps({'empresa_id': empresa_id, 'empresa_nome': empresa_nome, 'papel': PAPEL_EMPRESA})


def validar_token(token, max_age=VALIDADE_TOKEN):
    try:
        return _serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def _serializer_recuperacao():
    return URLSafeTimedSerializer(current_app.secret_key, salt='fixtruck-recuperacao-senha')


def gerar_token_recuperacao(empresa_id):
    return _serializer_recuperacao().dumps({'empresa_id': empresa_id})


def validar_token_recuperacao(token, max_age=60 * 30):
    try:
        return _serializer_recuperacao().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def _versao_senha(senha_hash):
    # Trocar a senha invalida tokens antigos do motorista.
    return (senha_hash or '')[-12:]


def gerar_token_motorista(motorista):
    return _serializer(PAPEL_MOTORISTA).dumps({
        'motorista_id': motorista.id,
        'empresa_id': motorista.empresa_id,
        'papel': PAPEL_MOTORISTA,
        'sv': _versao_senha(motorista.senha),
    })


def validar_token_motorista(token, max_age=VALIDADE_TOKEN):
    try:
        return _serializer(PAPEL_MOTORISTA).loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def _token_da_requisicao():
    auth = request.headers.get('Authorization', '')
    token = auth[7:] if auth.startswith('Bearer ') else None
    return token or request.cookies.get('fixtruck_token')


def login_required(f):
    """Rotas da empresa (gestor). Token de motorista recebe 403."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _token_da_requisicao()
        data = validar_token(token) if token else None
        if not data:
            if token and validar_token_motorista(token):
                return jsonify({'erro': 'Acesso restrito à empresa. Motoristas não acessam esta área.'}), 403
            return jsonify({'erro': 'Não autenticado'}), 401
        g.papel = PAPEL_EMPRESA
        g.empresa_id = data['empresa_id']
        g.empresa_nome = data['empresa_nome']
        return f(*args, **kwargs)
    return decorated


def motorista_required(f=None, permitir_troca_pendente=False):
    """Rotas do motorista. Confere no banco se o acesso continua válido a cada requisição."""
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            from models import Motorista
            token = _token_da_requisicao()
            data = validar_token_motorista(token) if token else None
            if not data:
                if token and validar_token(token):
                    return jsonify({'erro': 'Esta área é exclusiva para motoristas.'}), 403
                return jsonify({'erro': 'Não autenticado'}), 401
            motorista = Motorista.buscar_por_id(data['motorista_id'])
            if (not motorista or not motorista.ativo or not motorista.tem_acesso()
                    or motorista.empresa_id != data['empresa_id']
                    or _versao_senha(motorista.senha) != data.get('sv')):
                return jsonify({'erro': 'Sessão inválida. Faça login novamente.'}), 401
            if motorista.trocar_senha and not permitir_troca_pendente:
                return jsonify({'erro': 'Troque sua senha antes de continuar.', 'trocar_senha': True}), 403
            g.papel = PAPEL_MOTORISTA
            g.motorista = motorista
            g.motorista_id = motorista.id
            g.empresa_id = motorista.empresa_id
            return func(*args, **kwargs)
        return decorated
    return decorator(f) if f else decorator
