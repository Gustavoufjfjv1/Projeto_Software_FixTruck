# Diagrama de classes do domínio FixTruck

O diagrama representa as entidades SQLAlchemy em `backend/models/` e seus vínculos por chaves estrangeiras. Os métodos CRUD comuns são herdados de `ModeloBase`.

```mermaid
classDiagram
    class ModeloBase {
        <<abstract>>
        +salvar()
        +atualizar()
        +deletar()
        +listar_todos()
        +buscar_por_id(id)
        +to_dict(extras)
    }

    class Empresa {
        +int id
        +string nome
        +string email
        +string senha
        +int qtd_caminhoes
        +datetime criado_em
    }

    class Motorista {
        +int id
        +int empresa_id
        +string nome
        +string cnh
        +string telefone
        +int ativo
    }

    class Veiculo {
        +int id
        +int empresa_id
        +string placa
        +string modelo
        +string marca
        +string tipo_veiculo
        +int motorista_id
    }

    class Oficina {
        +int id
        +string nome
        +string endereco
        +string telefone
        +float lat
        +float lon
        +string cnae
        +string especialidades
        +string tipos_veiculo
        +int tem_guincho
        +string hora_abertura
        +string hora_fechamento
        +int ativa
    }

    class Ocorrencia {
        +int id
        +int empresa_id
        +int motorista_id
        +int veiculo_id
        +string tipo_veiculo
        +string tipo_problema
        +int pane_total
        +string lat
        +string lon
        +string endereco
        +string status
        +int oficina_id
        +string motivo_resolucao
        +string observacoes
        +string data_abertura
        +string data_reabertura
        +string data_encerramento
        +string data_vinculacao
    }

    class Favorito {
        +int id
        +int empresa_id
        +int oficina_id
    }

    ModeloBase <|-- Empresa
    ModeloBase <|-- Motorista
    ModeloBase <|-- Veiculo
    ModeloBase <|-- Oficina
    ModeloBase <|-- Ocorrencia
    ModeloBase <|-- Favorito

    Empresa "1" o-- "0..*" Motorista : possui
    Empresa "1" o-- "0..*" Veiculo : possui
    Empresa "1" o-- "0..*" Ocorrencia : registra
    Motorista "0..1" <-- "0..*" Veiculo : conduz
    Motorista "0..1" <-- "0..*" Ocorrencia : reporta
    Veiculo "0..1" <-- "0..*" Ocorrencia : envolvido
    Oficina "0..1" <-- "0..*" Ocorrencia : atende
    Empresa "1" <-- "0..*" Favorito : pertence
    Oficina "1" <-- "0..*" Favorito : marcada
    Empresa "0..*" -- "0..*" Oficina : favorita por meio de Favorito
```

## Relacionamentos e semântica

- **Herança:** todas as entidades concretas herdam de `ModeloBase`, que fornece as operações CRUD compartilhadas.
- **Agregação:** empresa e oficina são ligadas aos registros relacionados pelas chaves estrangeiras. A exclusão de registros referenciados é protegida pelas regras dos Services, não por exclusão em cascata.
- **Associação:** motorista, veículo, ocorrência e oficina se relacionam conforme as chaves estrangeiras opcionais mostradas no diagrama. `Favorito` é a classe associativa entre `Empresa` e `Oficina`, com unicidade para o par.
- **Composição:** não há composição forte implementada no esquema atual; a remoção de uma empresa, veículo, motorista ou oficina não apaga automaticamente registros dependentes.
