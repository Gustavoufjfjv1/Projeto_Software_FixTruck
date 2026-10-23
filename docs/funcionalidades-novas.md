# Funcionalidades novas

> **Confirmar com o professor o critério do que conta como nova funcionalidade.**
> A lista abaixo considera "nova" toda funcionalidade que não existia no projeto antes
> deste ciclo de trabalho (commit `797acf4` e anteriores) e que o usuário percebe como
> um comportamento novo. Correções de bugs e refatorações internas não entram na tabela.

Regra de status: **Concluída** só quando implementada **e** coberta por teste automatizado
ou por teste manual no navegador registrado. Testes automatizados ficam em
`backend/tests/` e rodam com:

```bash
cd backend
python3 -m unittest discover -s tests -t .
```

| # | Funcionalidade nova | O que foi feito | Arquivos principais | Teste que comprova | Status |
|---|---|---|---|---|---|
| 1 | Cadastro de oficinas pela empresa | Criar, editar, ativar e desativar oficinas próprias; oficinas do catálogo (seed) são somente leitura; duplicadas recusadas (409) | `services/cadastrar_oficina_service.py`, `services/atualizar_oficina_service.py`, `controllers/oficina_controller.py`, `frontend/gerenciar_oficinas.html` | `test_fase1_cadastro_oficinas.py` (`CadastroOficinasTest`) | Concluída |
| 2 | Catálogo inicial com 54 oficinas | Seed idempotente com oficinas em várias regiões, 24 h, com guincho e horários por dia | `seed.py`, `seed_dados.py` | `test_fase1_instalacao.py` (`test_seed_tem_40_ou_mais_oficinas_em_varias_regioes`, `test_seed_idempotente`) | Concluída |
| 3 | Atualização automática e segura do banco | Bancos antigos são migrados para o script oficial na inicialização, com backup e sem perda de linhas | `migracoes.py`, `database.py`, `database/create_database.sql` | `test_fase1_instalacao.py` (`MigracaoBancoLegadoTest`), `test_fase4_validacoes.py` (`TestMigracaoFase4`) | Concluída |
| 4 | Recomendação de oficinas por compatibilidade | Só aparecem oficinas ativas que atendem o problema e o veículo, com guincho em pane total, abertas e dentro do raio; ordenadas por distância | `services/workshop_matcher.py`, `services/buscar_oficinas_para_ocorrencia_service.py`, `frontend/js/busca_oficinas.js` | `test_fase2_workshop_matcher.py` (`WorkshopMatcherTest`, `BuscaOficinasApiTest`) | Concluída |
| 5 | Explicação quando não há oficina compatível | Motivo principal (problema, veículo, guincho, horário ou raio) e até 5 alternativas rotuladas como "Não compatível" | `services/workshop_matcher.py`, `frontend/js/busca_oficinas.js` | `test_fase2_workshop_matcher.py` (`test_sem_resultados_motivo_*`, `test_alternativas_separadas_e_rotuladas`, `test_resposta_explicita_sem_compativeis`) | Concluída |
| 6 | Horário de funcionamento por dia da semana | Horários por dia, 24 h, intervalos que passam da meia-noite, no fuso de São Paulo | `horarios.py`, `models/oficina.py` | `test_fase2_workshop_matcher.py` (`HorariosTest`) | Concluída |
| 7 | Login do motorista com papel próprio | Login separado, tokens distintos por papel, isolamento entre empresas | `auth.py`, `services/acesso_motorista_service.py`, `controllers/motorista_controller.py`, `frontend/motorista_login.html` | `test_fase3_motorista.py` (`TestLoginMotorista`, `TestPapeisEIsolamento`) | Concluída |
| 8 | Acesso do motorista criado pela empresa | Empresa define e-mail e gera senha provisória; troca obrigatória no primeiro acesso | `services/acesso_motorista_service.py`, `frontend/frota.html`, `frontend/motorista_trocar_senha.html` | `test_fase3_motorista.py` (`TestAcessoDefinidoPelaEmpresa`, `TestTrocaDeSenha`) | Concluída |
| 9 | Motorista registra e acompanha ocorrências | Registro só para veículo vinculado, painel com abertas/todas, busca de oficinas compatíveis; empresa vê o selo "via motorista" | `services/registrar_ocorrencia_service.py`, `services/dados_ocorrencia.py`, `frontend/motorista_painel.html`, `frontend/motorista_nova_ocorrencia.html`, `frontend/motorista_oficinas.html` | `test_fase3_motorista.py` (`TestOcorrenciasDoMotorista`) | Concluída |
| 10 | Alternativa manual quando o GPS falha | O GPS e a geocodificação já existiam (`geo.js`); agora, se o GPS for negado, estiver indisponível ou demorar, a tela explica o motivo, abre o preenchimento manual (rodovia/cidade geocodificadas ou coordenadas) e permite tentar de novo | `frontend/js/localizacao.js`, `frontend/nova_ocorrencia.html`, `frontend/motorista_nova_ocorrencia.html` | Teste manual no navegador (Fase 5): GPS negado, indisponível, timeout e sucesso; registro com coordenadas manuais e com endereço digitado | Concluída |
| 11 | Filtro por intervalo de datas | Data inicial e final (dia final incluído) em ocorrências e relatórios, combinável com os outros filtros; mantém 7/30/90 dias | `repositories/ocorrencia_repository.py`, `services/listar_ocorrencias_service.py`, `services/gerar_relatorio_service.py`, `frontend/js/filtro_datas.js` | `test_fase5_filtros_consistencia.py` (`TestIntervaloDeDatas`, `TestRelatorioComDatas`) e teste manual no navegador | Concluída |

## Melhorias em funcionalidades que já existiam

Ficam fora da contagem acima, mas podem contar dependendo do critério do professor.

| # | Melhoria | O que foi feito | Arquivos principais | Teste que comprova | Status |
|---|---|---|---|---|---|
| M1 | Recuperação de senha segura | Antes o token voltava na resposta da API. Agora é aleatório, guardado só como hash, vale 30 min, é de uso único, há limite de pedidos e de tentativas e a resposta é igual para e-mail existente ou não | `services/recuperar_senha_service.py`, `services/redefinir_senha_service.py`, `repositories/token_recuperacao_repository.py`, `email_simulado.py` | `test_fase4_validacoes.py` (`TestRecuperacaoSenha`) | Concluída |
| M2 | Placa normalizada e única | Aceita formato antigo e Mercosul, com ou sem hífen; grava em maiúsculas; placa repetida dá 409 | `validacoes.py`, `services/cadastrar_veiculo_service.py` | `test_fase4_validacoes.py` (`TestPlaca`) | Concluída |
| M3 | Proteção de dados entre empresas | Recurso de outra empresa na URL: 404; referência de outra empresa no corpo: 403; inexistente: 422; nunca 500 | `services/posse.py`, `app.py` | `test_fase4_validacoes.py` (`TestPosse`) | Concluída |
| M4 | Integridade referencial no banco | FKs com `ON DELETE`/`ON UPDATE`, `PRAGMA foreign_keys` ligado, CHECK nos enums | `database/create_database.sql`, `database.py` | `test_fase4_validacoes.py` (`TestChavesEstrangeiras`, `TestEnumTipoProblema`) | Concluída |
| M5 | Validação de formulários | Mensagens claras (422) para campos obrigatórios, tamanhos, e-mail, telefone, CNH, coordenadas | `validacoes.py`, services de cadastro | `test_fase4_validacoes.py` (`TestFormularios`) | Concluída |
