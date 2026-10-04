"""Casos de uso da aplicação.

ServicoBaixa não sabe de onde vêm os dados, que dia é hoje nem como o aviso é
enviado: recebe essas três dependências prontas (injeção de dependência). É isso
que permite testá-lo sem banco, sem esperar o tempo passar e sem enviar nada.
"""
import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app import regras


class TituloNaoEncontradoError(LookupError):
    pass


@dataclass(frozen=True)
class ResultadoBaixa:
    encargos: Decimal
    total_pago: Decimal
    saldo_restante: Decimal
    status: str


class RelogioSistema:
    def hoje(self) -> date:
        return date.today()


class NotificadorLog:
    """Em produção seria um envio de e-mail. Aqui, só registra no log."""

    def titulo_quitado(self, titulo_id: int, descricao: str) -> None:
        logging.getLogger("contas").info("Título %s quitado: %s", titulo_id, descricao)


class ServicoBaixa:
    def __init__(self, repositorio, relogio, notificador):
        self.repositorio = repositorio
        self.relogio = relogio
        self.notificador = notificador

    def baixar(self, titulo_id: int, valor: Decimal,
               data_pagamento: date | None = None) -> ResultadoBaixa:
        """Registra uma baixa total ou parcial.

        Sem data_pagamento, usa a data de hoje informada pelo relógio.
        """
        titulo = self.repositorio.buscar_titulo(titulo_id)
        if titulo is None:
            raise TituloNaoEncontradoError(f"Título {titulo_id} não encontrado.")

        regras.validar_baixa(titulo["saldo"], titulo["status"], valor)

        pagamento = data_pagamento or self.relogio.hoje()
        encargos = regras.calcular_encargos(valor, titulo["vencimento"], pagamento)
        self.repositorio.registrar_baixa(titulo_id, valor, encargos, pagamento)

        saldo_restante = titulo["saldo"] - valor
        status = regras.novo_status(titulo["valor"], saldo_restante)
        self.repositorio.atualizar_status(titulo_id, status)

        if status == "quitado":
            self.notificador.titulo_quitado(titulo_id, titulo["descricao"])

        return ResultadoBaixa(encargos, valor + encargos, saldo_restante, status)
