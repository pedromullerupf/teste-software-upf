"""Aplicação web (Flask): login, títulos, baixa e fluxo de caixa, mais a API em /api."""
import os
from datetime import timedelta

from flask import Flask, flash, redirect, render_template, request, session, url_for

from app import regras
from app.api import criar_api
from app.config import DATABASE_URL
from app.formularios import ler_data, ler_inteiro, ler_valor
from app.regras import RegraVioladaError
from app.repositorio import RepositorioPostgres
from app.servicos import (
    NotificadorLog,
    RelogioSistema,
    ServicoBaixa,
    TituloNaoEncontradoError,
)

USUARIO = os.environ.get("USUARIO", "admin")
SENHA = os.environ.get("SENHA", "admin123")
ROTAS_SEM_LOGIN = ("login", "entrar", "static")


def criar_app(database_url: str = DATABASE_URL, relogio=None) -> Flask:
    app = Flask(__name__)
    app.secret_key = "chave-apenas-para-aula"
    repositorio = RepositorioPostgres(database_url)
    relogio = relogio or RelogioSistema()
    servico_baixa = ServicoBaixa(repositorio, relogio, NotificadorLog())
    app.register_blueprint(criar_api(repositorio, servico_baixa))

    @app.before_request
    def exigir_login():
        rota = request.endpoint or ""
        if rota in ROTAS_SEM_LOGIN or rota.startswith("api."):
            return None
        if not session.get("usuario"):
            return redirect(url_for("login"))
        return None

    @app.get("/login")
    def login():
        return render_template("login.html")

    @app.post("/login")
    def entrar():
        if request.form.get("usuario") == USUARIO and request.form.get("senha") == SENHA:
            session["usuario"] = USUARIO
            return redirect(url_for("listar_titulos"))
        flash("Usuário ou senha inválidos.", "erro")
        return render_template("login.html"), 401

    @app.post("/sair")
    def sair():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/fluxo-caixa")
    def fluxo_caixa():
        hoje = relogio.hoje()
        try:
            inicio = ler_data(request.args.get("inicio") or hoje.replace(day=1).isoformat())
            fim = ler_data(request.args.get("fim") or (inicio + timedelta(days=30)).isoformat())
        except RegraVioladaError as erro:
            flash(str(erro), "erro")
            return redirect(url_for("fluxo_caixa"))
        return render_template(
            "fluxo.html", inicio=inicio, fim=fim, saldo=repositorio.fluxo_caixa(inicio, fim)
        )

    @app.get("/")
    def listar_titulos():
        return render_template("titulos.html", titulos=repositorio.listar_titulos())

    @app.get("/titulos/novo")
    def formulario_titulo():
        return render_template("titulo_novo.html", dados={})

    @app.post("/titulos/novo")
    def criar_titulo():
        dados = request.form
        try:
            tipo = dados.get("tipo", "")
            descricao = dados.get("descricao", "")
            valor = ler_valor(dados.get("valor"))
            vencimento = ler_data(dados.get("vencimento"))
            quantidade = ler_inteiro(dados.get("parcelas"))
            regras.validar_titulo(tipo, descricao, valor)
            parcelas = regras.gerar_parcelas(valor, quantidade)
            vencimentos = regras.vencimentos_das_parcelas(vencimento, quantidade)
        except RegraVioladaError as erro:
            flash(str(erro), "erro")
            return render_template("titulo_novo.html", dados=dados), 400

        for numero, (valor_parcela, data) in enumerate(zip(parcelas, vencimentos), start=1):
            sufixo = f" ({numero}/{quantidade})" if quantidade > 1 else ""
            repositorio.criar_titulo(
                tipo, descricao.strip() + sufixo, dados.get("pessoa", "").strip(),
                valor_parcela, data,
            )
        flash("Título cadastrado.", "sucesso")
        return redirect(url_for("listar_titulos"))

    @app.get("/titulos/<int:titulo_id>/baixa")
    def formulario_baixa(titulo_id):
        titulo = repositorio.buscar_titulo(titulo_id)
        if titulo is None:
            flash("Título não encontrado.", "erro")
            return redirect(url_for("listar_titulos"))
        return render_template(
            "baixa.html", titulo=titulo, baixas=repositorio.listar_baixas(titulo_id),
            hoje=relogio.hoje().isoformat(),
        )

    @app.post("/titulos/<int:titulo_id>/baixa")
    def registrar_baixa(titulo_id):
        try:
            valor = ler_valor(request.form.get("valor"))
            pagamento = ler_data(request.form.get("data_pagamento"))
            resultado = servico_baixa.baixar(titulo_id, valor, pagamento)
        except TituloNaoEncontradoError:
            flash("Título não encontrado.", "erro")
            return redirect(url_for("listar_titulos"))
        except RegraVioladaError as erro:
            flash(str(erro), "erro")
            return redirect(url_for("formulario_baixa", titulo_id=titulo_id))

        flash(f"Baixa registrada. Encargos por atraso: R$ {resultado.encargos:.2f}.", "sucesso")
        return redirect(url_for("formulario_baixa", titulo_id=titulo_id))

    @app.post("/titulos/<int:titulo_id>/cancelar")
    def cancelar_titulo(titulo_id):
        repositorio.atualizar_status(titulo_id, "cancelado")
        flash("Título cancelado.", "sucesso")
        return redirect(url_for("listar_titulos"))

    return app


app = criar_app()
