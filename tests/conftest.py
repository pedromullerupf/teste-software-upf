"""Configuração compartilhada dos testes.

Cada teste recebe automaticamente o marcador da pasta em que está
(tests/unit -> unit, tests/banco -> banco, e assim por diante), o que permite
rodar só uma camada: pytest -m unit

Fixtures de banco (sempre no banco de TESTE, nunca no de desenvolvimento):

    conexao   conexão com transação aberta, desfeita (rollback) ao fim do teste
    cliente   cliente HTTP da aplicação ligada ao banco de teste, com tabelas limpas
"""
from pathlib import Path

import psycopg
import pytest

from app.banco import aplicar_migracoes
from app.config import DATABASE_URL_TESTE

PASTAS_COM_MARCADOR = ("unit", "banco", "integracao", "e2e", "aceitacao")


def pytest_collection_modifyitems(items):
    raiz = Path(__file__).parent
    for item in items:
        partes = Path(str(item.fspath)).relative_to(raiz).parts
        if partes and partes[0] in PASTAS_COM_MARCADOR:
            item.add_marker(getattr(pytest.mark, partes[0]))


@pytest.fixture(scope="session")
def banco_de_teste():
    """Garante, uma vez por execução, que o banco de teste está com as migrações em dia."""
    aplicar_migracoes(DATABASE_URL_TESTE)
    return DATABASE_URL_TESTE


def _limpar_tabelas(url):
    with psycopg.connect(url) as conexao:
        conexao.execute("TRUNCATE baixas, titulos RESTART IDENTITY")


@pytest.fixture
def conexao(banco_de_teste):
    """Tudo o que o teste gravar por esta conexão é desfeito no final."""
    with psycopg.connect(banco_de_teste) as conexao:
        yield conexao
        conexao.rollback()


@pytest.fixture
def cliente(banco_de_teste):
    """A aplicação grava de verdade (commit); por isso as tabelas são limpas antes e depois."""
    from app.web import criar_app

    _limpar_tabelas(banco_de_teste)
    app = criar_app(banco_de_teste)
    app.testing = True
    yield app.test_client()
    _limpar_tabelas(banco_de_teste)
