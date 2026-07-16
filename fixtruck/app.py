from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, get_db
from datetime import datetime
import math

app = Flask(__name__)
app.secret_key = 'fixtruck-secret-2024'

STATUS_ABERTOS = ('aberta', 'em_atendimento')
STATUS_RESOLVIDO = 'resolvido'


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def oficina_aberta_agora(hora_abertura, hora_fechamento):
    agora = datetime.now()
    try:
        h_ab, m_ab = map(int, (hora_abertura or '08:00').split(':')[:2])
        h_fe, m_fe = map(int, (hora_fechamento or '18:00').split(':')[:2])
    except (ValueError, AttributeError):
        h_ab, m_ab, h_fe, m_fe = 8, 0, 18, 0
    minutos_agora = agora.hour * 60 + agora.minute
    minutos_ab = h_ab * 60 + m_ab
    minutos_fe = h_fe * 60 + m_fe
    if minutos_ab == minutos_fe:
        return True
    if minutos_ab < minutos_fe:
        return minutos_ab <= minutos_agora < minutos_fe
    return minutos_agora >= minutos_ab or minutos_agora < minutos_fe


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'empresa_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def index():
    if 'empresa_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        qtd_caminhoes = request.form.get('qtd_caminhoes', 0)
        db = get_db()
        existing = db.execute('SELECT id FROM empresas WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('Email já cadastrado.', 'error')
            return render_template('cadastro.html')
        db.execute('INSERT INTO empresas (nome, email, senha, qtd_caminhoes) VALUES (?,?,?,?)',
                   (nome, email, senha, qtd_caminhoes))
        db.commit()
        flash('Cadastro realizado! Faça login.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        db = get_db()
        empresa = db.execute('SELECT * FROM empresas WHERE email=? AND senha=?', (email, senha)).fetchone()
        if empresa:
            session['empresa_id'] = empresa['id']
            session['empresa_nome'] = empresa['nome']
            return redirect(url_for('dashboard'))
        flash('Email ou senha incorretos.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    empresa_id = session['empresa_id']
    ocorrencias_abertas = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status IN ('aberta','em_atendimento')",
        (empresa_id,)).fetchone()['c']
    total_ocorrencias = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=?", (empresa_id,)).fetchone()['c']
    orcamentos_pendentes = db.execute(
        """SELECT COUNT(*) as c FROM orcamentos o
           JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
           WHERE oc.empresa_id=? AND o.status='pendente'""",
        (empresa_id,)).fetchone()['c']
    tempo_medio = db.execute(
        """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
           FROM ocorrencias WHERE empresa_id=? AND status=? AND data_encerramento IS NOT NULL""",
        (empresa_id, STATUS_RESOLVIDO)).fetchone()['avg']
    problema_comum = db.execute(
        """SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=?
           GROUP BY tipo_problema ORDER BY c DESC LIMIT 1""", (empresa_id,)).fetchone()
    recentes = db.execute(
        """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa
           FROM ocorrencias o
           LEFT JOIN oficinas of ON o.oficina_id = of.id
           LEFT JOIN veiculos v ON o.veiculo_id = v.id
           WHERE o.empresa_id=? ORDER BY o.data_abertura DESC LIMIT 5""",
        (empresa_id,)).fetchall()
    abertas_list = db.execute(
        """SELECT o.*, v.placa as veiculo_placa FROM ocorrencias o
           LEFT JOIN veiculos v ON o.veiculo_id = v.id
           WHERE o.empresa_id=? AND o.status IN ('aberta','em_atendimento')
           ORDER BY o.data_abertura DESC LIMIT 5""",
        (empresa_id,)).fetchall()
    return render_template('dashboard.html',
                           ocorrencias_abertas=ocorrencias_abertas,
                           total_ocorrencias=total_ocorrencias,
                           orcamentos_pendentes=orcamentos_pendentes,
                           tempo_medio=round(tempo_medio, 0) if tempo_medio else 0,
                           problema_comum=problema_comum['tipo_problema'] if problema_comum else '-',
                           recentes=recentes,
                           abertas_list=abertas_list)


@app.route('/ocorrencias')
@login_required
def ocorrencias():
    db = get_db()
    empresa_id = session['empresa_id']
    filtro_periodo = request.args.get('periodo', '')
    filtro_tipo = request.args.get('tipo', '')
    filtro_veiculo = request.args.get('veiculo', '')
    filtro_status = request.args.get('status', '')
    query = """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa, m.nome as motorista_nome
               FROM ocorrencias o
               LEFT JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON o.veiculo_id = v.id
               LEFT JOIN motoristas m ON o.motorista_id = m.id
               WHERE o.empresa_id=?"""
    params = [empresa_id]
    if filtro_tipo:
        query += " AND o.tipo_problema=?"
        params.append(filtro_tipo)
    if filtro_veiculo:
        query += " AND o.veiculo_id=?"
        params.append(filtro_veiculo)
    if filtro_status == 'abertas':
        query += " AND o.status IN ('aberta','em_atendimento')"
    elif filtro_status:
        query += " AND o.status=?"
        params.append(filtro_status)
    if filtro_periodo == '7d':
        query += " AND o.data_abertura >= datetime('now', '-7 days')"
    elif filtro_periodo == '30d':
        query += " AND o.data_abertura >= datetime('now', '-30 days')"
    elif filtro_periodo == '90d':
        query += " AND o.data_abertura >= datetime('now', '-90 days')"
    query += " ORDER BY o.data_abertura DESC"
    ocorrencias_list = db.execute(query, params).fetchall()
    veiculos = db.execute(
        "SELECT id, placa, modelo FROM veiculos WHERE empresa_id=? ORDER BY placa",
        (empresa_id,)).fetchall()
    return render_template('ocorrencias.html', ocorrencias=ocorrencias_list,
                           veiculos=veiculos,
                           filtro_periodo=filtro_periodo, filtro_tipo=filtro_tipo,
                           filtro_veiculo=filtro_veiculo, filtro_status=filtro_status)


@app.route('/ocorrencias/abertas')
@login_required
def ocorrencias_abertas():
    return redirect(url_for('ocorrencias', status='abertas'))


@app.route('/ocorrencias/encerradas')
@login_required
def ocorrencias_encerradas():
    return redirect(url_for('ocorrencias', status=STATUS_RESOLVIDO))


@app.route('/ocorrencias/nova', methods=['GET', 'POST'])
@login_required
def nova_ocorrencia():
    db = get_db()
    empresa_id = session['empresa_id']
    veiculos = db.execute(
        """SELECT v.*, m.nome as motorista_nome FROM veiculos v
           LEFT JOIN motoristas m ON v.motorista_id = m.id
           WHERE v.empresa_id=? ORDER BY v.placa""",
        (empresa_id,)).fetchall()
    motoristas = db.execute(
        "SELECT * FROM motoristas WHERE empresa_id=? AND ativo=1 ORDER BY nome",
        (empresa_id,)).fetchall()
    if request.method == 'POST':
        veiculo_id = request.form.get('veiculo_id') or None
        motorista_id = request.form.get('motorista_id') or None
        tipo_problema = request.form['tipo_problema']
        pane_total = 1 if request.form.get('pane_total') else 0
        lat = request.form.get('lat', '')
        lon = request.form.get('lon', '')
        endereco = request.form.get('endereco', '')
        if not lat or not lon:
            flash('Informe a localização via GPS para registrar a ocorrência.', 'error')
            return render_template('nova_ocorrencia.html', veiculos=veiculos, motoristas=motoristas)
        tipo_veiculo = request.form.get('tipo_veiculo', 'pesado')
        if veiculo_id:
            veiculo = db.execute(
                "SELECT * FROM veiculos WHERE id=? AND empresa_id=?",
                (veiculo_id, empresa_id)).fetchone()
            if veiculo:
                tipo_veiculo = veiculo['tipo_veiculo']
                if not motorista_id and veiculo['motorista_id']:
                    motorista_id = veiculo['motorista_id']
        db.execute(
            """INSERT INTO ocorrencias (empresa_id, motorista_id, veiculo_id, tipo_veiculo, tipo_problema,
               pane_total, lat, lon, endereco, status, data_abertura)
               VALUES (?,?,?,?,?,?,?,?,?,'aberta',datetime('now','localtime'))""",
            (empresa_id, motorista_id, veiculo_id, tipo_veiculo, tipo_problema,
             pane_total, lat, lon, endereco or f'GPS: {lat}, {lon}'))
        db.commit()
        oc = db.execute("SELECT last_insert_rowid() as id").fetchone()['id']
        flash('Ocorrência registrada com localização GPS.', 'success')
        return redirect(url_for('buscar_oficinas', ocorrencia_id=oc))
    return render_template('nova_ocorrencia.html', veiculos=veiculos, motoristas=motoristas)


@app.route('/ocorrencias/<int:ocorrencia_id>/buscar-oficinas')
@login_required
def buscar_oficinas(ocorrencia_id):
    db = get_db()
    oc = db.execute("SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?",
                    (ocorrencia_id, session['empresa_id'])).fetchone()
    if not oc:
        return redirect(url_for('ocorrencias'))
    raio = request.args.get('raio', type=float)
    oficinas_raw = db.execute("SELECT * FROM oficinas WHERE ativa=1").fetchall()
    oficinas = []
    for of in oficinas_raw:
        of_dict = dict(of)
        if oc['lat'] and oc['lon']:
            try:
                dist = haversine(float(oc['lat']), float(oc['lon']), of['lat'], of['lon'])
                of_dict['distancia'] = round(dist, 1)
            except (TypeError, ValueError):
                of_dict['distancia'] = None
        else:
            of_dict['distancia'] = None
        if raio is not None and of_dict['distancia'] is not None and of_dict['distancia'] > raio:
            continue
        of_dict['aberta_agora'] = oficina_aberta_agora(of['hora_abertura'], of['hora_fechamento'])
        of_dict['atende_tipo'] = oc['tipo_problema'].lower() in (of['especialidades'] or '').lower()
        of_dict['atende_veiculo'] = oc['tipo_veiculo'].lower() in (of['tipos_veiculo'] or '').lower()
        fav = db.execute("SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?",
                         (session['empresa_id'], of['id'])).fetchone()
        of_dict['favoritada'] = fav is not None
        oficinas.append(of_dict)
    if oc['pane_total']:
        oficinas.sort(key=lambda x: (not x.get('tem_guincho', False), x['distancia'] or 9999))
    else:
        oficinas.sort(key=lambda x: (x['distancia'] or 9999))
    return render_template('buscar_oficinas.html', ocorrencia=oc, oficinas=oficinas, raio=raio)


@app.route('/ocorrencias/<int:ocorrencia_id>/encerrar', methods=['GET', 'POST'])
@login_required
def encerrar_ocorrencia(ocorrencia_id):
    db = get_db()
    oc = db.execute("SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?",
                    (ocorrencia_id, session['empresa_id'])).fetchone()
    if not oc:
        return redirect(url_for('ocorrencias'))
    if oc['status'] == STATUS_RESOLVIDO:
        flash('Esta ocorrência já está resolvida.', 'error')
        return redirect(url_for('ocorrencias'))
    if request.method == 'POST':
        oficina_id = request.form.get('oficina_id')
        motivo = request.form.get('motivo', '')
        observacoes = request.form.get('observacoes', '')
        if not oficina_id:
            flash('Selecione uma oficina para encerrar a ocorrência.', 'error')
            oficinas = db.execute("SELECT * FROM oficinas WHERE ativa=1").fetchall()
            return render_template('encerrar_ocorrencia.html', ocorrencia=oc, oficinas=oficinas)
        db.execute(
            """UPDATE ocorrencias SET status=?, oficina_id=?, motivo_resolucao=?,
               observacoes=?, data_encerramento=datetime('now','localtime') WHERE id=?""",
            (STATUS_RESOLVIDO, oficina_id, motivo, observacoes, ocorrencia_id))
        db.commit()
        flash('Ocorrência encerrada com status resolvido.', 'success')
        return redirect(url_for('ocorrencias', status=STATUS_RESOLVIDO))
    oficinas = db.execute("SELECT * FROM oficinas WHERE ativa=1").fetchall()
    return render_template('encerrar_ocorrencia.html', ocorrencia=oc, oficinas=oficinas)


@app.route('/ocorrencias/<int:ocorrencia_id>/status', methods=['POST'])
@login_required
def atualizar_status(ocorrencia_id):
    db = get_db()
    novo_status = request.form.get('status')
    if novo_status in ['aberta', 'em_atendimento']:
        db.execute("UPDATE ocorrencias SET status=? WHERE id=? AND empresa_id=?",
                   (novo_status, ocorrencia_id, session['empresa_id']))
        db.commit()
    return redirect(url_for('ocorrencias'))


@app.route('/ocorrencias/<int:ocorrencia_id>/vincular-oficina', methods=['POST'])
@login_required
def vincular_oficina(ocorrencia_id):
    db = get_db()
    oficina_id = request.form.get('oficina_id')
    oc = db.execute("SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?",
                    (ocorrencia_id, session['empresa_id'])).fetchone()
    if oc and oficina_id:
        db.execute(
            "UPDATE ocorrencias SET oficina_id=?, status='em_atendimento' WHERE id=?",
            (oficina_id, ocorrencia_id))
        db.commit()
        flash('Oficina vinculada à ocorrência.', 'success')
    return redirect(url_for('detalhe_ocorrencia', ocorrencia_id=ocorrencia_id))


@app.route('/ocorrencias/<int:ocorrencia_id>')
@login_required
def detalhe_ocorrencia(ocorrencia_id):
    db = get_db()
    oc = db.execute(
        """SELECT o.*, of.nome as oficina_nome, v.placa as veiculo_placa, v.modelo as veiculo_modelo,
                  m.nome as motorista_nome
           FROM ocorrencias o
           LEFT JOIN oficinas of ON o.oficina_id = of.id
           LEFT JOIN veiculos v ON o.veiculo_id = v.id
           LEFT JOIN motoristas m ON o.motorista_id = m.id
           WHERE o.id=? AND o.empresa_id=?""",
        (ocorrencia_id, session['empresa_id'])).fetchone()
    if not oc:
        return redirect(url_for('ocorrencias'))
    orcamentos = db.execute(
        """SELECT o.*, of.nome as oficina_nome,
                  (o.valor_pecas + o.valor_mao_obra) as total
           FROM orcamentos o
           JOIN oficinas of ON o.oficina_id = of.id
           WHERE o.ocorrencia_id=? ORDER BY o.data_envio DESC""",
        (ocorrencia_id,)).fetchall()
    oficinas = db.execute("SELECT * FROM oficinas WHERE ativa=1 ORDER BY nome").fetchall()
    return render_template('detalhe_ocorrencia.html', ocorrencia=oc,
                           orcamentos=orcamentos, oficinas=oficinas)


# ── Orçamentos ──────────────────────────────────────────────

@app.route('/orcamentos')
@login_required
def orcamentos():
    db = get_db()
    empresa_id = session['empresa_id']
    filtro = request.args.get('status', '')
    query = """SELECT o.*, of.nome as oficina_nome, oc.tipo_problema, oc.status as oc_status,
                      (o.valor_pecas + o.valor_mao_obra) as total, v.placa as veiculo_placa
               FROM orcamentos o
               JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
               JOIN oficinas of ON o.oficina_id = of.id
               LEFT JOIN veiculos v ON oc.veiculo_id = v.id
               WHERE oc.empresa_id=?"""
    params = [empresa_id]
    if filtro:
        query += " AND o.status=?"
        params.append(filtro)
    query += " ORDER BY o.data_envio DESC"
    lista = db.execute(query, params).fetchall()
    return render_template('orcamentos.html', orcamentos=lista, filtro_status=filtro)


@app.route('/orcamentos/enviar', methods=['POST'])
@login_required
def enviar_orcamento():
    """Simula envio de orçamento pela oficina vinculada à ocorrência."""
    db = get_db()
    ocorrencia_id = request.form.get('ocorrencia_id')
    oficina_id = request.form.get('oficina_id')
    valor_pecas = float(request.form.get('valor_pecas') or 0)
    valor_mao_obra = float(request.form.get('valor_mao_obra') or 0)
    descricao = request.form.get('descricao', '')
    oc = db.execute("SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?",
                    (ocorrencia_id, session['empresa_id'])).fetchone()
    if not oc:
        flash('Ocorrência não encontrada.', 'error')
        return redirect(url_for('ocorrencias'))
    db.execute(
        """INSERT INTO orcamentos (ocorrencia_id, oficina_id, valor_pecas, valor_mao_obra,
           descricao, status, data_envio)
           VALUES (?,?,?,?,?,'pendente',datetime('now','localtime'))""",
        (ocorrencia_id, oficina_id, valor_pecas, valor_mao_obra, descricao))
    if oc['status'] == 'aberta':
        db.execute("UPDATE ocorrencias SET oficina_id=?, status='em_atendimento' WHERE id=?",
                   (oficina_id, ocorrencia_id))
    db.commit()
    flash('Orçamento registrado. Aguardando aprovação do gestor.', 'success')
    return redirect(url_for('detalhe_ocorrencia', ocorrencia_id=ocorrencia_id))


@app.route('/orcamentos/<int:orcamento_id>/decidir', methods=['POST'])
@login_required
def decidir_orcamento(orcamento_id):
    db = get_db()
    decisao = request.form.get('decisao')
    orc = db.execute(
        """SELECT o.* FROM orcamentos o
           JOIN ocorrencias oc ON o.ocorrencia_id = oc.id
           WHERE o.id=? AND oc.empresa_id=?""",
        (orcamento_id, session['empresa_id'])).fetchone()
    if not orc:
        flash('Orçamento não encontrado.', 'error')
        return redirect(url_for('orcamentos'))
    if orc['status'] != 'pendente':
        flash('Este orçamento já foi decidido.', 'error')
        return redirect(url_for('detalhe_ocorrencia', ocorrencia_id=orc['ocorrencia_id']))
    if decisao == 'aprovar':
        db.execute(
            """UPDATE orcamentos SET status='aprovado', data_resposta=datetime('now','localtime')
               WHERE id=?""", (orcamento_id,))
        db.execute(
            """UPDATE ocorrencias SET oficina_id=?, status='em_atendimento' WHERE id=?""",
            (orc['oficina_id'], orc['ocorrencia_id']))
        flash('Orçamento aprovado digitalmente.', 'success')
    elif decisao == 'rejeitar':
        db.execute(
            """UPDATE orcamentos SET status='rejeitado', data_resposta=datetime('now','localtime')
               WHERE id=?""", (orcamento_id,))
        flash('Orçamento rejeitado.', 'success')
    else:
        flash('Decisão inválida.', 'error')
    db.commit()
    return redirect(url_for('detalhe_ocorrencia', ocorrencia_id=orc['ocorrencia_id']))


# ── Frota: motoristas e veículos ────────────────────────────

@app.route('/frota')
@login_required
def frota():
    db = get_db()
    empresa_id = session['empresa_id']
    veiculos = db.execute(
        """SELECT v.*, m.nome as motorista_nome FROM veiculos v
           LEFT JOIN motoristas m ON v.motorista_id = m.id
           WHERE v.empresa_id=? ORDER BY v.placa""",
        (empresa_id,)).fetchall()
    motoristas = db.execute(
        """SELECT m.*,
                  (SELECT placa FROM veiculos WHERE motorista_id=m.id LIMIT 1) as veiculo_placa
           FROM motoristas m WHERE m.empresa_id=? ORDER BY m.nome""",
        (empresa_id,)).fetchall()
    return render_template('frota.html', veiculos=veiculos, motoristas=motoristas)


@app.route('/frota/motoristas/novo', methods=['POST'])
@login_required
def novo_motorista():
    db = get_db()
    db.execute(
        "INSERT INTO motoristas (empresa_id, nome, cnh, telefone) VALUES (?,?,?,?)",
        (session['empresa_id'], request.form['nome'],
         request.form.get('cnh', ''), request.form.get('telefone', '')))
    db.commit()
    flash('Motorista cadastrado.', 'success')
    return redirect(url_for('frota'))


@app.route('/frota/veiculos/novo', methods=['POST'])
@login_required
def novo_veiculo():
    db = get_db()
    motorista_id = request.form.get('motorista_id') or None
    db.execute(
        """INSERT INTO veiculos (empresa_id, placa, modelo, marca, tipo_veiculo, motorista_id)
           VALUES (?,?,?,?,?,?)""",
        (session['empresa_id'], request.form['placa'].upper(),
         request.form.get('modelo', ''), request.form.get('marca', ''),
         request.form.get('tipo_veiculo', 'pesado'), motorista_id))
    db.commit()
    flash('Veículo cadastrado na frota.', 'success')
    return redirect(url_for('frota'))


@app.route('/frota/veiculos/<int:veiculo_id>/vincular', methods=['POST'])
@login_required
def vincular_motorista(veiculo_id):
    db = get_db()
    motorista_id = request.form.get('motorista_id') or None
    veiculo = db.execute(
        "SELECT * FROM veiculos WHERE id=? AND empresa_id=?",
        (veiculo_id, session['empresa_id'])).fetchone()
    if not veiculo:
        flash('Veículo não encontrado.', 'error')
        return redirect(url_for('frota'))
    if motorista_id:
        mot = db.execute(
            "SELECT id FROM motoristas WHERE id=? AND empresa_id=?",
            (motorista_id, session['empresa_id'])).fetchone()
        if not mot:
            flash('Motorista inválido.', 'error')
            return redirect(url_for('frota'))
    db.execute("UPDATE veiculos SET motorista_id=? WHERE id=?", (motorista_id, veiculo_id))
    db.commit()
    flash('Motorista vinculado ao veículo da frota.', 'success')
    return redirect(url_for('frota'))


# ── Oficinas ────────────────────────────────────────────────

@app.route('/oficinas')
@login_required
def oficinas():
    db = get_db()
    busca = request.args.get('busca', '')
    raio = request.args.get('raio', type=float)
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    query = "SELECT * FROM oficinas WHERE ativa=1"
    params = []
    if busca:
        query += " AND (nome LIKE ? OR especialidades LIKE ?)"
        params.extend([f'%{busca}%', f'%{busca}%'])
    query += " ORDER BY nome"
    oficinas_list = db.execute(query, params).fetchall()
    oficinas_com_fav = []
    for of in oficinas_list:
        of_dict = dict(of)
        fav = db.execute("SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?",
                         (session['empresa_id'], of['id'])).fetchone()
        of_dict['favoritada'] = fav is not None
        of_dict['aberta_agora'] = oficina_aberta_agora(of['hora_abertura'], of['hora_fechamento'])
        of_dict['distancia'] = None
        if lat is not None and lon is not None and of['lat'] and of['lon']:
            of_dict['distancia'] = round(haversine(lat, lon, of['lat'], of['lon']), 1)
            if raio is not None and of_dict['distancia'] > raio:
                continue
        oficinas_com_fav.append(of_dict)
    if lat is not None and lon is not None:
        oficinas_com_fav.sort(key=lambda x: x['distancia'] if x['distancia'] is not None else 9999)
    return render_template('oficinas.html', oficinas=oficinas_com_fav, busca=busca,
                           raio=raio, lat=lat, lon=lon)


@app.route('/oficinas/<int:oficina_id>')
@login_required
def detalhe_oficina(oficina_id):
    db = get_db()
    of = db.execute("SELECT * FROM oficinas WHERE id=?", (oficina_id,)).fetchone()
    if not of:
        return redirect(url_for('oficinas'))
    fav = db.execute("SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?",
                     (session['empresa_id'], oficina_id)).fetchone()
    aberta_agora = oficina_aberta_agora(of['hora_abertura'], of['hora_fechamento'])
    return render_template('detalhe_oficina.html', oficina=of,
                           favoritada=fav is not None, aberta_agora=aberta_agora)


@app.route('/favoritar/<int:oficina_id>', methods=['POST'])
@login_required
def favoritar(oficina_id):
    db = get_db()
    empresa_id = session['empresa_id']
    fav = db.execute("SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?",
                     (empresa_id, oficina_id)).fetchone()
    if fav:
        db.execute("DELETE FROM favoritos WHERE empresa_id=? AND oficina_id=?", (empresa_id, oficina_id))
    else:
        db.execute("INSERT INTO favoritos (empresa_id, oficina_id) VALUES (?,?)", (empresa_id, oficina_id))
    db.commit()
    next_url = request.form.get('next', url_for('oficinas'))
    return redirect(next_url)


@app.route('/relatorios')
@login_required
def relatorios():
    db = get_db()
    empresa_id = session['empresa_id']
    total = db.execute("SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=?", (empresa_id,)).fetchone()['c']
    abertas = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status='aberta'",
        (empresa_id,)).fetchone()['c']
    em_atendimento = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status='em_atendimento'",
        (empresa_id,)).fetchone()['c']
    resolvidas = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status=?",
        (empresa_id, STATUS_RESOLVIDO)).fetchone()['c']
    tempo_medio = db.execute(
        """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
           FROM ocorrencias WHERE empresa_id=? AND status=?""",
        (empresa_id, STATUS_RESOLVIDO)).fetchone()['avg']
    por_tipo = db.execute(
        "SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=? GROUP BY tipo_problema",
        (empresa_id,)).fetchall()
    por_veiculo = db.execute(
        """SELECT COALESCE(v.placa, o.tipo_veiculo) as veiculo, COUNT(*) as c
           FROM ocorrencias o LEFT JOIN veiculos v ON o.veiculo_id = v.id
           WHERE o.empresa_id=? GROUP BY veiculo""",
        (empresa_id,)).fetchall()
    por_mes = db.execute(
        """SELECT strftime('%m/%Y', data_abertura) as mes, COUNT(*) as c
           FROM ocorrencias WHERE empresa_id=?
           GROUP BY mes ORDER BY data_abertura DESC LIMIT 6""", (empresa_id,)).fetchall()
    return render_template('relatorios.html',
                           total=total, abertas=abertas, em_atendimento=em_atendimento,
                           encerradas=resolvidas,
                           tempo_medio=round(tempo_medio, 0) if tempo_medio else 0,
                           por_tipo=por_tipo, por_veiculo=por_veiculo, por_mes=por_mes)


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    db = get_db()
    empresa = db.execute("SELECT * FROM empresas WHERE id=?", (session['empresa_id'],)).fetchone()
    if request.method == 'POST':
        nome = request.form['nome']
        qtd_caminhoes = request.form.get('qtd_caminhoes', empresa['qtd_caminhoes'])
        db.execute("UPDATE empresas SET nome=?, qtd_caminhoes=? WHERE id=?",
                   (nome, qtd_caminhoes, session['empresa_id']))
        db.commit()
        session['empresa_nome'] = nome
        flash('Dados atualizados com sucesso.', 'success')
        return redirect(url_for('perfil'))
    return render_template('perfil.html', empresa=empresa)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
