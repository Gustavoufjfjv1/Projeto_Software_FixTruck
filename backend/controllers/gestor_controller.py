from flask import Blueprint, redirect, render_template, request, url_for
from models import Gestor, Orcamento, Oficina, db

gestor_bp = Blueprint("gestores", __name__, url_prefix="/gestores")

@gestor_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar_gestor():
    if request.method == "POST":
        novo = Gestor(
            nome=request.form.get("nome"),
            email=request.form.get("email"),
            senha=request.form.get("senha"),
            empresa_id=request.form.get("empresa_id"),
            telefone=request.form.get("telefone")
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("ocorrencias.index"))
    return render_template("gestor/formulario.html")

@gestor_bp.route("/<int:id>")
def obter_gestor(id):
    gestor = Gestor.query.get_or_404(id)
    return render_template("gestor/detalhes.html", gestor=gestor)

@gestor_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def atualizar_gestor(id):
    gestor = Gestor.query.get_or_404(id)
    if request.method == "POST":
        gestor.nome = request.form.get("nome")
        gestor.email = request.form.get("email")
        gestor.telefone = request.form.get("telefone")
        db.session.commit()
        return redirect(url_for("gestores.obter_gestor", id=gestor.id))
    return render_template("gestor/formulario.html", gestor=gestor)

@gestor_bp.route("/<int:id>/deletar", methods=["POST"])
def deletar_gestor(id):
    gestor = Gestor.query.get_or_404(id)
    db.session.delete(gestor)
    db.session.commit()
    return redirect(url_for("ocorrencias.index"))

@gestor_bp.route("/<int:id>/aprovar-orcamento", methods=["POST"])
def aprovar_orcamento(id):
    Gestor.query.get_or_404(id)
    orcamento = Orcamento.query.get_or_404(request.form.get("orcamento_id"))
    orcamento.alterarStatusAprovacao("Aprovado")
    return redirect(url_for("orcamentos.visualizar_orcamento", id=orcamento.id))

@gestor_bp.route("/<int:id>/favoritar-oficina", methods=["POST"])
def favoritar_oficina(id):
    Gestor.query.get_or_404(id)
    #implementar depois
    return redirect(url_for("oficinas.obter_oficina"))