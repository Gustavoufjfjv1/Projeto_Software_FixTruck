from flask import Blueprint, redirect, render_template, request, url_for
from models import Empresa, db

empresa_bp = Blueprint("empresas", __name__, url_prefix="/empresas")

@empresa_bp.route("/cadastrar", methods=["GET", "POST"])
def criar_empresa():
    if request.method == "POST":
        nova = Empresa(
            razao_social=request.form.get("razao_social"),
            cnpj=request.form.get("cnpj"),
            endereco=request.form.get("endereco")
        )
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for("ocorrencias.index"))
    return render_template("empresa/formulario.html")

@empresa_bp.route("/<int:id>")
def obter_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    return render_template("empresa/detalhes.html", empresa=empresa)

@empresa_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def atualizar_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    if request.method == "POST":
        empresa.razao_social = request.form.get("razao_social")
        empresa.cnpj = request.form.get("cnpj")
        empresa.endereco = request.form.get("endereco")
        db.session.commit()
        return redirect(url_for("empresas.obter_empresa", id=empresa.id))
    return render_template("empresa/formulario.html", empresa=empresa)

@empresa_bp.route("/<int:id>/deletar", methods=["POST"])
def deletar_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    db.session.delete(empresa)
    db.session.commit()
    return redirect(url_for("ocorrencias.index"))

@empresa_bp.route("/<int:id>/relatorio-mensal")
def emitir_relatorio_mensal(id):
    empresa = Empresa.query.get_or_404(id)
    #implementar deps
    return render_template("empresa/relatorio_mensal.html", empresa=empresa)