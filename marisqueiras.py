"""Modelagem POO do sistema Marisqueiras da Ilha.

Classes: EmpresaMarisqueira, EmpresaCompradora, Produto,
Pedido, ItemPedido, Avaliacao.

Modelagem conforme documento da disciplina (versão simplificada).
"""

# Registro global de produtos: permite que EmpresaCompradora consulte
# produtos de todas as marisqueiras (RN10 / RN12) sem precisar de repositório.
_REGISTRO_PRODUTOS = {}


# ============================================================
# PRODUTO
# ============================================================

class Produto:
    """Produto comercializado por uma EmpresaMarisqueira.

    RN04 - comercialização por kg (semântica da quantidade).
    RN05 - quantidade mínima de 25 kg.
    RN06 - fresco e congelado são produtos distintos.
    RN09 - quantidade zero => produto permanece cadastrado.
    """

    CATEGORIAS_VALIDAS = ("fresco", "congelado")
    QUANTIDADE_MINIMA = 25

    def __init__(self, id_produto, nome, categoria, preco,
                 quantidade_disponivel, fotografia=None, empresa=None):
        if not id_produto:
            raise ValueError("id_produto é obrigatório")
        if not nome:
            raise ValueError("nome é obrigatório")
        if categoria not in self.CATEGORIAS_VALIDAS:
            raise ValueError(f"categoria deve ser uma de {self.CATEGORIAS_VALIDAS}")
        if preco is None or preco < 0:
            raise ValueError("preco deve ser >= 0")
        if quantidade_disponivel is None or quantidade_disponivel < 0:
            raise ValueError("quantidade_disponivel deve ser >= 0")

        self.id_produto = id_produto
        self.nome = nome
        self.categoria = categoria
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel
        self.fotografia = fotografia
        self.empresa = empresa

        _REGISTRO_PRODUTOS[id_produto] = self

    def verificar_disponibilidade(self, quantidade=None):
        """Sem argumento: True se estoque > 0. Com argumento: estoque >= quantidade."""
        if quantidade is None:
            return self.quantidade_disponivel > 0
        return self.quantidade_disponivel >= quantidade

    def atualizar_quantidade(self, quantidade):
        """RN08 - atualiza a quantidade disponível."""
        if quantidade is None or quantidade < 0:
            raise ValueError("quantidade deve ser >= 0")
        self.quantidade_disponivel = quantidade

    def __repr__(self):
        return (
            f"Produto({self.id_produto}, {self.nome}, "
            f"{self.categoria}, R${self.preco}, {self.quantidade_disponivel}kg)"
        )


# ============================================================
# ITEM_PEDIDO
# ============================================================

class ItemPedido:
    """Entidade associativa entre Pedido e Produto."""

    def __init__(self, id_pedido, id_produto, quantidade):
        self.id_pedido = id_pedido
        self.id_produto = id_produto
        self.quantidade = quantidade

    def __repr__(self):
        return f"ItemPedido({self.id_pedido}, {self.id_produto}, {self.quantidade}kg)"


# ============================================================
# PEDIDO
# ============================================================

class Pedido:
    """Pedido realizado por EmpresaCompradora para uma EmpresaMarisqueira.

    RN13 - registra comprador, produtos, quantidade, endereço, tempo.
    RN14 - não reúne produtos de marisqueiras diferentes.
    RN15 - mínimo de 25 kg por item.
    RN17 - sem máximo fixo; limitado ao estoque.
    """

    STATUS_PENDENTE = "pendente"
    STATUS_RECEBIDO = "recebido"
    STATUS_PREPARO = "em preparo"
    STATUS_CURSO = "em curso"
    STATUS_FINALIZADO = "finalizado"
    STATUS_REJEITADO = "rejeitado"
    STATUS_AJUSTE = "ajuste solicitado"

    def __init__(self, id_pedido, comprador, endereco_entrega, tempo_entrega):
        if not id_pedido:
            raise ValueError("id_pedido é obrigatório")
        if comprador is None:
            raise ValueError("comprador é obrigatório")
        if not endereco_entrega:
            raise ValueError("endereco_entrega é obrigatório")
        if not tempo_entrega:
            raise ValueError("tempo_entrega é obrigatório")

        self.id_pedido = id_pedido
        self.comprador = comprador
        self.endereco_entrega = endereco_entrega
        self.tempo_entrega = tempo_entrega
        self.status_pedido = self.STATUS_PENDENTE
        self.itens = []
        self.marisqueira = None  # definida no primeiro item

    def adicionar_item(self, produto, quantidade):
        """Adiciona produto ao pedido.

        RN14 - mesma marisqueira em todos os itens.
        RN15 - quantidade mínima de 25 kg.
        RN18 - quantidade não pode ultrapassar disponibilidade.
        """
        if produto.empresa is None:
            raise ValueError("produto não está associado a uma marisqueira")

        item = ItemPedido(self.id_pedido, produto.id_produto, quantidade)
        self.validar_quantidade(item)

        if self.marisqueira is None:
            self.marisqueira = produto.empresa
        elif self.marisqueira is not produto.empresa:
            raise ValueError(
                "Um pedido não pode reunir produtos de marisqueiras diferentes (RN14)"
            )

        if quantidade > produto.quantidade_disponivel:
            raise ValueError(
                f"Quantidade indisponível: solicitado {quantidade}kg, "
                f"disponível {produto.quantidade_disponivel}kg (RN18)"
            )

        self.itens.append(item)
        return item

    def validar_quantidade(self, item):
        """RN15 - quantidade mínima de 25 kg por item."""
        if item.quantidade < Produto.QUANTIDADE_MINIMA:
            raise ValueError(
                f"Quantidade mínima por item é {Produto.QUANTIDADE_MINIMA}kg (RN15)"
            )
        return True

    def verificar_disponibilidade(self):
        """True se todos os itens têm estoque suficiente."""
        for item in self.itens:
            produto = _REGISTRO_PRODUTOS.get(item.id_produto)
            if produto is None or not produto.verificar_disponibilidade(item.quantidade):
                return False
        return True

    def __repr__(self):
        return (
            f"Pedido({self.id_pedido}, {self.status_pedido}, "
            f"{len(self.itens)} itens)"
        )


# ============================================================
# AVALIACAO
# ============================================================

class Avaliacao:
    """Avaliação de EmpresaMarisqueira por EmpresaCompradora.

    RN21 - escala de 1 a 5 estrelas.
    """

    NOTA_MINIMA = 1
    NOTA_MAXIMA = 5

    def __init__(self, id_avaliacao, nota, empresa=None):
        if not id_avaliacao:
            raise ValueError("id_avaliacao é obrigatório")
        self.id_avaliacao = id_avaliacao
        self.empresa = empresa
        self.nota = None
        self.registrar_nota(nota)

    def registrar_nota(self, nota):
        """RN21 - nota inteira entre 1 e 5."""
        if isinstance(nota, bool) or not isinstance(nota, int):
            raise ValueError("nota deve ser um número inteiro (RN21)")
        if nota < self.NOTA_MINIMA or nota > self.NOTA_MAXIMA:
            raise ValueError(
                f"nota deve estar entre {self.NOTA_MINIMA} e {self.NOTA_MAXIMA} (RN21)"
            )
        self.nota = nota
        return self.nota

    def __repr__(self):
        return f"Avaliacao({self.id_avaliacao}, {self.nota}★)"


# ============================================================
# EMPRESA_MARISQUEIRA
# ============================================================

class EmpresaMarisqueira:
    """Fornecedora. Cadastra produtos, analisa pedidos e realiza a entrega."""

    def __init__(self, id_empresa_marisqueira, CNPJ, nome, localizacao):
        if not id_empresa_marisqueira:
            raise ValueError("id_empresa_marisqueira é obrigatório")
        if not CNPJ:
            raise ValueError("CNPJ é obrigatório")
        if not nome:
            raise ValueError("nome é obrigatório")
        if not localizacao:
            raise ValueError("localizacao é obrigatória")

        self.id_empresa_marisqueira = id_empresa_marisqueira
        self.CNPJ = CNPJ
        self.nome = nome
        self.localizacao = localizacao
        self.produtos = []
        self.pedidos_recebidos = []
        self.avaliacoes_recebidas = []

    # ----- produto -----

    def cadastrar_produto(self, id_produto, nome, categoria, preco,
                          quantidade_disponivel, fotografia=None):
        """RN05 - mínimo de 25 kg no cadastro."""
        if quantidade_disponivel < Produto.QUANTIDADE_MINIMA:
            raise ValueError(
                f"Quantidade mínima no cadastro é {Produto.QUANTIDADE_MINIMA}kg (RN05)"
            )
        produto = Produto(
            id_produto=id_produto,
            nome=nome,
            categoria=categoria,
            preco=preco,
            quantidade_disponivel=quantidade_disponivel,
            fotografia=fotografia,
            empresa=self,
        )
        self.produtos.append(produto)
        return produto

    def alterar_quantidade(self, produto, quantidade):
        """RN08 - altera a quantidade disponível de um produto da marisqueira."""
        if produto not in self.produtos:
            raise ValueError("Produto não pertence a esta marisqueira")
        produto.atualizar_quantidade(quantidade)

    # ----- ciclo do pedido -----

    def receber_pedido(self, pedido):
        if pedido.marisqueira is not self:
            raise ValueError("Pedido não destinado a esta marisqueira")
        pedido.status_pedido = Pedido.STATUS_RECEBIDO
        self.pedidos_recebidos.append(pedido)

    def aceitar_pedido(self, pedido):
        if pedido.status_pedido != Pedido.STATUS_RECEBIDO:
            raise ValueError("Só é possível aceitar pedido no estado 'recebido'")
        pedido.status_pedido = Pedido.STATUS_PREPARO

    def rejeitar_pedido(self, pedido):
        if pedido.status_pedido != Pedido.STATUS_RECEBIDO:
            raise ValueError("Só é possível rejeitar pedido no estado 'recebido'")
        pedido.status_pedido = Pedido.STATUS_REJEITADO

    def solicitar_ajuste(self, pedido):
        if pedido.status_pedido != Pedido.STATUS_RECEBIDO:
            raise ValueError("Só é possível solicitar ajuste em pedido 'recebido'")
        pedido.status_pedido = Pedido.STATUS_AJUSTE

    def atualizar_status_entrega(self, pedido, status):
        """RN22 - atualiza status da entrega. Sem rastreamento em tempo real."""
        if pedido.status_pedido not in (Pedido.STATUS_PREPARO, Pedido.STATUS_CURSO):
            raise ValueError(
                "Só é possível atualizar entrega após o pedido estar em preparo"
            )
        if status not in (Pedido.STATUS_CURSO, Pedido.STATUS_FINALIZADO):
            raise ValueError(
                f"status de entrega deve ser '{Pedido.STATUS_CURSO}' "
                f"ou '{Pedido.STATUS_FINALIZADO}'"
            )
        pedido.status_pedido = status

    def __repr__(self):
        return f"EmpresaMarisqueira({self.id_empresa_marisqueira}, {self.nome})"


# ============================================================
# EMPRESA_COMPRADORA
# ============================================================

class EmpresaCompradora:
    """Compradora. Consulta produtos, realiza pedidos e avalia marisqueiras."""

    def __init__(self, id_empresa_compradora, CNPJ, nome, localizacao):
        if not id_empresa_compradora:
            raise ValueError("id_empresa_compradora é obrigatório")
        if not CNPJ:
            raise ValueError("CNPJ é obrigatório")
        if not nome:
            raise ValueError("nome é obrigatório")
        if not localizacao:
            raise ValueError("localizacao é obrigatória")

        self.id_empresa_compradora = id_empresa_compradora
        self.CNPJ = CNPJ
        self.nome = nome
        self.localizacao = localizacao
        self.pedidos_realizados = []
        self.avaliacoes_emitidas = []

    def consultar_produtos(self, nome=None, categoria=None, localizacao=None,
                           empresa=None, ordenar_por=None):
        """RN10 / RN11 - consulta e ordena produtos de todas as marisqueiras."""
        resultados = list(_REGISTRO_PRODUTOS.values())

        if nome is not None:
            resultados = [p for p in resultados if p.nome == nome]
        if categoria is not None:
            resultados = [p for p in resultados if p.categoria == categoria]
        if localizacao is not None:
            resultados = [
                p for p in resultados
                if p.empresa and p.empresa.localizacao == localizacao
            ]
        if empresa is not None:
            resultados = [p for p in resultados if p.empresa is empresa]

        if ordenar_por == "menor_preco":
            resultados.sort(key=lambda p: p.preco)
        elif ordenar_por == "maior_preco":
            resultados.sort(key=lambda p: p.preco, reverse=True)

        return resultados

    def comparar_produtos(self, produtos):
        """P26 - compara produtos de empresas diferentes."""
        if not produtos:
            return []
        return [
            {
                "id_produto": p.id_produto,
                "nome": p.nome,
                "categoria": p.categoria,
                "preco": p.preco,
                "quantidade_disponivel": p.quantidade_disponivel,
                "empresa": p.empresa.nome if p.empresa else None,
                "localizacao": p.empresa.localizacao if p.empresa else None,
            }
            for p in produtos
        ]

    def realizar_pedido(self, id_pedido, endereco_entrega, tempo_entrega):
        """RN13 - cria um novo pedido."""
        pedido = Pedido(
            id_pedido=id_pedido,
            comprador=self,
            endereco_entrega=endereco_entrega,
            tempo_entrega=tempo_entrega,
        )
        self.pedidos_realizados.append(pedido)
        return pedido

    def avaliar_empresa(self, id_avaliacao, empresa, nota):
        """RN21 - avalia uma EmpresaMarisqueira com nota de 1 a 5."""
        avaliacao = Avaliacao(id_avaliacao=id_avaliacao, nota=nota, empresa=empresa)
        self.avaliacoes_emitidas.append(avaliacao)
        if empresa is not None and hasattr(empresa, "avaliacoes_recebidas"):
            empresa.avaliacoes_recebidas.append(avaliacao)
        return avaliacao

    def __repr__(self):
        return f"EmpresaCompradora({self.id_empresa_compradora}, {self.nome})"