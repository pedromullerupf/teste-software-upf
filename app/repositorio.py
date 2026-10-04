"""Acesso ao PostgreSQL. Todo o SQL da aplicação fica aqui, à vista."""
from datetime import date
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row

_SELECT_TITULO = """
    SELECT t.id, t.tipo, t.descricao, t.pessoa, t.valor, t.vencimento, t.status,
           t.valor - COALESCE(SUM(b.valor), 0) AS saldo
      FROM titulos t
      LEFT JOIN baixas b ON b.titulo_id = t.id
"""


class RepositorioPostgres:
    def __init__(self, url: str):
        self.url = url

    def _conectar(self):
        return psycopg.connect(self.url, row_factory=dict_row)

    def criar_titulo(self, tipo: str, descricao: str, pessoa: str,
                     valor: Decimal, vencimento: date) -> int:
        with self._conectar() as conexao:
            linha = conexao.execute(
                "INSERT INTO titulos (tipo, descricao, pessoa, valor, vencimento) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (tipo, descricao, pessoa, valor, vencimento),
            ).fetchone()
            return linha["id"]

    def listar_titulos(self) -> list[dict]:
        with self._conectar() as conexao:
            return conexao.execute(
                _SELECT_TITULO + " GROUP BY t.id ORDER BY t.vencimento, t.id"
            ).fetchall()

    def buscar_titulo(self, titulo_id: int) -> dict | None:
        with self._conectar() as conexao:
            return conexao.execute(
                _SELECT_TITULO + " WHERE t.id = %s GROUP BY t.id", (titulo_id,)
            ).fetchone()

    def listar_baixas(self, titulo_id: int) -> list[dict]:
        with self._conectar() as conexao:
            return conexao.execute(
                "SELECT id, valor, encargos, data_baixa FROM baixas "
                "WHERE titulo_id = %s ORDER BY id",
                (titulo_id,),
            ).fetchall()

    def registrar_baixa(self, titulo_id: int, valor: Decimal,
                        encargos: Decimal, data_baixa: date) -> int:
        with self._conectar() as conexao:
            linha = conexao.execute(
                "INSERT INTO baixas (titulo_id, valor, encargos, data_baixa) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (titulo_id, valor, encargos, data_baixa),
            ).fetchone()
            return linha["id"]

    def atualizar_status(self, titulo_id: int, status: str) -> None:
        with self._conectar() as conexao:
            conexao.execute(
                "UPDATE titulos SET status = %s WHERE id = %s", (status, titulo_id)
            )

    def fluxo_caixa(self, inicio: date, fim: date) -> Decimal:
        """Regra 7, calculada pela função fn_fluxo_caixa do banco."""
        with self._conectar() as conexao:
            linha = conexao.execute(
                "SELECT fn_fluxo_caixa(%s, %s) AS saldo", (inicio, fim)
            ).fetchone()
            return linha["saldo"]
