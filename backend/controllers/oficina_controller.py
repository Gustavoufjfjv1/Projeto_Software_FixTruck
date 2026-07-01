from flask import Blueprint, redirect, render_template, request, url_for
from models import Oficina, db

oficina_bp = Blueprint("oficinas", __name__, url_prefix="/oficinas")

@oficina_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar_oficina():
    if request.method == "POST":
        novo = Oficina(
            nome=request.form.get("nome"),
            email=request.form.get("email"),
            senha=request.form.get("senha"),
            nome_fantasia=request.form.get("nome_fantasia"),
            cnpj=request.form.get("cnpj"),
            especialidades=request.form.get("especialidades"),
            horario_funcionamento=request.form.get("horario_funcionamento"),
            possui_guincho=request.form.get("possui_guincho") == "true",
            atende_pesado=request.form.get("atende_pesado") == "true"
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("ocorrencias.index"))
    return render_template("oficina/formulario.html")

@oficina_bp.route("/<int:id>")
def obter_oficina(id):
    oficina = Oficina.query.get_or_404(id)
    return render_template("oficina/detalhes.html", oficina=oficina)

@oficina_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def atualizar_oficina(id):
    oficina = Oficina.query.get_or_404(id)
    if request.method == "POST":
        oficina.nome = request.form.get("nome")
        oficina.email = request.form.get("email")
        oficina.nome_fantasia = request.form.get("nome_fantasia")
        oficina.cnpj = request.form.get("cnpj")
        oficina.especialidades = request.form.get("especialidades")
        oficina.horario_funcionamento = request.form.get("horario_funcionamento")
        oficina.possui_guincho = request.form.get("possui_guincho") == "true"
        oficina.atende_pesado = request.form.get("atende_pesado") == "true"
        db.session.commit()
        return redirect(url_for("oficinas.obter_oficina", id=oficina.id))
    return render_template("oficina/formulario.html", oficina=oficina)

@oficina_bp.route("/<int:id>/deletar", methods=["POST"])
def deletar_oficina(id):
    oficina = Oficina.query.get_or_404(id)
    db.session.delete(oficina)
    db.session.commit()
    return redirect(url_for("ocorrencias.index"))

@oficina_bp.route("/<int:id>/status-atendimento", methods=["POST"])
def atualizar_status_atendimento(id):
    oficina = Oficina.query.get_or_404(id)
    # adicionar depois
    db.session.commit()
    return redirect(url_for("oficinas.obter_oficina", id=oficina.id))