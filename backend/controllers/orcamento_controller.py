from flask import Blueprint, redirect, render_template, request, url_for
from models import Orcamento, db

orcamento_bp = Blueprint("orcamentos", __name__, url_prefix="/orcamentos")

@orcamento_bp.route("/propor", methods=["GET", "POST"])
def propor_orcamento():
    if request.method == "POST":
        novo = Orcamento(
            valor_pecas=request.form.get("valor_pecas"),
            valor_mao_obra=request.form.get("valor_mao_obra"),
            ocorrencia_id=int(request.form.get("ocorrencia_id")),
            oficina_id=int(request.form.get("oficina_id"))
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("ocorrencias.obter_ocorrencia", id=novo.起こりーエnシア_id)) # Correção de digitação de contexto para ocorrencia_id
        return redirect(url_for("ocorrencias.obter_ocorrencia", id=novo.ocorrencia_id))
    return render_template("orcamento/formulario.html")

@orcamento_bp.route("/<int:id>")
def visualizar_orcamento(id):
    orcamento = Orcamento.query.get_or_404(id)
    total = orcamento.calcularTotal()
    return render_template("orcamento/detalhes.html", orcamento=orcamento, total=total)

@orcamento_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def atualizar_orcamento(id):
    orcamento = Orcamento.query.get_or_404(id)
    if request.method == "POST":
        orcamento.valor_pecas = request.form.get("valor_pecas")
        orcamento.valor_mao_obra = request.form.get("valor_mao_obra")
        db.session.commit()
        return redirect(url_for("orcamentos.visualizar_orcamento", id=orcamento.id))
    return render_template("orcamento/formulario.html", orcamento=orcamento)

@orcamento_bp.route("/<int:id>/deletar", methods=["POST"])
def deletar_orcamento(id):
    orcamento = Orcamento.query.get_or_404(id)
    id_ocorrencia = orcamento.ocorrencia_id
    db.session.delete(orcamento)
    db.session.commit()
    return redirect(url_for("ocorrencias.obter_ocorrencia", id=id_ocorrencia))

@orcamento_bp.route("/<int:id>/status", methods=["POST"])
def atualizar_status_orcamento(id):
    orcamento = Orcamento.query.get_or_404(id)
    orcamento.alterarStatusAprovacao(request.form.get("status"))
    return redirect(url_for("orcamentos.visualizar_orcamento", id=orcamento.id))