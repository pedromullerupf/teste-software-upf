"""Regras de negócio do contas a pagar e a receber.

Só funções puras: recebem valores, devolvem valores, não tocam em banco nem em relógio.
A descrição de cada regra está em docs/regras_de_negocio.md.
"""
from datetime import date, timedelta
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

MULTA = Decimal("0.02")            # 2% sobre o valor pago em atraso
JUROS_AO_DIA = Decimal("0.00033")  # 0,033% ao dia
CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")

TIPOS = ("pagar", "receber")
STATUS_QUE_ACEITAM_BAIXA = ("aberto", "parcial")


class RegraVioladaError(ValueError):
    """Uma regra de negócio foi violada. A mensagem é mostrada ao usuário."""


def proximo_dia_util(data: date) -> date:
    """Regra 5: sábado e domingo são prorrogados para a segunda-feira."""
    while data.weekday() >= 5:
        data += timedelta(days=1)
    return data


def calcular_encargos(valor: Decimal, vencimento: date, pagamento: date) -> Decimal:
    """Regra 4: multa de 2% mais juros de 0,033% ao dia, só para pagamento em atraso."""
    vencimento_efetivo = proximo_dia_util(vencimento)
    if pagamento <= vencimento_efetivo:
        return ZERO
    dias_de_atraso = (pagamento - vencimento_efetivo).days
    encargos = valor * MULTA + valor * JUROS_AO_DIA * dias_de_atraso
    return encargos.quantize(CENTAVO, rounding=ROUND_DOWN)


def gerar_parcelas(valor: Decimal, quantidade: int) -> list[Decimal]:
    """Regra 6: a soma das parcelas é o valor original; o resto vai para a primeira."""
    if quantidade < 1:
        raise RegraVioladaError("A quantidade de parcelas deve ser pelo menos 1.")
    parcela = (valor / quantidade).quantize(CENTAVO, rounding=ROUND_DOWN)
    parcelas = [parcela] * quantidade
    parcelas[0] += valor - parcela * quantidade
    return parcelas


def vencimentos_das_parcelas(primeiro_vencimento: date, quantidade: int) -> list[date]:
    """As parcelas vencem de 30 em 30 dias a partir do primeiro vencimento."""
    return [primeiro_vencimento + timedelta(days=30 * i) for i in range(quantidade)]


def validar_titulo(tipo: str, descricao: str, valor: Decimal) -> None:
    """Regra 1 e campos obrigatórios. Levanta RegraVioladaError se algo estiver errado."""
    if tipo not in TIPOS:
        raise RegraVioladaError("O tipo deve ser 'pagar' ou 'receber'.")
    if not descricao.strip():
        raise RegraVioladaError("A descrição é obrigatória.")
    if valor <= 0:
        raise RegraVioladaError("O valor do título deve ser maior que zero.")


def validar_baixa(saldo: Decimal, status: str, valor: Decimal) -> None:
    """Regra 3: a baixa não pode exceder o saldo nem ocorrer em título cancelado ou quitado."""
    if status not in STATUS_QUE_ACEITAM_BAIXA:
        raise RegraVioladaError(f"Título {status} não pode receber baixa.")
    if valor <= 0:
        raise RegraVioladaError("O valor da baixa deve ser maior que zero.")
    if valor > saldo:
        raise RegraVioladaError("O valor da baixa não pode ser maior que o saldo do título.")


def novo_status(valor_do_titulo: Decimal, saldo_restante: Decimal) -> str:
    """Regra 2: status do título depois de uma baixa."""
    if saldo_restante == 0:
        return "quitado"
    if saldo_restante < valor_do_titulo:
        return "parcial"
    return "aberto"
