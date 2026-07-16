from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from database import init_db, get_db
from datetime import datetime
import math

app = Flask(__name__)
app.secret_key = 'fixtruck-secret-2024'

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

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
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    empresa_id = session['empresa_id']
    ocorrencias_abertas = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status != 'encerrada'",
        (empresa_id,)).fetchone()['c']
    total_ocorrencias = db.execute(
        "SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=?", (empresa_id,)).fetchone()['c']
    tempo_medio = db.execute(
        """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
           FROM ocorrencias WHERE empresa_id=? AND status='encerrada' AND data_encerramento IS NOT NULL""",
        (empresa_id,)).fetchone()['avg']
    problema_comum = db.execute(
        """SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=?
           GROUP BY tipo_problema ORDER BY c DESC LIMIT 1""", (empresa_id,)).fetchone()
    recentes = db.execute(
        """SELECT o.*, of.nome as oficina_nome FROM ocorrencias o
           LEFT JOIN oficinas of ON o.oficina_id = of.id
           WHERE o.empresa_id=? ORDER BY o.data_abertura DESC LIMIT 5""",
        (empresa_id,)).fetchall()
    return render_template('dashboard.html',
        ocorrencias_abertas=ocorrencias_abertas,
        total_ocorrencias=total_ocorrencias,
        tempo_medio=round(tempo_medio, 0) if tempo_medio else 0,
        problema_comum=problema_comum['tipo_problema'] if problema_comum else '-',
        recentes=recentes)

@app.route('/ocorrencias')
@login_required
def ocorrencias():
    db = get_db()
    empresa_id = session['empresa_id']
    filtro_periodo = request.args.get('periodo', '')
    filtro_tipo = request.args.get('tipo', '')
    filtro_veiculo = request.args.get('veiculo', '')
    filtro_status = request.args.get('status', '')
    query = """SELECT o.*, of.nome as oficina_nome FROM ocorrencias o
               LEFT JOIN oficinas of ON o.oficina_id = of.id
               WHERE o.empresa_id=?"""
    params = [empresa_id]
    if filtro_tipo:
        query += " AND o.tipo_problema=?"
        params.append(filtro_tipo)
    if filtro_veiculo:
        query += " AND o.tipo_veiculo=?"
        params.append(filtro_veiculo)
    if filtro_status:
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
    return render_template('ocorrencias.html', ocorrencias=ocorrencias_list,
                           filtro_periodo=filtro_periodo, filtro_tipo=filtro_tipo,
                           filtro_veiculo=filtro_veiculo, filtro_status=filtro_status)

@app.route('/ocorrencias/nova', methods=['GET', 'POST'])
@login_required
def nova_ocorrencia():
    if request.method == 'POST':
        db = get_db()
        empresa_id = session['empresa_id']
        tipo_veiculo = request.form['tipo_veiculo']
        tipo_problema = request.form['tipo_problema']
        pane_total = 1 if request.form.get('pane_total') else 0
        lat = request.form.get('lat', '')
        lon = request.form.get('lon', '')
        endereco = request.form.get('endereco', '')
        db.execute(
            """INSERT INTO ocorrencias (empresa_id, tipo_veiculo, tipo_problema, pane_total,
               lat, lon, endereco, status, data_abertura)
               VALUES (?,?,?,?,?,?,?,'aberta',datetime('now','localtime'))""",
            (empresa_id, tipo_veiculo, tipo_problema, pane_total, lat, lon, endereco))
        db.commit()
        oc = db.execute("SELECT last_insert_rowid() as id").fetchone()['id']
        return redirect(url_for('buscar_oficinas', ocorrencia_id=oc))
    return render_template('nova_ocorrencia.html')

@app.route('/ocorrencias/<int:ocorrencia_id>/buscar-oficinas')
@login_required
def buscar_oficinas(ocorrencia_id):
    db = get_db()
    oc = db.execute("SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?",
                    (ocorrencia_id, session['empresa_id'])).fetchone()
    if not oc:
        return redirect(url_for('ocorrencias'))
    oficinas_raw = db.execute("SELECT * FROM oficinas WHERE ativa=1").fetchall()
    oficinas = []
    for of in oficinas_raw:
        of_dict = dict(of)
        if oc['lat'] and oc['lon']:
            try:
                dist = haversine(float(oc['lat']), float(oc['lon']), of['lat'], of['lon'])
                of_dict['distancia'] = round(dist, 1)
            except:
                of_dict['distancia'] = None
        else:
            of_dict['distancia'] = None
        # Check if open now
        now_hour = datetime.now().hour
        abertura = int(of['hora_abertura'].split(':')[0]) if of['hora_abertura'] else 6
        fechamento = int(of['hora_fechamento'].split(':')[0]) if of['hora_fechamento'] else 18
        of_dict['aberta_agora'] = abertura <= now_hour < fechamento
        # Check specialty match
        of_dict['atende_tipo'] = oc['tipo_problema'].lower() in (of['especialidades'] or '').lower()
        # Check vehicle type
        of_dict['atende_veiculo'] = oc['tipo_veiculo'].lower() in (of['tipos_veiculo'] or '').lower()
        # Favorited
        fav = db.execute("SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?",
                         (session['empresa_id'], of['id'])).fetchone()
        of_dict['favoritada'] = fav is not None
        oficinas.append(of_dict)
    # Sort: if pane total → guincho first, then distance
    if oc['pane_total']:
        oficinas.sort(key=lambda x: (not x.get('tem_guincho', False), x['distancia'] or 9999))
    else:
        oficinas.sort(key=lambda x: (x['distancia'] or 9999))
    return render_template('buscar_oficinas.html', ocorrencia=oc, oficinas=oficinas)

@app.route('/ocorrencias/<int:ocorrencia_id>/encerrar', methods=['GET', 'POST'])
@login_required
def encerrar_ocorrencia(ocorrencia_id):
    db = get_db()
    oc = db.execute("SELECT * FROM ocorrencias WHERE id=? AND empresa_id=?",
                    (ocorrencia_id, session['empresa_id'])).fetchone()
    if not oc:
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
            """UPDATE ocorrencias SET status='encerrada', oficina_id=?, motivo_resolucao=?,
               observacoes=?, data_encerramento=datetime('now','localtime') WHERE id=?""",
            (oficina_id, motivo, observacoes, ocorrencia_id))
        db.commit()
        flash('Ocorrência encerrada com sucesso.', 'success')
        return redirect(url_for('ocorrencias'))
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

@app.route('/oficinas')
@login_required
def oficinas():
    db = get_db()
    busca = request.args.get('busca', '')
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
        now_hour = datetime.now().hour
        abertura = int(of['hora_abertura'].split(':')[0]) if of['hora_abertura'] else 6
        fechamento = int(of['hora_fechamento'].split(':')[0]) if of['hora_fechamento'] else 18
        of_dict['aberta_agora'] = abertura <= now_hour < fechamento
        oficinas_com_fav.append(of_dict)
    return render_template('oficinas.html', oficinas=oficinas_com_fav, busca=busca)

@app.route('/oficinas/<int:oficina_id>')
@login_required
def detalhe_oficina(oficina_id):
    db = get_db()
    of = db.execute("SELECT * FROM oficinas WHERE id=?", (oficina_id,)).fetchone()
    if not of:
        return redirect(url_for('oficinas'))
    fav = db.execute("SELECT id FROM favoritos WHERE empresa_id=? AND oficina_id=?",
                     (session['empresa_id'], oficina_id)).fetchone()
    now_hour = datetime.now().hour
    abertura = int(of['hora_abertura'].split(':')[0]) if of['hora_abertura'] else 6
    fechamento = int(of['hora_fechamento'].split(':')[0]) if of['hora_fechamento'] else 18
    aberta_agora = abertura <= now_hour < fechamento
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
    abertas = db.execute("SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status='aberta'", (empresa_id,)).fetchone()['c']
    em_atendimento = db.execute("SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status='em_atendimento'", (empresa_id,)).fetchone()['c']
    encerradas = db.execute("SELECT COUNT(*) as c FROM ocorrencias WHERE empresa_id=? AND status='encerrada'", (empresa_id,)).fetchone()['c']
    tempo_medio = db.execute(
        """SELECT AVG((julianday(data_encerramento) - julianday(data_abertura)) * 24 * 60) as avg
           FROM ocorrencias WHERE empresa_id=? AND status='encerrada'""", (empresa_id,)).fetchone()['avg']
    por_tipo = db.execute(
        "SELECT tipo_problema, COUNT(*) as c FROM ocorrencias WHERE empresa_id=? GROUP BY tipo_problema",
        (empresa_id,)).fetchall()
    por_veiculo = db.execute(
        "SELECT tipo_veiculo, COUNT(*) as c FROM ocorrencias WHERE empresa_id=? GROUP BY tipo_veiculo",
        (empresa_id,)).fetchall()
    por_mes = db.execute(
        """SELECT strftime('%m/%Y', data_abertura) as mes, COUNT(*) as c
           FROM ocorrencias WHERE empresa_id=?
           GROUP BY mes ORDER BY data_abertura DESC LIMIT 6""", (empresa_id,)).fetchall()
    return render_template('relatorios.html',
        total=total, abertas=abertas, em_atendimento=em_atendimento, encerradas=encerradas,
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
