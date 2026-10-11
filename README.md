# Marisqueiras da Ilha

Modelagem orientada a objetos e testes unitários do sistema **Marisqueiras da Ilha** — projeto da disciplina de Programação Orientada a Objetos (docente: Aline Maya).

O sistema apoia a comercialização direta de mariscos entre **empresas de marisqueiras** (fornecedoras) e **empresas compradoras**, no modelo **B2B**. Não há atendimento a consumidor final.

---

## Sobre o projeto

Este repositório contém:

- **Modelagem POO** das classes do domínio (`MODELAGEM_POO.md`)
- **Implementação** das classes em Python (`marisqueiras.py`)
- **Testes unitários** que validam a modelagem contra as regras de negócio (`tests/`)

O foco é a **modelagem** — os testes servem como especificação executável das regras de negócio (RN01 a RN23) definidas no documento-base da disciplina.

---

## Estrutura

```text
.
├── marisqueiras.py              # Classes do sistema
├── MODELAGEM_POO.md             # Documento de modelagem (classes, relações, restrições)
├── pytest.ini                   # Configuração do pytest
├── requirements.txt             # Dependências do projeto
├── README.md                    # Este arquivo
└── tests/
    ├── conftest.py              # Fixtures compartilhadas
    ├── test_produto.py
    ├── test_empresa_marisqueira.py
    ├── test_empresa_compradora.py
    ├── test_pedido.py
    ├── test_fluxo_pedido.py
    └── test_avaliacao.py
```

---

## Classes

| Classe | Papel |
|---|---|
| `EmpresaMarisqueira` | Fornecedora. Cadastra produtos, analisa pedidos, realiza a entrega. |
| `EmpresaCompradora` | Compradora. Consulta produtos, realiza pedidos, avalia marisqueiras. |
| `Produto` | Produto oferecido por uma marisqueira. |
| `Pedido` | Pedido de compra realizado por uma empresa compradora. |
| `ItemPedido` | Entidade associativa entre `Pedido` e `Produto`. |
| `Avaliacao` | Avaliação (1 a 5 estrelas) de uma marisqueira por uma compradora. |

Detalhes de atributos, métodos e relações em [`MODELAGEM_POO.md`](MODELAGEM_POO.md).

---

## Requisitos

- Python 3.9 ou superior
- pytest (instalado via `requirements.txt`)

Instalação das dependências:

```bash
python -m pip install -r requirements.txt
```

---

## Como rodar os testes

Na raiz do repositório:

```bash
python -m pytest -v
```

Saída esperada:

```
62 passed in 0.0Xs
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

**62 testes · todos verdes.**

| Arquivo | Testes | Cobre |
|---|---|---|
| `test_produto.py` | 10 | Cadastro, mínimo de 25 kg, fresco/congelado, estoque zerado |
| `test_empresa_marisqueira.py` | 4 | Alterar quantidade, estoque, visibilidade dos próprios produtos |
| `test_empresa_compradora.py` | 9 | Consulta, filtros, ordenação, comparação |
| `test_pedido.py` | 15 | Itens, mínimo por item, disponibilidade, preço por empresa |
| `test_fluxo_pedido.py` | 9 | Ciclo receber → aceitar/rejeitar/ajustar → entrega |
| `test_avaliacao.py` | 15 | Escala 1–5, registrar nota, validações |

---

## Regras de negócio cobertas

| RN | Descrição | Onde é validada |
|---|---|---|
| RN04 | Venda por quilograma | `test_produto.py` |
| RN05 | Mínimo de 25 kg por produto | `test_produto.py`, `test_pedido.py` |
| RN06 | Fresco e congelado são produtos diferentes | `test_produto.py` |
| RN07 | Preço fixo durante a venda | `test_pedido.py` |
| RN08 | Quantidade disponível pode ser alterada | `test_produto.py`, `test_empresa_marisqueira.py` |
| RN09 | Estoque zero → produto permanece indisponível | `test_produto.py` |
| RN10 | Busca por nome, categoria, localização, empresa | `test_empresa_compradora.py` |
| RN11 | Ordenação por preço | `test_empresa_compradora.py` |
| RN12 | Visibilidade restrita / comparação | `test_empresa_marisqueira.py`, `test_empresa_compradora.py` |
| RN13 | Campos obrigatórios do pedido | `test_pedido.py` |
| RN14 | Um pedido = uma marisqueira | `test_pedido.py` |
| RN15 | 25 kg por item do pedido | `test_pedido.py` |
| RN16 | Sem valor financeiro mínimo | `test_pedido.py` |
| RN17 | Sem quantidade máxima fixa | `test_pedido.py` |
| RN18 | Bloqueia quantidade acima do disponível | `test_pedido.py` |
| RN19 | Empresa permanece cadastrada sem estoque | `test_empresa_marisqueira.py` |
| RN21 | Avaliação de 1 a 5 estrelas | `test_avaliacao.py` |
| RN22 | Entrega pela marisqueira, sem rastreamento | `test_fluxo_pedido.py` |
| RN23 | Custo da entrega embutido no preço | `test_pedido.py` |

RN01, RN02, RN03 e RN20 são restrições organizacionais / de apresentação e não têm teste unitário associado nesta modelagem.

---

## Fluxo do pedido

```
pendente → recebido → em preparo → em curso → finalizado
                ↓
          rejeitado | ajuste solicitado
```

Os estados `em preparo`, `em curso` e `finalizado` vêm do PDF da disciplina. Os demais são decisões de modelagem documentadas em `MODELAGEM_POO.md`.

---

## Decisões de modelagem em aberto

Alguns pontos foram resolvidos por decisão de modelagem (marcados com ⚠️ em `MODELAGEM_POO.md`) e podem ser revistos:

- `Pedido` guarda referência ao comprador (associação).
- `Avaliacao` guarda referência à marisqueira (associação).
- Estados extras em `status_pedido` para suportar `rejeitar_pedido` e `solicitar_ajuste`.
- Registro global de produtos (`_REGISTRO_PRODUTOS`) para viabilizar a consulta de produtos de várias marisqueiras.

---

## Licença

Projeto acadêmico — uso educacional.