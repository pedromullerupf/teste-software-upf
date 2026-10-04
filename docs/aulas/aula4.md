# Aula 4: Integração e testes no banco de dados

> Passo a passo para copiar e colar: [`docs/playbooks/aula-4.md`](../playbooks/aula-4.md).

Novidades desta versão:

- `db/migrations/003_funcoes.sql`: funções e triggers no PostgreSQL.
- `app/api.py`: API REST em `/api`.
- `tests/conftest.py`: fixtures `conexao` e `cliente`, ambas ligadas ao banco de teste.
- `defeitos/banco/`: versões defeituosas das funções do banco.

Depois de atualizar o projeto, reinicie a aplicação para aplicar as migrações:

```
docker compose restart app
```

## Exercício 0: a suíte antiga ainda passa?

Rode todos os testes das aulas anteriores nesta versão. Algo mudou?
Descubra o que foi, em que arquivo, e corrija.

## Exercício 1: funções e triggers (`tests/banco/test_funcoes.py`)

Use a fixture `conexao`. Leia `db/migrations/003_funcoes.sql` e derive os casos:

| Objeto | Casos a cobrir |
|---|---|
| Restrição `titulos_valor_positivo` | zero, negativo, um centavo |
| `fn_saldo_titulo(id)` | sem baixas, uma baixa parcial, várias baixas, quitado, id inexistente |
| Trigger `trg_valida_baixa` | baixa igual ao saldo, um centavo acima, valor zero, título cancelado, título quitado |
| Trigger `trg_atualiza_status` | aberto para parcial, parcial para quitado |
| `fn_fluxo_caixa(inicio, fim)` | período vazio, só a pagar, só a receber, título na data limite, cancelados e quitados fora da conta |

Erros esperados: `psycopg.errors.CheckViolation` para a restrição e
`psycopg.errors.RaiseException` para os triggers.

Atenção: depois de um erro, o PostgreSQL aborta a transação inteira. Qualquer comando
seguinte na mesma conexão falha até um `rollback`.

## Exercício 2: a mesma regra em dois lugares

A regra de encargos existe em `app/regras.py` e em `fn_encargos` no banco.
Escreva um teste parametrizado que chama as duas com as mesmas entradas e compara os
resultados. Inclua valores "quebrados" e vencimentos em fim de semana.

## Exercício 3: API (`tests/integracao/test_api.py`)

Use a fixture `cliente`.

| Método e rota | Corpo | Resposta |
|---|---|---|
| `GET /api/titulos` | | 200, lista |
| `POST /api/titulos` | `tipo`, `descricao`, `pessoa`, `valor`, `vencimento` | 201 com o título, ou 400 com `erro` |
| `GET /api/titulos/<id>` | | 200, ou 404 |
| `POST /api/titulos/<id>/baixas` | `valor`, `data_pagamento` (opcional) | 201 com `encargos`, `total_pago`, `saldo_restante`, `status`; 400 ou 404 |
| `GET /api/fluxo-caixa?inicio=AAAA-MM-DD&fim=AAAA-MM-DD` | | 200 com `saldo_projetado` |

Em cada teste, confira três coisas: o código de status, o corpo da resposta e o estado
que ficou gravado (consultando de novo pela API).

## Exercício 4: camadas e placar

```
docker compose run --rm testes pytest -m unit
docker compose run --rm testes pytest -m banco
docker compose run --rm testes pytest -m integracao
docker compose run --rm testes python validar_testes.py banco
```

Compare os tempos de cada camada.
