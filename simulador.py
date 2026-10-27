"""
SIMULADOR INTERATIVO — Marisqueiras da Ilha
============================================
Mini-sistema onde VOCÊ digita as entradas. Cada operação é validada
contra as regras de negócio do PDF.

Uso:
    python simulador.py
"""

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

# --- Cores (com fallback caso colorama não esteja instalado) ---------------
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


WIDTH = 72


# ===========================================================================
# Helpers de entrada
# ===========================================================================
def ler_int(prompt, minimo=None, maximo=None):
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
        except ValueError:
            print(vermelho("  ! Digite um número inteiro."))
            continue
        if minimo is not None and v < minimo:
            print(vermelho(f"  ! Valor deve ser >= {minimo}."))
            continue
        if maximo is not None and v > maximo:
            print(vermelho(f"  ! Valor deve ser <= {maximo}."))
            continue
        return v


def ler_float(prompt, minimo=None):
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            v = float(s)
        except ValueError:
            print(vermelho("  ! Digite um número."))
            continue
        if minimo is not None and v < minimo:
            print(vermelho(f"  ! Valor deve ser >= {minimo}."))
            continue
        return v


def ler_texto(prompt, obrigatorio=True):
    while True:
        s = input(prompt).strip()
        if not s and obrigatorio:
            print(vermelho("  ! Campo obrigatório."))
            continue
        return s


def sep(cor=ciano):
    print(cor("=" * WIDTH))


# ===========================================================================
# Tradução de erros → regra
# ===========================================================================
def explicar_erro(e):
    msg = str(e).lower()
    if isinstance(e, QuantidadeMinimaError):
        return "RN05/RN15 — mínimo de 25 kg por produto."
    if isinstance(e, EstoqueInsuficienteError):
        return "RN18/P34 — quantidade acima do estoque disponível."
    if isinstance(e, RegraNegocioError):
        if "empresas diferentes" in msg:
            return "RN14/P29 — pedido não pode reunir empresas diferentes."
        if "já foi analisado" in msg:
            return "P7 — pedido já passou pela análise da marisqueira."
        if "atualizar entrega" in msg:
            return "RN22 — só é possível atualizar entrega de pedido aceito."
        if "transição inválida" in msg or "estado final" in msg:
            return "RN22 — transições: EM_PREPARO → EM_CURSO → FINALIZADO."
        if "pelo menos um item" in msg:
            return "RN13 — pedido precisa ter pelo menos um item."
        if "produto não pertence" in msg:
            return "RN12 — a empresa só manipula os próprios produtos."
        if "avaliar após a compra" in msg:
            return "RN21/P23 — avaliação só ocorre após compra aceita."
        if "já existe um produto" in msg:
            return "RN06/P18 — fresco e congelado são categorias distintas."
        return "Regra de negócio violada."
    if isinstance(e, ValueError):
        return "Campo inválido (ver mensagem)."
    return "Erro inesperado."


def executar(fn, *args, **kwargs):
    """Executa e imprime OK ou BLOQ, mostrando a regra se falhar."""
    try:
        resultado = fn(*args, **kwargs)
        print(f"  {verde('[OK]')} {negrito('operação concluída.')}")
        return True, resultado
    except (RegraNegocioError, ValueError) as e:
        print(f"  {vermelho('[BLOQ]')} {e}")
        print(f"  {vermelho('→')} {vermelho(explicar_erro(e))}")
        return False, None


# ===========================================================================
# Estado
# ===========================================================================
class Sessao:
    def __init__(self):
        self.marisqueiras = []
        self.compradoras = []
        self.marisqueira_atual = None
        self.compradora_atual = None


# ===========================================================================
# Formatação de produtos / pedidos
# ===========================================================================
def formatar_produto(p, mostrar_empresa=True):
    cat = ciano(p.categoria.value)
    if p.quantidade_disponivel == 0:
        qtd = vermelho("0 kg (indisponível)")
    elif p.quantidade_disponivel < 25:
        qtd = amarelo(f"{p.quantidade_disponivel} kg (abaixo do mínimo)")
    else:
        qtd = verde(f"{p.quantidade_disponivel} kg")
    txt = f"{negrito(p.nome)} ({cat}) — R$ {p.preco:.2f}/kg — {qtd}"
    if mostrar_empresa:
        txt += f" — {ciano(p.empresa.nome)}"
    return txt


def cor_status(p):
    if p.aceito is None:   return dim
    if p.aceito is False:  return vermelho
    if p.status == StatusPedido.FINALIZADO: return verde
    if p.status == StatusPedido.EM_CURSO:   return ciano
    return amarelo


def resumo_pedido(p):
    cor = cor_status(p)
    if p.aceito is None:
        analise = "PENDENTE"
    elif p.aceito:
        analise = "ACEITO"
    else:
        analise = "REJEITADO"
    status = p.status.value.upper() if p.status else "—"
    print(f"      {negrito('Análise:')} {cor(analise)} | "
          f"{negrito('Entrega:')} {cor(status)}")
    print(f"      {negrito('Endereço:')} {p.endereco_entrega} | "
          f"{negrito('Tempo:')} {p.tempo_entrega}")
    for it in p.itens:
        print(f"        · {it}")
    print(f"      {negrito('Total:')} {verde(f'R$ {p.calcular_total():.2f}')}")
    if p.mensagem_ajuste:
        print(f"      {amarelo('Ajuste solicitado:')} {p.mensagem_ajuste}")


# ===========================================================================
# Seleção e criação de empresas
# ===========================================================================
def cadastrar_empresa(sessao):
    print()
    print(f"  {negrito('Tipo de empresa:')}")
    print(f"    {amarelo('1')}. Marisqueira (fornecedora)")
    print(f"    {amarelo('2')}. Compradora")
    tipo = ler_int("  Escolha: ", 1, 2)

    nome = ler_texto("  Nome: ")
    local = ler_texto("  Localização: ")
    responsavel = ler_texto("  Responsável: ")
    print(f"  {negrito('Horário de funcionamento:')}")
    abertura = ler_int("    Hora de abertura (0-23): ", 0, 23)
    fechamento = ler_int("    Hora de fechamento (1-24): ", 1, 24)

    try:
        if tipo == 1:
            emp = EmpresaMarisqueira(nome, local, responsavel, (abertura, fechamento))
            sessao.marisqueiras.append(emp)
            print(f"  {verde('[OK]')} Marisqueira {ciano(emp.nome)} cadastrada.")
        else:
            emp = EmpresaCompradora(nome, local, responsavel, (abertura, fechamento))
            sessao.compradoras.append(emp)
            print(f"  {verde('[OK]')} Compradora {magenta(emp.nome)} cadastrada.")
    except ValueError as e:
        print(f"  {vermelho('[BLOQ]')} {e}")


def escolher_marisqueira(sessao):
    if not sessao.marisqueiras:
        print(vermelho("  Nenhuma marisqueira cadastrada. Cadastre primeiro."))
        return None
    print(f"  {negrito('Marisqueiras:')}")
    for i, m in enumerate(sessao.marisqueiras, 1):
        print(f"    {amarelo(i)}. {ciano(m.nome)} ({m.localizacao})")
    n = ler_int("  Escolha: ", 1, len(sessao.marisqueiras))
    return sessao.marisqueiras[n - 1]


def escolher_compradora(sessao):
    if not sessao.compradoras:
        print(vermelho("  Nenhuma compradora cadastrada. Cadastre primeiro."))
        return None
    print(f"  {negrito('Compradoras:')}")
    for i, c in enumerate(sessao.compradoras, 1):
        print(f"    {amarelo(i)}. {magenta(c.nome)} ({c.localizacao})")
    n = ler_int("  Escolha: ", 1, len(sessao.compradoras))
    return sessao.compradoras[n - 1]


# ===========================================================================
# Ações da Marisqueira
# ===========================================================================
def acao_cadastrar_produto(m):
    print()
    print(f"  {negrito('Categoria:')}")
    print(f"    {amarelo('1')}. Fresco")
    print(f"    {amarelo('2')}. Congelado")
    cat = CategoriaProduto.FRESCO if ler_int("  Escolha: ", 1, 2) == 1 else CategoriaProduto.CONGELADO

    nome = ler_texto("  Nome do produto: ")
    preco = ler_float("  Preço por kg (R$): ", 0.01)
    qtd = ler_int("  Quantidade inicial (kg, >= 0): ", 0)
    foto = ler_texto("  Foto (opcional, Enter para vazio): ", obrigatorio=False)

    sucesso, _ = executar(m.cadastrar_produto, nome, cat, preco, qtd, foto or None)
    if sucesso:
        print(f"  {dim('(RN05 é regra de venda, não de cadastro:')}")
        print(f"  {dim(' produtos com < 25 kg são permitidos, mas não vendáveis.)')}")


def acao_alterar_quantidade(m):
    print()
    if not m.produtos:
        print(vermelho("  Nenhum produto cadastrado."))
        return
    print(f"  {negrito('Seus produtos:')}")
    for i, p in enumerate(m.produtos, 1):
        print(f"    {amarelo(i)}. {formatar_produto(p, mostrar_empresa=False)}")
    n = ler_int("  Escolha: ", 1, len(m.produtos))
    nova = ler_int("  Nova quantidade (kg, >= 0): ", 0)
    executar(m.alterar_quantidade, m.produtos[n - 1], nova)


def acao_ver_proprios_produtos(m):
    print()
    produtos = m.consultar_proprios_produtos()
    if not produtos:
        print(vermelho("  Nenhum produto cadastrado."))
        return
    print(f"  {negrito(f'{len(produtos)} produto(s):')}")
    for p in produtos:
        print(f"    - {formatar_produto(p, mostrar_empresa=False)}")
    print(f"  {dim('(RN12/P25: a marisqueira vê apenas os próprios produtos.)')}")


def acao_ver_pedidos_recebidos(m):
    print()
    if not m.pedidos_recebidos:
        print(vermelho("  Nenhum pedido recebido."))
        return
    for i, ped in enumerate(m.pedidos_recebidos, 1):
        print(f"  {amarelo(i)}. Pedido de {magenta(ped.empresa_compradora.nome)}")
        resumo_pedido(ped)


def acao_analisar_pedido(m):
    print()
    pendentes = [p for p in m.pedidos_recebidos if p.aceito is None]
    if not pendentes:
        print(vermelho("  Nenhum pedido pendente de análise."))
        return
    print(f"  {negrito('Pedidos pendentes:')}")
    for i, ped in enumerate(pendentes, 1):
        print(f"    {amarelo(i)}. De {magenta(ped.empresa_compradora.nome)} — "
              f"total {verde(f'R$ {ped.calcular_total():.2f}')}")
    n = ler_int("  Escolha: ", 1, len(pendentes))
    ped = pendentes[n - 1]
    print()
    resumo_pedido(ped)

    print()
    print(f"  {negrito('Ação:')}")
    print(f"    {verde('1')}. {verde(negrito('Aceitar'))}")
    print(f"    {vermelho('2')}. {vermelho(negrito('Rejeitar'))}")
    print(f"    {amarelo('3')}. {amarelo('Solicitar ajuste')}")
    opc = ler_int("  Escolha: ", 1, 3)

    if opc == 1:
        sucesso, _ = executar(m.aceitar_pedido, ped)
        if sucesso:
            print(f"  → status de entrega: {amarelo(ped.status.value)}")
            print(f"  → estoque baixado em cada item (RN08, RN18).")
    elif opc == 2:
        executar(m.rejeitar_pedido, ped)
        print(f"  {dim('(rejeição não movimenta estoque.)')}")
    else:
        msg = ler_texto("  Mensagem de ajuste: ")
        executar(m.solicitar_ajuste, ped, msg)


def acao_atualizar_entrega(m):
    print()
    candidatos = [
        p for p in m.pedidos_recebidos
        if p.aceito is True and p.status != StatusPedido.FINALIZADO
    ]
    if not candidatos:
        print(vermelho("  Nenhum pedido aceito em andamento."))
        return
    print(f"  {negrito('Pedidos em andamento:')}")
    for i, ped in enumerate(candidatos, 1):
        print(f"    {amarelo(i)}. De {magenta(ped.empresa_compradora.nome)} — "
              f"status: {amarelo(ped.status.value)}")
    n = ler_int("  Escolha: ", 1, len(candidatos))
    ped = candidatos[n - 1]

    proximo = {
        StatusPedido.EM_PREPARO: ("EM_CURSO", StatusPedido.EM_CURSO),
        StatusPedido.EM_CURSO:   ("FINALIZADO", StatusPedido.FINALIZADO),
    }
    if ped.status not in proximo:
        print(vermelho("  Este pedido não pode mais avançar."))
        return
    nome_prox, valor_prox = proximo[ped.status]
    print(f"  Status atual: {amarelo(ped.status.value)} → "
          f"próximo permitido: {verde(nome_prox)}")
    if ler_int("  Confirmar? (1=sim / 2=não): ", 1, 2) == 1:
        executar(m.atualizar_status_entrega, ped, valor_prox)


def acao_status_visual(m):
    print()
    print(f"    {amarelo('1')}. Usar a hora atual do sistema")
    print(f"    {amarelo('2')}. Informar hora manualmente")
    opc = ler_int("  Escolha: ", 1, 2)
    if opc == 1:
        hora = None
        s = m.status_visual()
    else:
        hora = ler_int("  Hora (0-23): ", 0, 23)
        s = m.status_visual(hora_atual=hora)

    no_horario = m.esta_no_horario(hora)
    produtos = m.produtos
    vendaveis = [p for p in produtos if p.quantidade_disponivel >= 25]
    abaixo_do_min = [p for p in produtos if 0 < p.quantidade_disponivel < 25]
    zerados = [p for p in produtos if p.quantidade_disponivel == 0]

    if s.value == "verde":
        print(f"  → {verde('VERDE')}: {negrito('DISPONÍVEL')}")
        print(f"     {len(vendaveis)} produto(s) com estoque suficiente (≥ 25 kg):")
        for p in vendaveis:
            print(f"       · {negrito(p.nome)} ({ciano(p.categoria.value)}): "
                  f"{verde(str(p.quantidade_disponivel) + ' kg')}")
    elif s.value == "laranja":
        print(f"  → {amarelo('LARANJA')}: {negrito('ESTOQUE BAIXO')}")
        print(f"     A empresa está no horário, mas nenhum produto atinge o")
        print(f"     mínimo de venda de 25 kg (RN05/RN15).")
        if abaixo_do_min:
            print(f"     Produtos com estoque abaixo de 25 kg:")
            for p in abaixo_do_min:
                faltam = 25 - p.quantidade_disponivel
                print(f"       · {negrito(p.nome)} ({ciano(p.categoria.value)}): "
                      f"{amarelo(str(p.quantidade_disponivel) + ' kg')} "
                      f"(faltam {faltam} kg)")
        if zerados:
            print(f"     Produtos com estoque zerado (indisponíveis — RN09):")
            for p in zerados:
                print(f"       · {negrito(p.nome)} ({ciano(p.categoria.value)}): "
                      f"{vermelho('0 kg')}")
        if not produtos:
            print(f"     {dim('(Nenhum produto cadastrado.)')}")
    else:
        abertura, fechamento = m.horario_funcionamento
        print(f"  → {vermelho('VERMELHO')}: {negrito('FORA DO HORÁRIO')}")
        print(f"     Horário de funcionamento: {abertura}h às {fechamento}h.")
    print(f"     {dim('(RN20/P33)')}")


# ===========================================================================
# Ações da Compradora
# ===========================================================================
def todos_os_produtos(sessao):
    return [p for m in sessao.marisqueiras for p in m.produtos]


def acao_consultar_produtos(c, sessao):
    print()
    todos = todos_os_produtos(sessao)
    if not todos:
        print(vermelho("  Nenhum produto cadastrado no sistema."))
        return

    print(f"  {negrito('Filtros (Enter para ignorar):')}")
    nome = ler_texto("    Nome contém: ", obrigatorio=False) or None
    print(f"    {negrito('Categoria:')}")
    print(f"      {amarelo('0')}. Todas")
    print(f"      {amarelo('1')}. Fresco")
    print(f"      {amarelo('2')}. Congelado")
    cat_opc = ler_int("    Escolha: ", 0, 2)
    categoria = {1: CategoriaProduto.FRESCO, 2: CategoriaProduto.CONGELADO}.get(cat_opc)
    local = ler_texto("    Localização: ", obrigatorio=False) or None

    print(f"    {negrito('Ordenar por:')}")
    print(f"      {amarelo('0')}. Sem ordenação")
    print(f"      {amarelo('1')}. Menor preço")
    print(f"      {amarelo('2')}. Maior preço")
    print(f"      {amarelo('3')}. Melhor avaliação")
    print(f"      {amarelo('4')}. Localização")
    ord_opc = ler_int("    Escolha: ", 0, 4)
    ordenar = {0: None, 1: "menor_preco", 2: "maior_preco",
               3: "melhor_avaliacao", 4: "localizacao"}[ord_opc]

    resultado = c.consultar_produtos(
        todos, nome=nome, categoria=categoria,
        localizacao=local, ordenar_por=ordenar,
    )
    print()
    if not resultado:
        print(vermelho("  Nenhum produto corresponde aos filtros."))
        return
    print(f"  {negrito(f'{len(resultado)} resultado(s):')}")
    for p in resultado:
        aval = p.empresa.media_avaliacoes()
        estrelas = amarelo(f"{aval:.1f}★")
        print(f"    - {formatar_produto(p)} | {estrelas}")


def acao_comparar_produtos(c, sessao):
    print()
    todos = todos_os_produtos(sessao)
    if len(todos) < 2:
        print(vermelho("  Precisa de pelo menos 2 produtos cadastrados."))
        return
    print(f"  {negrito('Produtos disponíveis:')}")
    for i, p in enumerate(todos, 1):
        print(f"    {amarelo(i)}. {formatar_produto(p)}")
    a = ler_int("  Primeiro produto: ", 1, len(todos))
    b = ler_int("  Segundo produto: ", 1, len(todos))
    if a == b:
        print(vermelho("  Escolha produtos diferentes."))
        return
    try:
        info = c.comparar_produtos(todos[a - 1], todos[b - 1])
    except ValueError as e:
        print(f"  {vermelho('[BLOQ]')} {e}")
        return
    print()
    for k, v in info.items():
        print(f"  {negrito(k)}: {v}")


def acao_realizar_pedido(c, sessao):
    print()
    m = escolher_marisqueira(sessao)
    if m is None:
        return
    if not m.produtos:
        print(vermelho("  Esta marisqueira não tem produtos cadastrados."))
        return

    endereco = ler_texto("  Endereço de entrega: ")
    tempo = ler_texto("  Tempo de entrega: ")

    itens_dict = {}   # {produto: quantidade_acumulada}
    while True:
        print()
        print(f"  {negrito('Produtos da marisqueira:')}")
        for i, p in enumerate(m.produtos, 1):
            print(f"    {amarelo(i)}. {formatar_produto(p, mostrar_empresa=False)}")
        opc = ler_int("  Adicionar item (número) ou 0 para finalizar: ", 0, len(m.produtos))
        if opc == 0:
            break
        produto = m.produtos[opc - 1]
        qtd = ler_int("  Quantidade (kg): ", 1)
        # Soma à quantidade anterior do MESMO produto (evita bug do total)
        qtd_total = itens_dict.get(produto, 0) + qtd
        try:
            ItemPedido(produto, qtd_total)
            itens_dict[produto] = qtd_total
            if qtd != qtd_total:
                print(f"  {verde('[OK]')} adicionado. Total deste produto: "
                      f"{amarelo(f'{qtd_total} kg')}")
            else:
                print(f"  {verde('[OK]')} item adicionado à lista.")
        except (QuantidadeMinimaError, EstoqueInsuficienteError) as e:
            print(f"  {vermelho('[BLOQ]')} {e}")
            print(f"  {vermelho('→')} {vermelho(explicar_erro(e))}")

    if not itens_dict:
        print(vermelho("\n  Nenhum item válido. Pedido cancelado."))
        return

    itens = list(itens_dict.items())
    total_prev = sum(p.preco * q for p, q in itens)
    print(f"\n  {negrito(f'{len(itens)} item(ns) selecionado(s).')}")
    for p, q in itens:
        print(f"    · {formatar_produto(p, mostrar_empresa=False)} — "
              f"{amarelo(f'{q} kg')}")
    print(f"  {negrito('Total previsto:')} {verde(f'R$ {total_prev:.2f}')}")

    if ler_int("  Confirmar pedido? (1=sim / 2=não): ", 1, 2) != 1:
        print(vermelho("  Pedido cancelado."))
        return

    sucesso, pedido = executar(c.realizar_pedido, m, endereco, tempo, itens)
    if sucesso:
        print()
        resumo_pedido(pedido)
        print(f"  {dim('→ enviado para a marisqueira analisar (P7).')}")


def acao_ver_meus_pedidos(c):
    print()
    if not c.pedidos_realizados:
        print(vermelho("  Nenhum pedido realizado."))
        return
    for i, ped in enumerate(c.pedidos_realizados, 1):
        print(f"  {amarelo(i)}. Pedido para {ciano(ped.empresa_marisqueira.nome)}")
        resumo_pedido(ped)


def acao_avaliar_empresa(c, sessao):
    print()
    if not sessao.marisqueiras:
        print(vermelho("  Nenhuma marisqueira cadastrada."))
        return
    m = escolher_marisqueira(sessao)
    if m is None:
        return
    nota = ler_int("  Nota (1 a 5): ", 1, 5)
    comentario = ler_texto("  Comentário (opcional, Enter para vazio): ", obrigatorio=False)
    sucesso, av = executar(c.avaliar_empresa, m, nota, comentario or None)
    if sucesso:
        print(f"  → média atual da marisqueira: "
              f"{amarelo(f'{m.media_avaliacoes():.2f}★')}")


# ===========================================================================
# Menus
# ===========================================================================
def menu_marisqueira(sessao):
    m = sessao.marisqueira_atual
    while True:
        print()
        sep(verde)
        print(verde(negrito(f"  MARISQUEIRA: {m.nome} ({m.localizacao})".center(WIDTH))))
        sep(verde)
        print(f"    {amarelo('1')}. Cadastrar produto")
        print(f"    {amarelo('2')}. Alterar quantidade de um produto")
        print(f"    {amarelo('3')}. Ver meus produtos")
        print(f"    {amarelo('4')}. Ver pedidos recebidos")
        print(f"    {amarelo('5')}. Analisar pedido (aceitar/rejeitar/ajustar)")
        print(f"    {amarelo('6')}. Atualizar status de entrega")
        print(f"    {amarelo('7')}. Ver status visual "
              f"({verde('verde')}/{amarelo('laranja')}/{vermelho('vermelho')})")
        print(f"    {vermelho('0')}. {vermelho('Voltar')}")
        sep(verde)
        opc = ler_int("  Escolha: ", 0, 7)
        if opc == 0:
            sessao.marisqueira_atual = None
            return
        elif opc == 1: acao_cadastrar_produto(m)
        elif opc == 2: acao_alterar_quantidade(m)
        elif opc == 3: acao_ver_proprios_produtos(m)
        elif opc == 4: acao_ver_pedidos_recebidos(m)
        elif opc == 5: acao_analisar_pedido(m)
        elif opc == 6: acao_atualizar_entrega(m)
        elif opc == 7: acao_status_visual(m)


def menu_compradora(sessao):
    c = sessao.compradora_atual
    while True:
        print()
        sep(magenta)
        print(magenta(negrito(f"  COMPRADORA: {c.nome} ({c.localizacao})".center(WIDTH))))
        sep(magenta)
        print(f"    {amarelo('1')}. Consultar produtos")
        print(f"    {amarelo('2')}. Comparar dois produtos")
        print(f"    {amarelo('3')}. Realizar pedido")
        print(f"    {amarelo('4')}. Ver meus pedidos")
        print(f"    {amarelo('5')}. Avaliar marisqueira")
        print(f"    {vermelho('0')}. {vermelho('Voltar')}")
        sep(magenta)
        opc = ler_int("  Escolha: ", 0, 5)
        if opc == 0:
            sessao.compradora_atual = None
            return
        elif opc == 1: acao_consultar_produtos(c, sessao)
        elif opc == 2: acao_comparar_produtos(c, sessao)
        elif opc == 3: acao_realizar_pedido(c, sessao)
        elif opc == 4: acao_ver_meus_pedidos(c)
        elif opc == 5: acao_avaliar_empresa(c, sessao)


def menu_principal():
    sessao = Sessao()
    while True:
        print()
        sep(ciano)
        print(ciano(negrito("  SIMULADOR — MARISQUEIRAS DA ILHA".center(WIDTH))))
        sep(ciano)
        print(f"    {amarelo('1')}. Cadastrar empresa")
        print(f"    {amarelo('2')}. Entrar como {verde('Marisqueira')}")
        print(f"    {amarelo('3')}. Entrar como {magenta('Compradora')}")
        print(f"    {amarelo('4')}. Ver empresas cadastradas")
        print(f"    {vermelho('0')}. {vermelho('Sair')}")
        sep(ciano)
        opc = ler_int("  Escolha: ", 0, 4)
        if opc == 0:
            print(verde("\n  Até logo!\n"))
            return
        elif opc == 1:
            cadastrar_empresa(sessao)
        elif opc == 2:
            m = escolher_marisqueira(sessao)
            if m:
                sessao.marisqueira_atual = m
                menu_marisqueira(sessao)
        elif opc == 3:
            c = escolher_compradora(sessao)
            if c:
                sessao.compradora_atual = c
                menu_compradora(sessao)
        elif opc == 4:
            print()
            print(f"  {negrito('Marisqueiras:')}")
            if not sessao.marisqueiras:
                print(f"    {dim('(nenhuma)')}")
            for m in sessao.marisqueiras:
                print(f"    - {ciano(m.nome)} ({m.localizacao})")
            print(f"  {negrito('Compradoras:')}")
            if not sessao.compradoras:
                print(f"    {dim('(nenhuma)')}")
            for c in sessao.compradoras:
                print(f"    - {magenta(c.nome)} ({c.localizacao})")


if __name__ == "__main__":
    menu_principal()