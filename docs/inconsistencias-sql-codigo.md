# Inconsistências entre script SQL, banco e código

Levantamento feito nas Fases 0 a 5. A fonte da verdade do schema é
`backend/database/create_database.sql`; `backend/migracoes.py` reconstrói, na
inicialização (`init_db`), qualquer tabela cujo `CREATE` armazenado divirja do script,
com backup `fixtruck.db.bak-AAAAMMDDHHMMSS` antes de alterar.

Verificação automática: `backend/tests/test_fase5_filtros_consistencia.py`
(colunas e `NOT NULL` dos models = banco criado pelo script; tabelas do script;
enums do SQL = `constantes.py`; seed dentro do enum; placas do seed válidas).

| # | Inconsistência encontrada | Correção | Onde |
|---|---|---|---|
| 0 | `create_database.sql` estava vazio; o schema real vinha de `db.create_all()` (models) mais `ALTER TABLE` avulsos em `database.py`, e o banco versionado tinha sido criado por uma versão ainda mais antiga | Script SQL passou a ser a fonte da verdade, executado por `init_db`; migração alinha bancos antigos | Fase 1 |
| 1 | Campo `ativa`: o model tinha só `default=1` do lado Python (sem `DEFAULT` no banco), e o seed inseria oficinas por SQL puro sem a coluna; numa instalação nova as oficinas ficavam com `ativa = NULL` e a busca (`WHERE ativa=1`) não retornava nenhuma | `ativa INTEGER NOT NULL DEFAULT 1 CHECK (0,1)` no SQL e `server_default='1'` no model | Fase 1 |
| 2 | Banco antigo usava `hora_abertura`/`hora_fechamento`; o código novo usa `horarios` (JSON por dia) e `aberta_24h` | Migração converte os horários legados | `migracoes._aplicar_horarios_legados` |
| 3 | `oficinas` sem `cidade`, `uf`, `empresa_id`, `criado_em` | Colunas adicionadas; `empresa_id` com `ON DELETE SET NULL` | script SQL |
| 4 | `motoristas` sem `email`, `senha`, `trocar_senha` (login do motorista) | Colunas adicionadas (`email UNIQUE`) | Fase 3 |
| 5 | `ocorrencias` sem `descricao` e `registrada_por` | Colunas adicionadas (`registrada_por` com CHECK empresa/motorista) | Fase 3 |
| 6 | Status `encerrada` em dados antigos; o código só conhece `aberta`, `em_atendimento`, `resolvido` | Migração converte `encerrada` em `resolvido`; CHECK no SQL | `_antes_de_reconstruir` |
| 7 | Tipo de problema `pneu` nos dados e nas especialidades; o enum do código usa `borracharia` | Enum único em `constantes.py` e CHECK no SQL; migração converte `pneu` em `borracharia` (4 ocorrências no banco real) | Fase 4 |
| 8 | Placa sem normalização e sem `UNIQUE` (mesma placa podia ser cadastrada com hífen/minúsculas) | `placa TEXT NOT NULL UNIQUE`; normalização (maiúsculas, sem hífen/espaço) no código e na migração; duplicadas cancelam a migração sem alterar nada | Fase 4 |
| 9 | FKs declaradas sem `ON DELETE` e `PRAGMA foreign_keys` desligado (FKs não eram aplicadas) | `ON DELETE CASCADE/SET NULL` e `ON UPDATE CASCADE` em todas as FKs; PRAGMA ligado em toda conexão (SQLAlchemy e sqlite3) | Fase 4 |
| 10 | Sem `CHECK` para `tipo_veiculo`, `status`, `pane_total`, `ativo`, `qtd_caminhoes` | CHECKs adicionados | Fase 4 |
| 11 | Recuperação de senha devolvia o token na resposta, sem expiração persistida nem uso único | Tabela `tokens_recuperacao` (só hash SHA-256, expiração, uso único) | Fase 4 |
| 12 | Referências órfãs possíveis em colunas anuláveis | Migração anula referências para linhas inexistentes antes de ligar as FKs | `_corrigir_referencias_orfas` |
| 13 | Relatório "por mês" fazia `GROUP BY mes ORDER BY o.data_abertura` (coluna não agregada: ordem indefinida no SQLite, o `LIMIT 6` podia cortar meses recentes) | `ORDER BY MAX(o.data_abertura) DESC` | Fase 5 |
| 14 | Atalhos 7/30/90d comparavam com `datetime('now')` (UTC), mas `data_abertura` é gravada no horário de São Paulo (diferença de 3 h nos limites) | Limites calculados em Python com `agora_sao_paulo` | Fase 5 |

## Itens mantidos (apenas sinalizados)

- **Tabela `orcamentos`**: existe no banco real (4 linhas) e não está no script nem no código.
  Orçamentos estão fora do escopo; a tabela é preservada pela migração, sem uso.
- **Especialidade `freios`** na oficina "Hidráulica & Freios SP" (vinda do seed original):
  não pertence ao enum de problemas.
  Mantida como texto (não é apagada); não casa com nenhum tipo de problema na busca.
  O rótulo do tipo `hidráulica` é "Hidráulica / Freios".
- **`backend/fixtruck.db` versionado**: recomendável removê-lo do Git e gerar o banco com o seed.
