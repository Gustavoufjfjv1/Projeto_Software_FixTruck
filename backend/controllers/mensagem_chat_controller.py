from flask import Blueprint, redirect, render_template, request, url_for
from models import MensagemChat, db

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("/ocorrencia/<int:ocorrencia_id>")
def listar_mensagens_ocorrencia(ocorrencia_id):
    mensagens = MensagemChat.query.filter_by(ocorrencia_id=ocorrencia_id).all()
    return render_template("chat/historico.html", mensagens=mensagens, ocorrencia_id=ocorrencia_id)

@chat_bp.route("/enviar", methods=["POST"])
def enviar_mensagem():
    nova = MensagemChat(
        texto=request.form.get("texto"),
        tipo_remetente=request.form.get("tipo_remetente"),
        remetente_id=int(request.form.get("remetente_id")),
        ocorrencia_id=int(request.form.get("ocorrencia_id")),
        url_foto=request.form.get("url_foto")
    )
    db.session.add(nova)
    db.session.commit()
    return redirect(url_for("chat.listar_mensagens_ocorrencia", ocorrencia_id=nova.ocorrencia_id))

@chat_bp.route("/<int:id>/editar", methods=["POST"])
def atualizar_mensagem(id):
    mensagem = MensagemChat.query.get_or_404(id)
    mensagem.texto = request.form.get("texto")
    db.session.commit()
    return redirect(url_for("chat.listar_mensagens_ocorrencia", ocorrencia_id=mensagem.ocorrencia_id))

@chat_bp.route("/<int:id>/deletar", methods=["POST"])
def deletar_mensagem(id):
    mensagem = MensagemChat.query.get_or_404(id)
    id_ocorrencia = mensagem.ocorrencia_id
    db.session.delete(mensagem)
    db.session.commit()
    return redirect(url_for("chat.listar_mensagens_ocorrencia", ocorrencia_id=id_ocorrencia))