from flask import Blueprint, redirect, render_template, request, url_for
from models import Ocorrencia, db

ocorrencia_bp = Blueprint("ocorrencias", __name__, url_prefix="/ocorrencias")

@ocorrencia_bp.route("/")
def index():
    ocorrencias = Ocorrencia.query.all()
    return render_template("ocorrencia/lista.html", ocorrencias=ocorrencias)

@ocorrencia_bp.route("/abrir", methods=["GET", "POST"])
def abrir_ocorrencia():
    if request.method == "POST":
        nova = Ocorrencia(
            status="Aberto",
            latitude=float(request.form.get("latitude")),
            longitude=float(request.form.get("longitude")),
            observacao=request.form.get("observacao"),
            empresa_id=int(request.form.get("empresa_id")),
            motorista_id=request.form.get("motorista_id"),
            veiculo_id=request.form.get("veiculo_id")
        )
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for("ocorrencias.index"))
    return render_template("ocorrencia/formulario.html")

@ocorrencia_bp.route("/<int:id>")
def obter_ocorrencia(id):
    ocorrencia = Ocorrencia.query.get_or_404(id)
    downtime = ocorrencia.calcularDowntime()
    return render_template("ocorrencia/detalhes.html", ocorrencia=ocorrencia, downtime=downtime)

@ocorrencia_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def atualizar_ocorrencia(id):
    ocorrencia = Ocorrencia.query.get_or_404(id)
    if request.method == "POST":
        ocorrencia.latitude = float(request.form.get("latitude"))
        ocorrencia.longitude = float(request.form.get("longitude"))
        ocorrencia.observacao = request.form.get("observacao")
        db.session.commit()
        return redirect(url_for("ocorrencias.obter_ocorrencia", id=ocorrencia.id))
    return render_template("ocorrencia/formulario.html", ocorrencia=ocorrencia)

@ocorrencia_bp.route("/<int:id>/deletar", methods=["POST"])
def deletar_ocorrencia(id):
    ocorrencia = Ocorrencia.query.get_or_404(id)
    db.session.delete(ocorrencia)
    db.session.commit()
    return redirect(url_for("ocorrencias.index"))

@ocorrencia_bp.route("/<int:id>/encerrar", methods=["POST"])
def registrar_encerramento(id):
    ocorrencia = Ocorrencia.query.get_or_404(id)
    ocorrencia.encerrarOcorrencia(obs=request.form.get("observacao"))
    return redirect(url_for("ocorrencias.obter_ocorrencia", id=ocorrencia.id))

@ocorrencia_bp.route("/<int:id>/vincular-oficina", methods=["POST"])
def vincular_oficina(id):
    ocorrencia = Ocorrencia.query.get_or_404(id)
    # implementar depois
    db.session.commit()
    return redirect(url_for("ocorrencias.obter_ocorrencia", id=ocorrencia.id))