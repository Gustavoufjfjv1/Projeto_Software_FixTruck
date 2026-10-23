# Roteiro do vídeo de demonstração (até 5 minutos)

Preparação antes de gravar:

- Instalação limpa já testada (ver README). Para gravar a instalação, use um banco novo:
  `FIXTRUCK_DB=/tmp/fixtruck-video.db python app.py` (o banco real não é tocado).
- Navegador com permissão de localização liberada para `http://127.0.0.1:5000`.
- Duas abas: uma para a empresa e outra (anônima) para o motorista, porque cada papel
  guarda o próprio token no navegador.

Credenciais demo (criadas pelo seed):

| Papel | E-mail | Senha |
|---|---|---|
| Empresa | `demo@fixtruck.com` | `123456` |
| Motorista | `carlos@fixtruck.com` | `motorista123` |

| Tempo | Cena | O que mostrar e falar |
|---|---|---|
| 0:00–0:40 | Instalação | Terminal: `python -m venv venv`, ativar, `pip install -r requirements.txt`, `cd backend`, `python app.py`. Mostrar a linha "Banco pronto em ... — 54 oficinas ativas." (script SQL + seed automáticos). Rodar os testes rapidamente (`python -m unittest discover -s tests -t .`) e mostrar o "OK". |
| 0:40–1:05 | Login da empresa | `http://127.0.0.1:5000` → Entrar → `demo@fixtruck.com` / `123456`. Mostrar o dashboard em uma frase. |
| 1:05–1:40 | Cadastro de oficina | Menu "Cadastro de oficinas" → nova oficina com especialidades, tipos de veículo, guincho e horário por dia. Mostrar que oficinas do catálogo são só leitura e que é possível desativar a própria oficina (ela some da busca). |
| 1:40–2:00 | Login do motorista | Aba anônima → "Entrar como motorista" → `carlos@fixtruck.com` / `motorista123`. Mostrar o painel com o veículo vinculado. |
| 2:00–2:50 | Ocorrência com GPS | "Nova ocorrência" → tipo de problema, descrição, "Usar minha localização atual" (endereço preenchido automaticamente). Comentar a alternativa: se o GPS for negado, a tela abre o preenchimento manual (rodovia/cidade ou coordenadas). Registrar. |
| 2:50–3:30 | Busca compatível | Lista de oficinas compatíveis ordenadas por distância, com mapa e selos (compatível, guincho, aberta agora). Explicar os critérios: problema, veículo, guincho em pane total, horário e raio. |
| 3:30–4:00 | Caso sem compatíveis | Reduzir o raio para 5 km (ou registrar pane total em local sem oficina com guincho): mostrar a mensagem com o motivo e as alternativas rotuladas "Não compatível". |
| 4:00–4:30 | Filtro por datas | Aba da empresa → Ocorrências → Período "Intervalo de datas…" → escolher início e fim → Aplicar; combinar com tipo de problema. Mostrar o selo "via motorista" na ocorrência registrada pelo Carlos. Abrir Relatórios com o mesmo intervalo. |
| 4:30–5:00 | Encerramento | Abrir a ocorrência → Encerrar → oficina utilizada, motivo e observações → Confirmar. Mostrar o status "Resolvido" e, no painel do motorista (filtro "Todas"), a ocorrência encerrada. |

Observação: orçamentos (envio, aprovação ou rejeição) estão fora do escopo e não aparecem no vídeo.
