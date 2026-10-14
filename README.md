# Marisqueiras da Ilha

Modelagem orientada a objetos e testes unitários do sistema **Marisqueiras da Ilha** — projeto da disciplina de Programação Orientada a Objetos (docente: Aline Maya).

O sistema apoia a comercialização direta de mariscos entre **empresas de marisqueiras** (fornecedoras) e **empresas compradoras**, no modelo **B2B**. Não há atendimento a consumidor final.

---

## Sobre o projeto

Este repositório contém:

- **Modelagem POO** das classes do domínio (`MODELAGEM_POO.md`)
- **Implementação** das classes em Python (pacote `marisqueiras/`)
- **Testes unitários** que validam a modelagem contra as regras de negócio (`tests/`)

O foco é a **modelagem** — os testes servem como especificação executável das regras de negócio (RN01 a RN23) definidas no documento-base da disciplina.

---

## Estrutura

```text
.
├── marisqueiras/                # Pacote com as classes do sistema
│   ├── __init__.py              # Reexporta as classes públicas
│   ├── enums.py                 # CategoriaProduto, StatusPedido, StatusEmpresa
│   ├── excecoes.py              # RegraNegocioError, QuantidadeMinimaError, EstoqueInsuficienteError
│   ├── empresa.py               # Empresa (classe base)
│   ├── empresa_marisqueira.py   # EmpresaMarisqueira
│   ├── empresa_compradora.py    # EmpresaCompradora
│   ├── produto.py               # Produto
│   ├── item_pedido.py           # ItemPedido
│   ├── pedido.py                # Pedido
│   └── avaliacao.py             # Avaliacao
├── tests/                       # Suíte de testes
│   ├── conftest.py              # Fixtures compartilhadas
│   ├── test_produto.py
│   ├── test_empresa_marisqueira.py
│   ├── test_empresa_compradora.py
│   ├── test_pedido.py
│   ├── test_avaliacao.py
│   └── test_fluxo_pedido.py
├── MODELAGEM_POO.md             # Documento de modelagem
├── pytest.ini                   # Configuração do pytest
├── requirements.txt             # Dependências
└── README.md                    # Este arquivo
```

---

## Classes

| Classe | Papel |
|---|---|
| `Empresa` | Classe-base. Identidade, responsável e horário de funcionamento. |
| `EmpresaMarisqueira` | Fornecedora. Cadastra produtos, analisa pedidos, realiza a entrega, atualiza status. |
| `EmpresaCompradora` | Compradora. Consulta produtos, realiza pedidos, avalia marisqueiras. |
| `Produto` | Produto oferecido por uma marisqueira. |
| `ItemPedido` | Entidade associativa entre `Pedido` e `Produto`. |
| `Pedido` | Pedido de compra realizado por uma empresa compradora. |
| `Avaliacao` | Avaliação (1 a 5 estrelas) de uma marisqueira por uma compradora. |

Detalhes de atributos, métodos, relações e restrições em [`MODELAGEM_POO.md`](MODELAGEM_POO.md).

---

## Requisitos

- Python 3.9 ou superior
- pytest (declarado em `requirements.txt`)

Instalação das dependências:

```bash
python -m pip install -r requirements.txt
```

---

## Como rodar os testes

Na raiz do repositório:

```bash
python -m pytest tests/ -v
```

> **Dica:** use sempre `python -m pytest` em vez de só `pytest`. Em alguns ambientes (como o Windows do laboratório), o executável `pytest.exe` fica numa pasta fora do `PATH` e o comando isolado falha com `command not found`. O `python -m pytest` invoca o módulo diretamente e funciona sempre.

Saída esperada:

```
67 passed in 0.1Xs
```

Rodar só um arquivo:

```bash
python -m pytest tests/test_produto.py -v
python -m pytest tests/test_pedido.py -v
```

Rodar só os testes que falharam por último:

```bash
python -m pytest --lf
```

---

## Suíte de testes

**67 testes · todos verdes.**

| Arquivo | Testes | Cobre |
|---|---|---|
| `test_produto.py` | 10 | Cadastro (P15), fresco/congelado (RN06), estoque alterável (RN08), estoque zerado (RN09) |
| `test_empresa_marisqueira.py` | 16 | Indicador visual (RN20), aceitar/rejeitar/ajustar pedido, transições de status de entrega (RN22) |
| `test_empresa_compradora.py` | 16 | Consulta, filtros, ordenação (RN10–RN11), comparação (RN12), realizar pedido (RN13–RN18) |
| `test_pedido.py` | 12 | ItemPedido (RN05, RN07, RN15, RN17, RN18), Pedido (RN13, RN14, RN22) |
| `test_avaliacao.py` | 11 | Avaliação só após compra (RN21), escala 1–5 (P24), média |
| `test_fluxo_pedido.py` | 2 | Integração ponta a ponta (P7): consulta → pedido → aceite → entrega → avaliação |
| **Total** | **67** | |

---

## Regras de negócio cobertas

| RN | Descrição | Onde é validada |
|---|---|---|
| RN04 | Venda por quilograma | `test_produto.py` |
| RN05 | Mínimo de 25 kg por produto (na **venda**) | `test_pedido.py` |
| RN06 | Fresco e congelado são produtos diferentes | `test_produto.py` |
| RN07 | Preço fixo durante a venda | `test_pedido.py` |
| RN08 | Quantidade disponível pode ser alterada | `test_produto.py` |
| RN09 | Estoque zero → produto permanece indisponível | `test_produto.py` |
| RN10 | Busca por nome, categoria, localização, empresa | `test_empresa_compradora.py` |
| RN11 | Ordenação por preço, avaliação, proximidade | `test_empresa_compradora.py` |
| RN12 | Visibilidade restrita / comparação | `test_empresa_compradora.py` |
| RN13 | Campos obrigatórios do pedido | `test_pedido.py`, `test_empresa_compradora.py` |
| RN14 | Um pedido = uma marisqueira | `test_empresa_compradora.py` |
| RN15 | 25 kg por item do pedido | `test_pedido.py`, `test_empresa_compradora.py` |
| RN16 | Sem valor financeiro mínimo | `test_empresa_compradora.py` |
| RN17 | Sem quantidade máxima fixa | `test_empresa_compradora.py` |
| RN18 | Bloqueia quantidade acima do disponível | `test_pedido.py`, `test_empresa_compradora.py` |
| RN19 | Empresa permanece cadastrada sem estoque | `test_produto.py` |
| RN20 | Indicador visual (verde/laranja/vermelho) | `test_empresa_marisqueira.py` |
| RN21 | Avaliação de 1 a 5 estrelas, só após compra | `test_avaliacao.py` |
| RN22 | Entrega pela marisqueira, sem rastreamento em tempo real | `test_empresa_marisqueira.py`, `test_fluxo_pedido.py` |
| RN23 | Custo da entrega embutido no preço | `test_pedido.py` (por omissão — não há campo de frete) |

RN01, RN02 e RN03 são restrições organizacionais e não têm teste unitário associado — são garantidas pela própria estrutura (B2B, uma empresa por habitação, marisqueira autônoma).

---

## Fluxo do pedido

O `Pedido` tem **dois atributos independentes**:

**Análise (`aceito`)** — controlada pela `EmpresaMarisqueira`:

```
None (pendente) ──aceitar_pedido──▶ True  (aceito)
                └─rejeitar_pedido─▶ False (rejeitado)
```

**Entrega (`status`)** — só avança após o aceite:

```
None ──aceitar_pedido──▶ EM_PREPARO ──▶ EM_CURSO ──▶ FINALIZADO
```

- `solicitar_ajuste` **não muda** nenhum dos dois — apenas grava `mensagem_ajuste`.
- `atualizar_status_entrega` só é permitido se `aceito is True` (RN22).
- Não é possível voltar atrás em nenhuma transição.

Os três estados de entrega (`EM_PREPARO`, `EM_CURSO`, `FINALIZADO`) vêm diretamente do PDF da disciplina. O `aceito` booleano é decisão de modelagem para suportar `aceitar_pedido` / `rejeitar_pedido` sem inventar estados extras.

---

## Decisões de modelagem

1. **`Pedido` guarda referências às duas empresas** — `empresa_compradora` e `empresa_marisqueira` são atributos do construtor, atendendo RN13 e RN14.
2. **`Avaliacao` guarda referências às duas empresas** — atendendo RN21 / P23.
3. **`aceitar_pedido()` e `rejeitar_pedido()` ficam em `EmpresaMarisqueira`** — é ela quem analisa o pedido.
4. **Apenas 3 estados de entrega** — o aceite é um booleano à parte, não um estado do enum (RN22).
5. **`solicitar_ajuste()` existe** — está na lista oficial de métodos do PDF.
6. **`realizar_pedido` recebe lista de `(produto, quantidade)`** — já valida tudo de uma vez (RN14, RN15, RN18) antes de instanciar o `Pedido`.
7. **`consultar_produtos` recebe a lista de produtos por parâmetro** — sem registro global nem repositório.
8. **RN05 é regra de venda, não de cadastro** — `Produto` aceita qualquer quantidade ≥ 0; o mínimo de 25 kg só é validado no `ItemPedido`.
9. **RN20 implementada** — `status_visual` retorna verde / laranja / vermelho.
10. **RN07 garantida por congelamento do preço** — `ItemPedido.preco_unitario` guarda o preço no momento da compra.
11. **RN23 garantida por omissão** — o custo da entrega está embutido em `Produto.preco`; não há campo de frete separado.

---

## Licença

Projeto acadêmico — uso educacional.

---