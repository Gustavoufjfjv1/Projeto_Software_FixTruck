from flask import Blueprint, redirect, render_template, request, url_for
from models import Motorista, db

motorista_bp = Blueprint("motoristas", __name__, url_prefix="/motoristas")

@motorista_bp.route("/")
def index():
    motoristas = Motorista.query.all()
    return render_template("motorista/lista.html", motoristas=motoristas)

@motorista_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar_motorista():
    if request.method == "POST":
        novo = Motorista(
            nome=request.form.get("nome"),
            email=request.form.get("email"),
            senha=request.form.get("senha"),
            empresa_id=request.form.get("empresa_id"),
            cnh=request.form.get("cnh")
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("motoristas.index"))
    return render_template("motorista/formulario.html")

@motorista_bp.route("/<int:id>")
def obter_motorista(id):
    motorista = Motorista.query.get_or_404(id)
    return render_template("motorista/detalhes.html", motorista=motorista)

@motorista_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def atualizar_motorista(id):
    motorista = Motorista.query.get_or_404(id)
    if request.method == "POST":
        motorista.nome = request.form.get("nome")
        motorista.email = request.form.get("email")
        motorista.cnh = request.form.get("cnh")
        db.session.commit()
        return redirect(url_for("motoristas.obter_motorista", id=motorista.id))
    return render_template("motorista/formulario.html", motorista=motorista)

@motorista_bp.route("/<int:id>/deletar", methods=["POST"])
def deletar_motorista(id):
    motorista = Motorista.query.get_or_404(id)
    db.session.delete(motorista)
    db.session.commit()
    return redirect(url_for("motoristas.index"))

@motorista_bp.route("/<int:id>/acionar-socorro", methods=["POST"])
def acionar_socorro(id):
    motorista = Motorista.query.get_or_404(id)
    #implementar depois
    return redirect(url_for("ocorrencias.index"))