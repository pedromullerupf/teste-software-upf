"""Fixtures dos testes de ponta a ponta (Playwright).

Os testes E2E usam a aplicação que está no ar (docker compose up), e por isso
gravam no banco de DESENVOLVIMENTO. As tabelas são esvaziadas antes de cada teste.

    BASE_URL           endereço da aplicação (padrão: http://localhost:8000)
    DATABASE_URL_E2E   banco usado pela aplicação (padrão: o DATABASE_URL)
"""
import os

import psycopg
import pytest

from app.config import DATABASE_URL

USUARIO = os.environ.get("USUARIO", "admin")
SENHA = os.environ.get("SENHA", "admin123")


@pytest.fixture(scope="session")
def base_url():
    return os.environ.get("BASE_URL", "http://localhost:8000")


@pytest.fixture(autouse=True)
def banco_limpo():
    with psycopg.connect(os.environ.get("DATABASE_URL_E2E", DATABASE_URL)) as conexao:
        conexao.execute("TRUNCATE baixas, titulos RESTART IDENTITY")
