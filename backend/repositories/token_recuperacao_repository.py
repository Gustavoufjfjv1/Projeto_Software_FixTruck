from database import get_db


class TokenRecuperacaoRepository:
    """Tokens de recuperação de senha (somente o hash é guardado). Datas em UTC."""

    @staticmethod
    def contar_recentes(empresa_id, desde):
        return get_db().execute(
            'SELECT COUNT(*) AS c FROM tokens_recuperacao WHERE empresa_id=? AND criado_em >= ?',
            (empresa_id, desde),
        ).fetchone()['c']

    @staticmethod
    def invalidar_da_empresa(empresa_id, agora):
        get_db().execute(
            'UPDATE tokens_recuperacao SET usado_em=? WHERE empresa_id=? AND usado_em IS NULL',
            (agora, empresa_id),
        )

    @staticmethod
    def criar(empresa_id, token_hash, expira_em, agora):
        db = get_db()
        db.execute(
            'INSERT INTO tokens_recuperacao (empresa_id, token_hash, expira_em, criado_em) VALUES (?,?,?,?)',
            (empresa_id, token_hash, expira_em, agora),
        )
        db.commit()

    @staticmethod
    def consumir(token_hash, agora):
        """Marca o token como usado se ainda for válido; devolve empresa_id ou None (uso único, atômico)."""
        db = get_db()
        row = db.execute(
            'SELECT id, empresa_id FROM tokens_recuperacao '
            'WHERE token_hash=? AND usado_em IS NULL AND expira_em > ?',
            (token_hash, agora),
        ).fetchone()
        if not row:
            return None
        cur = db.execute(
            'UPDATE tokens_recuperacao SET usado_em=? WHERE id=? AND usado_em IS NULL', (agora, row['id'])
        )
        if cur.rowcount != 1:
            db.rollback()
            return None
        db.execute(
            'UPDATE tokens_recuperacao SET usado_em=? WHERE empresa_id=? AND usado_em IS NULL',
            (agora, row['empresa_id']),
        )
        db.commit()
        return row['empresa_id']
