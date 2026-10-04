"""API REST em JSON. Valores monetários trafegam como texto ("600.00") e datas em ISO."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify, request

from app import regras
from app.formularios import ler_data, ler_valor
from app.regras import RegraVioladaError
from app.servicos import TituloNaoEncontradoError


def _serializar(dados: dict) -> dict:
    convertido = {}
    for chave, valor in dados.items():
        if isinstance(valor, Decimal):
            convertido[chave] = f"{valor:.2f}"
        elif isinstance(valor, date):
            convertido[chave] = valor.isoformat()
        else:
            convertido[chave] = valor
    return convertido


def criar_api(repositorio, servico_baixa) -> Blueprint:
    api = Blueprint("api", __name__, url_prefix="/api")

    @api.errorhandler(RegraVioladaError)
    def regra_violada(erro):
        return jsonify(erro=str(erro)), 400

    @api.errorhandler(TituloNaoEncontradoError)
    def nao_encontrado(erro):
        return jsonify(erro=str(erro)), 404

    @api.get("/titulos")
    def listar():
        return jsonify([_serializar(t) for t in repositorio.listar_titulos()])

    @api.post("/titulos")
    def criar():
        dados = request.get_json(silent=True) or {}
        tipo = str(dados.get("tipo", ""))
        descricao = str(dados.get("descricao", ""))
        valor = ler_valor(str(dados.get("valor", "")))
        vencimento = ler_data(str(dados.get("vencimento", "")))
        regras.validar_titulo(tipo, descricao, valor)
        titulo_id = repositorio.criar_titulo(
            tipo, descricao.strip(), str(dados.get("pessoa", "")).strip(), valor, vencimento
        )
        return jsonify(_serializar(repositorio.buscar_titulo(titulo_id))), 201

    @api.get("/titulos/<int:titulo_id>")
    def buscar(titulo_id):
        titulo = repositorio.buscar_titulo(titulo_id)
        if titulo is None:
            raise TituloNaoEncontradoError(f"Título {titulo_id} não encontrado.")
        return jsonify(_serializar(titulo))

    @api.post("/titulos/<int:titulo_id>/baixas")
    def baixar(titulo_id):
        dados = request.get_json(silent=True) or {}
        valor = ler_valor(str(dados.get("valor", "")))
        pagamento = ler_data(str(dados["data_pagamento"])) if dados.get("data_pagamento") else None
        resultado = servico_baixa.baixar(titulo_id, valor, pagamento)
        return jsonify(_serializar(vars(resultado))), 201

    @api.get("/fluxo-caixa")
    def fluxo_caixa():
        inicio = ler_data(request.args.get("inicio"))
        fim = ler_data(request.args.get("fim"))
        saldo = repositorio.fluxo_caixa(inicio, fim)
        return jsonify(_serializar({"inicio": inicio, "fim": fim, "saldo_projetado": saldo}))

    return api
