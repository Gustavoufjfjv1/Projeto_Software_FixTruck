# Diagrama de classes — FixTruck

Gerado a partir do código em `backend/` (models, repositories, services e controllers).
Os diagramas usam Mermaid `classDiagram` e são renderizados direto no GitHub/GitLab
e no VS Code/Cursor com extensão de Mermaid.

Convenções: `+` público, `-` privado (prefixo `_` no Python), `$` estático
(`@staticmethod`/`@classmethod`). Tipos seguem as colunas do SQLite.

## 1. Modelo de domínio (models SQLAlchemy)

Cada model corresponde a uma tabela de `backend/database/create_database.sql`.
As multiplicidades e as regras de exclusão vêm das chaves estrangeiras do script.

```mermaid
classDiagram
    direction LR

    class ModeloBase {
        <<abstract>>
        +salvar() ModeloBase
        +atualizar() ModeloBase
        +deletar() None
        +listar_todos()$ list
        +buscar_por_id(id_)$ ModeloBase
        +to_dict(extras) dict
    }

    class Empresa {
        +int id
        +str nome
        +str email
        +str senha
        +int qtd_caminhoes
        +datetime criado_em
        +to_dict_publico() dict
    }

    class Motorista {
        +int id
        +int empresa_id
        +str nome
        +str cnh
        +str telefone
        +int ativo
        +str email
        +str senha
        +int trocar_senha
        +tem_acesso() bool
        +to_dict(extras) dict
        +to_dict_publico() dict
    }

    class Veiculo {
        +int id
        +int empresa_id
        +str placa
        +str modelo
        +str marca
        +str tipo_veiculo
        +int motorista_id
    }

    class Oficina {
        +int id
        +str nome
        +str endereco
        +str cidade
        +str uf
        +str telefone
        +float lat
        +float lon
        +str especialidades
        +str tipos_veiculo
        +int tem_guincho
        +int aberta_24h
        +str horarios
        +int ativa
        +int empresa_id
        +datetime criado_em
        +lista_especialidades() list
        +lista_tipos_veiculo() list
        +horarios_dict() dict
        +to_dict(extras) dict
    }

    class Ocorrencia {
        +int id
        +int empresa_id
        +int motorista_id
        +int veiculo_id
        +str tipo_veiculo
        +str tipo_problema
        +int pane_total
        +str descricao
        +str lat
        +str lon
        +str endereco
        +str status
        +int oficina_id
        +str motivo_resolucao
        +str observacoes
        +str data_abertura
        +str data_encerramento
        +str data_vinculacao
        +str registrada_por
    }

    class Favorito {
        +int id
        +int empresa_id
        +int oficina_id
    }

    class TokenRecuperacao {
        <<tabela tokens_recuperacao>>
        +int id
        +int empresa_id
        +str token_hash
        +datetime expira_em
        +datetime usado_em
        +datetime criado_em
    }

    ModeloBase <|-- Empresa
    ModeloBase <|-- Motorista
    ModeloBase <|-- Veiculo
    ModeloBase <|-- Oficina
    ModeloBase <|-- Ocorrencia
    ModeloBase <|-- Favorito

    Empresa "1" *-- "0..*" Motorista : emprega (CASCADE)
    Empresa "1" *-- "0..*" Veiculo : possui (CASCADE)
    Empresa "1" *-- "0..*" Ocorrencia : registra (CASCADE)
    Empresa "1" *-- "0..*" Favorito : marca (CASCADE)
    Empresa "1" *-- "0..*" TokenRecuperacao : recupera senha (CASCADE)
    Empresa "0..1" o-- "0..*" Oficina : cadastrou (SET NULL)
    Motorista "0..1" o-- "0..*" Veiculo : dirige (SET NULL)
    Motorista "0..1" o-- "0..*" Ocorrencia : envolvido (SET NULL)
    Veiculo "0..1" o-- "0..*" Ocorrencia : sofreu (SET NULL)
    Oficina "0..1" o-- "0..*" Ocorrencia : atendeu (SET NULL)
    Oficina "1" *-- "0..*" Favorito : favoritada (CASCADE)
```

Enumerações (CHECK no SQL e listas em `backend/constantes.py`):

| Campo | Valores |
|---|---|
| `Ocorrencia.tipo_problema` | mecânica, elétrica, hidráulica, borracharia, não identificado |
| `tipo_veiculo` (Veiculo, Ocorrencia) | leve, médio, pesado |
| `Ocorrencia.status` | aberta, em_atendimento, resolvido |
| `Ocorrencia.registrada_por` | empresa, motorista |

`TokenRecuperacao` não tem model SQLAlchemy: é acessado apenas por
`TokenRecuperacaoRepository` (SQL puro) e guarda só o hash SHA-256 do token.

## 2. Recomendação de oficinas (WorkshopMatcher)

Módulo puro, sem acesso a banco (`backend/services/workshop_matcher.py`).
Recebe dicionários de oficina (vindos de `OficinaRepository`) e os critérios da ocorrência.

```mermaid
classDiagram
    direction LR

    class CriteriosBusca {
        <<dataclass>>
        +str tipo_problema
        +str tipo_veiculo
        +bool pane_total
        +float lat
        +float lon
        +float raio_km
        +datetime quando
        +int janela_minutos
        +set favoritos
        +tem_localizacao bool
    }

    class WorkshopMatcher {
        +avaliar(oficina, criterios) dict
        +chave_ordenacao(of)$ tuple
        +motivo_principal(avaliadas)$ str
        +detalhe(motivo, criterios)$ str
        +mensagem(motivo, criterios)$ str
        +recomendar(oficinas, criterios) dict
    }

    class BuscarOficinasParaOcorrenciaService {
        +executar(empresa_id, ocorrencia_id, raio, janela, quando) dict
    }

    class OficinaRepository {
        +listar_ativas(busca)$ list
        +listar_da_empresa(empresa_id)$ list
        +contar_ativas()$ int
        +buscar_duplicada(nome, endereco, ignorar_id)$ Oficina
        +ids_favoritos(empresa_id)$ set
        +listar_com_contexto(empresa_id, busca, raio, lat, lon)$ list
    }

    class horarios {
        <<módulo>>
        +agora_sao_paulo() datetime
        +esta_aberta(horarios, aberta_24h, quando) bool
        +minutos_para_abrir(horarios, aberta_24h, quando, limite_minutos) int
        +resumo_horarios(horarios, aberta_24h) str
    }

    class utils {
        <<módulo>>
        +haversine(lat1, lon1, lat2, lon2) float
    }

    BuscarOficinasParaOcorrenciaService --> OficinaRepository : carrega oficinas e favoritos
    BuscarOficinasParaOcorrenciaService --> CriteriosBusca : monta a partir da ocorrência
    BuscarOficinasParaOcorrenciaService --> WorkshopMatcher : recomendar()
    WorkshopMatcher ..> CriteriosBusca : usa
    WorkshopMatcher ..> horarios : aberta agora / janela
    WorkshopMatcher ..> utils : distância
```

Ordem dos critérios eliminatórios: inativa, problema, veículo, guincho (pane total),
horário e raio. Sem compatíveis, `recomendar` devolve `motivo`, `mensagem`, `detalhe`
e até 5 alternativas rotuladas como não compatíveis.

## 3. Camadas: fluxo de ocorrências

Padrão usado em todo o backend: Controller (Blueprint Flask) chama um Service por caso
de uso; o Service valida (`validacoes`, `posse`), lança `ServiceError(mensagem, status)`
e usa Models (CRUD SQLAlchemy) e Repositories (consultas em SQL puro).

```mermaid
classDiagram
    direction TB

    class OcorrenciaController {
        +listar()
        +form_data()
        +criar()
        +detalhe(ocorrencia_id)
        +editar(ocorrencia_id)
        +buscar_oficinas(ocorrencia_id)
        +encerrar(ocorrencia_id)
        +atualizar_status(ocorrencia_id)
        +vincular_oficina(ocorrencia_id)
    }

    class MotoristaController {
        +login()
        +me()
        +trocar_senha()
        +form_data()
        +listar()
        +criar()
        +detalhe(ocorrencia_id)
        +buscar_oficinas(ocorrencia_id)
    }

    class RelatorioController {
        +obter()
    }

    class RegistrarOcorrenciaService {
        +executar(empresa_id, dados, motorista) dict
    }
    class ListarOcorrenciasService {
        +executar(empresa_id, filtros) dict
    }
    class EncerrarOcorrenciaService {
        +executar(empresa_id, ocorrencia_id, dados) dict
    }
    class VincularOficinaOcorrenciaService {
        +executar(empresa_id, ocorrencia_id, dados) dict
    }
    class GerarRelatorioService {
        +executar(empresa_id, filtros) dict
    }

    class OcorrenciaRepository {
        +listar_por_empresa(empresa_id, filtros)$ list
        +listar_do_motorista(motorista_id, empresa_id, apenas_abertas)$ list
        +buscar_detalhe(ocorrencia_id, empresa_id)$ dict
        +buscar_da_empresa(ocorrencia_id, empresa_id)$ Ocorrencia
        +contar_total(empresa_id, filtros)$ int
        +contar_por_status(empresa_id, status, filtros)$ int
        +tempo_medio_resolucao(empresa_id, filtros)$ float
        +agregados_relatorio(empresa_id, filtros)$ dict
    }

    class dados_ocorrencia {
        <<módulo>>
        +extrair_dados_ocorrencia(empresa_id, dados, motorista) dict
    }

    class posse {
        <<módulo>>
        +veiculo_da_empresa(valor, empresa_id, obrigatorio) Veiculo
        +motorista_da_empresa(valor, empresa_id, obrigatorio) Motorista
        +oficina_disponivel(valor, permitir_id) Oficina
    }

    class validacoes {
        <<módulo>>
        +texto(valor, rotulo, obrigatorio, max_len, min_len) str
        +placa(valor) str
        +coordenadas(lat, lon, obrigatorio) tuple
        +opcao(valor, permitidas, rotulo, obrigatorio) str
        +intervalo_datas(inicio, fim) tuple
    }

    class ServiceError {
        +str mensagem
        +int status
    }

    OcorrenciaController --> RegistrarOcorrenciaService
    OcorrenciaController --> ListarOcorrenciasService
    OcorrenciaController --> EncerrarOcorrenciaService
    OcorrenciaController --> VincularOficinaOcorrenciaService
    MotoristaController --> RegistrarOcorrenciaService : motorista=atual
    RelatorioController --> GerarRelatorioService

    RegistrarOcorrenciaService ..> dados_ocorrencia
    dados_ocorrencia ..> posse
    dados_ocorrencia ..> validacoes
    EncerrarOcorrenciaService ..> posse
    EncerrarOcorrenciaService ..> validacoes
    VincularOficinaOcorrenciaService ..> posse
    ListarOcorrenciasService --> OcorrenciaRepository
    GerarRelatorioService --> OcorrenciaRepository
    GerarRelatorioService ..> ListarOcorrenciasService : validar_periodo()

    EncerrarOcorrenciaService ..> ServiceError : 404 / 409
    posse ..> ServiceError : 403 / 422
    validacoes ..> ServiceError : 422
```

Os demais controllers seguem o mesmo padrão: `AuthController`, `FrotaController`,
`OficinaController`, `PerfilController`, `DashboardController` e `OpcoesController`
(ver `backend/controllers/`), cada um com seus Services em `backend/services/`.
