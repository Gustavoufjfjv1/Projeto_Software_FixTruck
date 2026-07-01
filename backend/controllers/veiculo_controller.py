from flask import Blueprint, redirect, render_template, request, url_for
from models import Veiculo, Ocorrencia, Motorista, db

veiculo_bp = Blueprint("veiculos", __name__, url_prefix="/veiculos")

@veiculo_bp.route("/")
def index():
    veiculos = Veiculo.query.all()
    return render_template("veiculo/lista.html", veiculos=veiculos)

@veiculo_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar_veiculo():
    motoristas = Motorista.query.all()
    if request.method == "POST":
        novo = Veiculo(
            placa=request.form.get("placa"),
            modelo=request.form.get("modelo"),
            marca=request.form.get("marca"),
            motorista_id=request.form.get("motorista_id")
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("veiculos.index"))
    return render_template("veiculo/formulario.html", motoristas=motoristas)

@veiculo_bp.route("/<int:id>")
def obter_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
    return render_template("veiculo/detalhes.html", veiculo=veiculo)

@veiculo_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def atualizar_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
    motoristas = Motorista.query.all()
    if request.method == "POST":
        veiculo.placa = request.form.get("placa")
        veiculo.modelo = request.form.get("modelo")
        veiculo.marca = request.form.get("marca")
        veiculo.motorista_id = request.form.get("motorista_id")
        db.session.commit()
        return redirect(url_for("veiculos.obter_veiculo", id=veiculo.id))
    return render_template("veiculo/formulario.html", veiculo=veiculo, motoristas=motoristas)

@veiculo_bp.route("/<int:id>/deletar", methods=["POST"])
def remover_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
    db.session.delete(veiculo)
    db.session.commit()
    return redirect(url_for("veiculos.index"))

@veiculo_bp.route("/<int:id>/historico")
def obter_historico_ocorrencias(id):
    veiculo = Veiculo.query.get_or_404(id)
    ocorrencias = Ocorrencia.query.filter_by(veiculo_id=id).all()
    return render_template("veiculo/historico.html", veiculo=veiculo, ocorrencias=ocorrencias)