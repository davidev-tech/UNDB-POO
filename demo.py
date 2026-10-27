"""
DEMO INTERATIVA — Sistema Marisqueiras da Ilha
==============================================

Menu para testar cada classe e ver o comportamento conforme as regras
de negócio (RN01 a RN23) do projeto.

Uso:
    python demo.py                 # menu interativo
    python demo.py --all           # roda todos os cenários de uma vez
    python demo.py --scenario 3    # roda só o cenário 3

Para gerar a saída que vai no artigo:
    python demo.py --all > saida_demo.txt
    (o colorama remove as cores automaticamente quando redirecionado)
"""

import sys
from datetime import datetime

from marisqueiras import (
    EmpresaCompradora,
    EmpresaMarisqueira,
    ItemPedido,
    CategoriaProduto,
    StatusPedido,
    RegraNegocioError,
    QuantidadeMinimaError,
    EstoqueInsuficienteError,
)


# ---------------------------------------------------------------------------
# Cores (com fallback caso colorama não esteja instalado)
# ---------------------------------------------------------------------------
try:
    from colorama import init, Fore, Style
    init(autoreset=False)

    def verde(s):     return f"{Fore.GREEN}{s}{Style.RESET_ALL}"
    def vermelho(s):  return f"{Fore.RED}{s}{Style.RESET_ALL}"
    def amarelo(s):   return f"{Fore.YELLOW}{s}{Style.RESET_ALL}"
    def ciano(s):     return f"{Fore.CYAN}{s}{Style.RESET_ALL}"
    def magenta(s):   return f"{Fore.MAGENTA}{s}{Style.RESET_ALL}"
    def azul(s):      return f"{Fore.BLUE}{s}{Style.RESET_ALL}"
    def negrito(s):   return f"{Style.BRIGHT}{s}{Style.RESET_ALL}"
    def dim(s):       return f"{Style.DIM}{s}{Style.RESET_ALL}"
except ImportError:
    def _id(s): return s
    verde = vermelho = amarelo = ciano = magenta = azul = negrito = dim = _id


WIDTH = 74


# ---------------------------------------------------------------------------
# Helpers de saída (com cores)
# ---------------------------------------------------------------------------
def titulo(texto, regras=""):
    print()
    print(ciano("=" * WIDTH))
    print(ciano(negrito(f"  {texto}")))
    if regras:
        print(dim(f"  Regras testadas: {regras}"))
    print(ciano("=" * WIDTH))


def passo(numero, descricao):
    print()
    print(f"  {amarelo(negrito(f'[{numero}]'))} {negrito(descricao)}")


def ok(msg):
    print(f"        {verde(negrito('[OK]'))}   {msg}")


def bloq(msg):
    print(f"        {vermelho(negrito('[BLOQ]'))} {vermelho(msg)}")


def erro(msg):
    print(f"        {vermelho(negrito('[ERRO]'))} {vermelho(negrito(msg))}")


def info(msg):
    print(f"        {azul('[INFO]')} {dim(msg)}")


# Helper extra: colorir o status visual (verde/laranja/vermelho)
def _status_visual_colorido(valor):
    v = valor.lower()
    if v == "verde":
        return verde(valor.upper())
    if v == "laranja":
        return amarelo(valor.upper())
    if v == "vermelho":
        return vermelho(valor.upper())
    return negrito(valor.upper())


# ---------------------------------------------------------------------------
# Cenários
# ---------------------------------------------------------------------------

def cenario_01_cadastro_produto():
    titulo("EmpresaMarisqueira.cadastrar_produto()", "RN05, RN06, P15, P16, P18")
    m = EmpresaMarisqueira("Marisqueira da Vila", "Raposa - MA", "Dona Maria", (0, 24))
    print(f"        Empresa: {ciano(m.nome)} | Local: {m.localizacao}")
    print(f"        Responsável: {m.responsavel}")

    passo(1, 'Cadastrar "Camarão" fresco — R$ 40.00/kg, 100 kg')
    try:
        p = m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
        ok(f"Produto criado: {p}")
    except Exception as e:
        erro(str(e))

    passo(2, 'Cadastrar "Camarão" congelado — mesmo nome, categoria diferente')
    try:
        p = m.cadastrar_produto("Camarão", CategoriaProduto.CONGELADO, 35.0, 80)
        ok(f"Produto criado: {p}")
        info("RN06: fresco e congelado são produtos distintos no cadastro.")
    except Exception as e:
        erro(str(e))

    passo(3, 'Tentar cadastrar "Camarão" fresco novamente')
    try:
        m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 42.0, 50)
        erro("Deveria ter sido bloqueado, mas não foi.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(4, "Tentar cadastrar produto com preço R$ 0.00")
    try:
        m.cadastrar_produto("Siri", CategoriaProduto.FRESCO, 0, 50)
        erro("Deveria ter sido bloqueado, mas não foi.")
    except ValueError as e:
        bloq(str(e))

    passo(5, "Cadastrar produto com 10 kg (abaixo do mínimo de venda de 25 kg)")
    try:
        p = m.cadastrar_produto("Siri", CategoriaProduto.FRESCO, 30.0, 10)
        ok(f"Produto criado: {p}")
        info("RN05 é regra de VENDA, não de cadastro. Este produto existe,")
        info("mas não pode ser vendido (a venda é validada em ItemPedido).")
    except Exception as e:
        erro(str(e))


def cenario_02_estoque_visual():
    titulo("Estoque e indicador visual", "RN08, RN09, RN19, RN20, P19, P20, P33")
    m = EmpresaMarisqueira("Marisqueira da Vila", "Raposa - MA", "Dona Maria", (8, 18))
    p = m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
    print(f"        Horário de funcionamento: "
          f"{amarelo(str(m.horario_funcionamento[0]) + 'h')} às "
          f"{amarelo(str(m.horario_funcionamento[1]) + 'h')}")
    print(f"        Estoque inicial: {verde(str(p.quantidade_disponivel) + ' kg')}")

    passo(1, "Verificar disponibilidade com estoque de 100 kg")
    ok(f"esta_disponivel() → {verde(str(p.esta_disponivel()))}")

    passo(2, "Alterar quantidade para 50 kg (RN08)")
    m.alterar_quantidade(p, 50)
    ok(f"Nova quantidade: {amarelo(str(p.quantidade_disponivel) + ' kg')}")

    passo(3, "Zerar o estoque (RN09 — produto permanece cadastrado)")
    m.alterar_quantidade(p, 0)
    ok(f"Quantidade: {vermelho(str(p.quantidade_disponivel) + ' kg')}")
    ok(f"esta_disponivel() → {vermelho(str(p.esta_disponivel()))}")
    ok(f"Produto ainda na lista da empresa? {verde(str(p in m.produtos))}")

    passo(4, "Tentar definir quantidade negativa (-5)")
    try:
        m.alterar_quantidade(p, -5)
        erro("Deveria ter sido bloqueado.")
    except ValueError as e:
        bloq(str(e))

    passo(5, "Status visual às 20h (fora do horário 8h–18h)")
    m.alterar_quantidade(p, 100)
    s = m.status_visual(hora_atual=20)
    ok(f"Status: {_status_visual_colorido(s.value)}")
    info("Vermelho = fora do horário de funcionamento (P33).")

    passo(6, "Status visual às 10h com estoque de 100 kg")
    s = m.status_visual(hora_atual=10)
    ok(f"Status: {_status_visual_colorido(s.value)}")
    info("Verde = disponível: existe pelo menos um produto com estoque ≥ 25 kg.")

    passo(7, "Status visual às 10h com estoque de apenas 10 kg")
    m.alterar_quantidade(p, 10)
    s = m.status_visual(hora_atual=10)
    ok(f"Status: {_status_visual_colorido(s.value)}")
    info("Laranja = estoque baixo: nenhum produto com estoque suficiente (≥ 25 kg).")


def cenario_03_analise_pedido():
    titulo("Análise de pedido — aceitar / rejeitar / ajustar", "RN07, RN08, P7")
    m = EmpresaMarisqueira("Marisqueira da Vila", "Raposa - MA", "Dona Maria", (0, 24))
    c = EmpresaCompradora("Restaurante Maré", "São Luís - MA", "Sr. João", (0, 24))
    p = m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
    print(f"        Estoque inicial: {verde(str(p.quantidade_disponivel) + ' kg')}")

    passo(1, "PEDIDO 1 — será ACEITO")
    ped1 = c.realizar_pedido(m, "Rua X, 100", "2 dias", [(p, 50)])
    m.receber_pedido(ped1)
    ok(f"Recebido. Estoque antes: {amarelo(str(p.quantidade_disponivel) + ' kg')}")
    m.aceitar_pedido(ped1)
    ok(f"Aceito | status = {amarelo(ped1.status.value)} | "
       f"aceito = {verde(str(ped1.aceito))}")
    ok(f"Estoque após baixa: {verde(str(p.quantidade_disponivel) + ' kg')} (baixa de 50)")
    info("RN18: aceite revalida disponibilidade e dá baixa no estoque.")

    passo(2, "Tentar aceitar o MESMO pedido duas vezes")
    try:
        m.aceitar_pedido(ped1)
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(3, "PEDIDO 2 — será REJEITADO")
    ped2 = c.realizar_pedido(m, "Rua Y, 200", "3 dias", [(p, 25)])
    m.receber_pedido(ped2)
    est_antes = p.quantidade_disponivel
    m.rejeitar_pedido(ped2)
    ok(f"aceito = {vermelho(str(ped2.aceito))} | status = {dim(str(ped2.status))}")
    ok(f"Estoque inalterado: {verde(str(p.quantidade_disponivel) + ' kg')} "
       f"(era {est_antes} kg)")
    info("Rejeição não movimenta estoque.")

    passo(4, "Tentar rejeitar um pedido já ACEITO")
    try:
        m.rejeitar_pedido(ped1)
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(5, "PEDIDO 3 — SOLICITAR AJUSTE ao comprador")
    ped3 = c.realizar_pedido(m, "Rua Z, 300", "1 dia", [(p, 30)])
    m.receber_pedido(ped3)
    m.solicitar_ajuste(ped3, "Aumentar 10 kg para fechar a carga")
    ok(f'mensagem_ajuste = "{amarelo(ped3.mensagem_ajuste)}"')
    ok(f"aceito = {dim(str(ped3.aceito))} | status = {dim(str(ped3.status))}")
    info("Solicitar ajuste não altera aceito nem status — só registra a mensagem.")


def cenario_04_status_entrega():
    titulo("Atualizar status de entrega", "RN22, P7")
    m = EmpresaMarisqueira("Marisqueira da Vila", "Raposa - MA", "Dona Maria", (0, 24))
    c = EmpresaCompradora("Restaurante Maré", "São Luís - MA", "Sr. João", (0, 24))
    p = m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 1000)

    passo(1, "Tentar atualizar entrega ANTES do aceite")
    ped = c.realizar_pedido(m, "Rua X", "2 dias", [(p, 25)])
    m.receber_pedido(ped)
    try:
        m.atualizar_status_entrega(ped, StatusPedido.EM_CURSO)
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(2, "Aceitar o pedido e avançar a entrega (fluxo válido)")
    m.aceitar_pedido(ped)
    ok(f"Após aceite | status = {amarelo(ped.status.value)}")
    m.atualizar_status_entrega(ped, StatusPedido.EM_CURSO)
    ok(f"Após 1ª atualização | status = {ciano(ped.status.value)}")
    m.atualizar_status_entrega(ped, StatusPedido.FINALIZADO)
    ok(f"Após 2ª atualização | status = {verde(ped.status.value)}")
    info("RN22: transições permitidas: EM_PREPARO → EM_CURSO → FINALIZADO.")

    passo(3, "Tentar pular de EM_PREPARO direto para FINALIZADO")
    ped2 = c.realizar_pedido(m, "Rua Y", "1 dia", [(p, 25)])
    m.receber_pedido(ped2)
    m.aceitar_pedido(ped2)
    try:
        m.atualizar_status_entrega(ped2, StatusPedido.FINALIZADO)
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(4, "Tentar avançar um pedido já FINALIZADO")
    m.atualizar_status_entrega(ped2, StatusPedido.EM_CURSO)
    m.atualizar_status_entrega(ped2, StatusPedido.FINALIZADO)
    try:
        m.atualizar_status_entrega(ped2, StatusPedido.FINALIZADO)
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))


def cenario_05_consulta_comparacao():
    titulo("EmpresaCompradora — consulta e comparação",
           "RN10, RN11, RN12, P9, P21, P22, P25, P26")
    m1 = EmpresaMarisqueira("Marisqueira A", "Raposa - MA", "Dona Ana", (0, 24))
    m2 = EmpresaMarisqueira("Marisqueira B", "São Luís - MA", "Sr. Pedro", (0, 24))
    c = EmpresaCompradora("Restaurante Maré", "São Luís - MA", "Sr. João", (0, 24))

    p1 = m1.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
    p2 = m1.cadastrar_produto("Siri", CategoriaProduto.CONGELADO, 30.0, 60)
    p3 = m2.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 35.0, 80)
    todos = [p1, p2, p3]

    print(f"        {negrito('Produtos cadastrados:')}")
    for p in todos:
        print(f"          - {p}")

    passo(1, 'Filtro por nome = "camarão"')
    r = c.consultar_produtos(todos, nome="camarão")
    ok(f"Encontrados: {verde(str(len(r)))}")
    for p in r:
        print(f"          - {p}")

    passo(2, "Filtro por categoria = CONGELADO")
    r = c.consultar_produtos(todos, categoria=CategoriaProduto.CONGELADO)
    ok(f"Encontrados: {verde(str(len(r)))}")
    for p in r:
        print(f"          - {p}")

    passo(3, 'Filtro por localização = "Raposa - MA"')
    r = c.consultar_produtos(todos, localizacao="Raposa - MA")
    ok(f"Encontrados: {verde(str(len(r)))}")
    for p in r:
        print(f"          - {p}")

    passo(4, "Filtro por empresa = Marisqueira B")
    r = c.consultar_produtos(todos, empresa_marisqueira=m2)
    ok(f"Encontrados: {verde(str(len(r)))}")
    for p in r:
        print(f"          - {p}")

    passo(5, "Ordenar por MENOR preço")
    r = c.consultar_produtos(todos, ordenar_por="menor_preco")
    for p in r:
        print(f"          - {verde(f'R$ {p.preco:>6.2f}')}  "
              f"{p.nome} ({ciano(p.empresa.nome)})")

    passo(6, "Ordenar por MAIOR preço")
    r = c.consultar_produtos(todos, ordenar_por="maior_preco")
    for p in r:
        print(f"          - {verde(f'R$ {p.preco:>6.2f}')}  "
              f"{p.nome} ({ciano(p.empresa.nome)})")

    passo(7, "Comparar produtos de empresas diferentes (P26)")
    comparacao = c.comparar_produtos(p1, p3)
    for k, v in comparacao.items():
        print(f"          {negrito(k)}: {v}")

    passo(8, "Marisqueira A vê apenas os próprios produtos (RN12 / P25)")
    proprios = m1.consultar_proprios_produtos()
    ok(f"Marisqueira A vê {verde(str(len(proprios)))} produtos (de 3 no total)")
    for p in proprios:
        print(f"          - {p}")


def cenario_06_realizar_pedido():
    titulo("EmpresaCompradora — realizar pedido (válido e inválidos)",
           "RN13 a RN18, P27 a P34")
    m1 = EmpresaMarisqueira("Marisqueira A", "Raposa - MA", "Dona Ana", (0, 24))
    m2 = EmpresaMarisqueira("Marisqueira B", "São Luís - MA", "Sr. Pedro", (0, 24))
    c = EmpresaCompradora("Restaurante Maré", "São Luís - MA", "Sr. João", (0, 24))
    camarao = m1.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
    siri = m1.cadastrar_produto("Siri", CategoriaProduto.CONGELADO, 30.0, 60)
    camarao_b = m2.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 35.0, 80)

    passo(1, "Pedido VÁLIDO com 2 produtos da mesma marisqueira")
    try:
        ped = c.realizar_pedido(m1, "Rua X, 100", "2 dias", [(camarao, 50), (siri, 30)])
        ok(f"Pedido criado com {verde(str(len(ped.itens)))} itens")
        for item in ped.itens:
            print(f"          - {item}")
        ok(f"Total: {verde(f'R$ {ped.calcular_total():.2f}')}")
        info("RN16: não há mínimo financeiro — só mínimo de 25 kg por item.")
        info("RN17: não há máximo fixo — só o limite do estoque.")
    except Exception as e:
        erro(str(e))

    passo(2, "Pedido INVÁLIDO — item com 24 kg (abaixo de 25)")
    try:
        c.realizar_pedido(m1, "Rua X", "2 dias", [(camarao, 24)])
        erro("Deveria ter sido bloqueado.")
    except QuantidadeMinimaError as e:
        bloq(str(e))

    passo(3, "Pedido INVÁLIDO — 500 kg de camarão (estoque: 100 kg)")
    try:
        c.realizar_pedido(m1, "Rua X", "2 dias", [(camarao, 500)])
        erro("Deveria ter sido bloqueado.")
    except EstoqueInsuficienteError as e:
        bloq(str(e))
        info("RN18 / P34: sistema impede pedido acima do disponível.")

    passo(4, "Pedido INVÁLIDO — produtos de 2 marisqueiras diferentes")
    try:
        c.realizar_pedido(m1, "Rua X", "2 dias", [(camarao, 25), (camarao_b, 25)])
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))
        info("RN14 / P29: um pedido não pode reunir empresas diferentes.")

    passo(5, "Pedido INVÁLIDO — sem itens")
    try:
        c.realizar_pedido(m1, "Rua X", "2 dias", [])
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(6, "Pedido INVÁLIDO — endereço vazio")
    try:
        c.realizar_pedido(m1, "", "2 dias", [(camarao, 25)])
        erro("Deveria ter sido bloqueado.")
    except ValueError as e:
        bloq(str(e))


def cenario_07_avaliar():
    titulo("EmpresaCompradora — avaliar marisqueira", "RN21, P23, P24")
    m = EmpresaMarisqueira("Marisqueira da Vila", "Raposa - MA", "Dona Maria", (0, 24))
    c = EmpresaCompradora("Restaurante Maré", "São Luís - MA", "Sr. João", (0, 24))
    p = m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 1000)

    passo(1, "Avaliar SEM nenhuma compra (bloqueado)")
    try:
        c.avaliar_empresa(m, 5, "Ótimo")
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(2, "Pedido CRIADO mas AINDA NÃO ACEITO — avaliar (bloqueado)")
    ped1 = c.realizar_pedido(m, "Rua X", "2 dias", [(p, 50)])
    m.receber_pedido(ped1)
    try:
        c.avaliar_empresa(m, 5)
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(3, "Pedido REJEITADO — avaliar (bloqueado)")
    m.rejeitar_pedido(ped1)
    try:
        c.avaliar_empresa(m, 5)
        erro("Deveria ter sido bloqueado.")
    except RegraNegocioError as e:
        bloq(str(e))

    passo(4, "Novo pedido ACEITO — avaliar com nota 5 (sucesso)")
    ped2 = c.realizar_pedido(m, "Rua Y", "1 dia", [(p, 50)])
    m.receber_pedido(ped2)
    m.aceitar_pedido(ped2)
    av = c.avaliar_empresa(m, 5, "Produto fresco, entrega rápida")
    ok(f"Avaliação registrada: {verde(negrito(str(av)))}")
    ok(f"Média atual da marisqueira: "
       f"{amarelo(str(f'{m.media_avaliacoes():.2f}') + '★')}")
    info("RN21 / P23: avaliação só ocorre após a compra aceita.")

    passo(5, "Nota 0 (inválida — escala é 1 a 5)")
    try:
        c.avaliar_empresa(m, 0)
        erro("Deveria ter sido bloqueado.")
    except ValueError as e:
        bloq(str(e))

    passo(6, "Nota 6 (inválida)")
    try:
        c.avaliar_empresa(m, 6)
        erro("Deveria ter sido bloqueado.")
    except ValueError as e:
        bloq(str(e))

    passo(7, "Nota não inteira (4.5) — inválida")
    try:
        c.avaliar_empresa(m, 4.5)
        erro("Deveria ter sido bloqueado.")
    except ValueError as e:
        bloq(str(e))


def cenario_08_item_pedido():
    titulo("ItemPedido / Pedido — validações internas", "RN05, RN07, RN15, RN18")
    m = EmpresaMarisqueira("Marisqueira da Vila", "Raposa - MA", "Dona Maria", (0, 24))
    p = m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)

    passo(1, "ItemPedido com 24 kg (abaixo do mínimo)")
    try:
        ItemPedido(p, 24)
        erro("Deveria ter sido bloqueado.")
    except QuantidadeMinimaError as e:
        bloq(str(e))

    passo(2, "ItemPedido com exatamente 25 kg (mínimo aceito)")
    item = ItemPedido(p, 25)
    ok(f"Item criado: {item}")

    passo(3, "ItemPedido com 101 kg (estoque é 100 kg)")
    try:
        ItemPedido(p, 101)
        erro("Deveria ter sido bloqueado.")
    except EstoqueInsuficienteError as e:
        bloq(str(e))

    passo(4, "Preço congelado no momento da compra (RN07)")
    item = ItemPedido(p, 50)
    ok(f"Produto.preco original:     {verde(f'R$ {p.preco:.2f}')}")
    ok(f"ItemPedido.preco_unitario:  {verde(f'R$ {item.preco_unitario:.2f}')}")
    info("Alterando Produto.preco para R$ 999.00...")
    p.preco = 999.0
    print(f"        Novo Produto.preco:        {amarelo(f'R$ {p.preco:.2f}')}")
    print(f"        ItemPedido.preco_unitario: {verde(f'R$ {item.preco_unitario:.2f}')}")
    if item.preco_unitario == 40.0:
        ok("RN07 satisfeita: preço da venda já feita não muda.")
    else:
        erro("Preço do item foi alterado indevidamente!")


def cenario_09_fluxo_completo():
    titulo("Fluxo completo ponta a ponta",
           "P7 — consulta → pedido → aceite → entrega → avaliação")
    m = EmpresaMarisqueira("Marisqueira da Vila", "Raposa - MA", "Dona Maria", (0, 24))
    c = EmpresaCompradora("Restaurante Maré", "São Luís - MA", "Sr. João", (0, 24))
    p = m.cadastrar_produto("Camarão", CategoriaProduto.FRESCO, 40.0, 100)
    print(f"        Produto: {p}")

    passo(1, "Compradora consulta produtos da marisqueira")
    r = c.consultar_produtos(m.consultar_proprios_produtos(), nome="camarão")
    ok(f"{verde(str(len(r)))} produto(s) encontrado(s)")

    passo(2, "Compradora realiza pedido de 50 kg")
    ped = c.realizar_pedido(m, "Rua X, 100", "2 dias", [(p, 50)])
    ok(f"Pedido criado | Total: {verde(f'R$ {ped.calcular_total():.2f}')}")

    passo(3, "Marisqueira recebe o pedido")
    m.receber_pedido(ped)
    ok(f"Pedido na lista da marisqueira (total: {amarelo(str(len(m.pedidos_recebidos)))})")

    passo(4, "Marisqueira ACEITA o pedido")
    m.aceitar_pedido(ped)
    ok(f"status = {amarelo(ped.status.value)} | aceito = {verde(str(ped.aceito))}")
    ok(f"Estoque após baixa: {verde(str(p.quantidade_disponivel) + ' kg')}")

    passo(5, "Marisqueira atualiza status de entrega")
    m.atualizar_status_entrega(ped, StatusPedido.EM_CURSO)
    ok(f"status = {ciano(ped.status.value)}")
    m.atualizar_status_entrega(ped, StatusPedido.FINALIZADO)
    ok(f"status = {verde(ped.status.value)}")

    passo(6, "Compradora avalia a marisqueira")
    av = c.avaliar_empresa(m, 5, "Entrega no prazo, produto fresco")
    ok(f"Avaliação: {verde(negrito(str(av)))}")
    ok(f"Média da marisqueira: "
       f"{amarelo(str(f'{m.media_avaliacoes():.2f}') + '★')}")

    passo(7, "Resumo final")
    print(f"        Pedido #{id(ped)}")
    print(f"        Status: {verde(ped.status.value)}")
    print(f"        Total:  {verde(f'R$ {ped.calcular_total():.2f}')}")
    print(f"        Estoque restante de camarão: "
          f"{verde(str(p.quantidade_disponivel) + ' kg')}")
    print(f"        Avaliações recebidas: "
          f"{amarelo(str(len(m.avaliacoes_recebidas)))}")


# ---------------------------------------------------------------------------
# Menu e execução
# ---------------------------------------------------------------------------

CENARIOS = [
    ("1", "EmpresaMarisqueira — cadastro de produto",        cenario_01_cadastro_produto),
    ("2", "EmpresaMarisqueira — estoque e indicador visual", cenario_02_estoque_visual),
    ("3", "EmpresaMarisqueira — análise de pedido",          cenario_03_analise_pedido),
    ("4", "EmpresaMarisqueira — status de entrega",          cenario_04_status_entrega),
    ("5", "EmpresaCompradora — consulta e comparação",       cenario_05_consulta_comparacao),
    ("6", "EmpresaCompradora — realizar pedido",             cenario_06_realizar_pedido),
    ("7", "EmpresaCompradora — avaliar marisqueira",         cenario_07_avaliar),
    ("8", "ItemPedido / Pedido — validações internas",       cenario_08_item_pedido),
    ("9", "Fluxo completo ponta a ponta",                    cenario_09_fluxo_completo),
]


def cabecalho():
    print(ciano("=" * WIDTH))
    print(ciano(negrito("  DEMO — MARISQUEIRAS DA ILHA".center(WIDTH))))
    print(ciano("  Projeto POO | Docente: Aline Maya".center(WIDTH)))
    print(dim(f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}".center(WIDTH)))
    print(ciano("=" * WIDTH))


def rodar_todos():
    cabecalho()
    for _, _, funcao in CENARIOS:
        funcao()
    print()
    print(ciano("=" * WIDTH))
    print(verde(negrito("  FIM — todos os cenários executados.".center(WIDTH))))
    print(ciano("=" * WIDTH))


def menu():
    while True:
        print()
        print(ciano("=" * WIDTH))
        print(ciano(negrito("  MENU DE TESTES — MARISQUEIRAS DA ILHA".center(WIDTH))))
        print(ciano("=" * WIDTH))
        for codigo, descricao, _ in CENARIOS:
            print(f"  {amarelo(codigo)}. {descricao}")
        print(f"  {verde('A')}. {verde(negrito('Rodar TODOS os cenários'))} "
              f"{dim('(útil para gerar a saída do artigo)')}")
        print(f"  {vermelho('0')}. {vermelho('Sair')}")
        print(ciano("=" * WIDTH))
        opcao = input(f"  {negrito('Escolha:')} ").strip().upper()

        if opcao == "0":
            print(verde("\n  Até logo!\n"))
            return
        if opcao == "A":
            rodar_todos()
            continue

        funcao = next((f for c_, _, f in CENARIOS if c_ == opcao), None)
        if funcao is None:
            print(vermelho(f"\n  Opção inválida: {opcao!r}"))
        else:
            funcao()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--all", "-a"):
            rodar_todos()
        elif arg in ("--scenario", "-s") and len(sys.argv) > 2:
            num = sys.argv[2]
            funcao = next((f for c_, _, f in CENARIOS if c_ == num), None)
            if funcao:
                cabecalho()
                funcao()
            else:
                print(vermelho(f"Cenário desconhecido: {num}"))
                sys.exit(1)
        else:
            print(__doc__)
            sys.exit(1)
    else:
        menu()