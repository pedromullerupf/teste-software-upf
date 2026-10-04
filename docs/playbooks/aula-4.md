# Playbook da aula 4: integração e testes no banco de dados

Copie e cole cada bloco, na ordem. Exercícios completos: [`docs/aulas/aula4.md`](../aulas/aula4.md).

## 1. Chegar à versão desta aula

Escolha **um** dos caminhos.

### Caminho A: mesma máquina, a pasta da aula passada ainda existe

<!-- caminho: A -->
```bash
git add -A
git commit --allow-empty -m "Meu trabalho antes da aula 4"
git fetch turma
git merge -X theirs turma/aula-4 -m "Atualiza para a aula 4"
```

### Caminho B: máquina zerada

<!-- caminho: B -->
```bash
git clone -o turma -b aula-4 https://github.com/pedromullerupf/teste-software-upf.git
cd teste-software-upf
git switch -c meu-trabalho
git config user.name "Seu Nome"
git config user.email "seu.email@upf.br"
```

Com o seu repositório no GitHub:

<!-- manual -->
```bash
git clone -o meu -b meu-trabalho https://github.com/SEU-USUARIO/contas-upf.git teste-software-upf
cd teste-software-upf
git remote add turma https://github.com/pedromullerupf/teste-software-upf.git
git fetch turma
git merge -X theirs turma/aula-4 -m "Atualiza para a aula 4"
```

## 2. Subir o ambiente e aplicar as migrações novas

Esta versão traz funções e triggers no PostgreSQL. A aplicação aplica as migrações ao iniciar,
por isso é preciso reiniciá-la:

```bash
docker compose up -d
docker compose restart app
```

<!-- contem: 003_funcoes.sql -->
```bash
docker compose exec -T db psql -U contas contas -c "SELECT nome FROM migracoes ORDER BY nome"
```

Resultado esperado: `001_tabelas.sql`, `002_restricoes.sql` e `003_funcoes.sql`.

## 3. Exercício 0: a suíte antiga ainda passa?

Crie `tests/unit/test_arredondamento.py` (é o caso de "valor quebrado" pedido na aula 2):

<!-- arquivo: tests/unit/test_arredondamento.py -->
```python
from datetime import date
from decimal import Decimal

from app.regras import calcular_encargos


def test_encargos_arredondam_meio_centavo_para_cima():
    # 150,00 com 1 dia de atraso: 3,00 de multa + 0,0495 de juros = 3,0495 -> 3,05
    encargos = calcular_encargos(Decimal("150.00"), date(2026, 11, 10), date(2026, 11, 11))

    assert encargos == Decimal("3.05")
```

Rode todos os testes unitários, os seus das aulas anteriores e este:

<!-- espera: falha -->
<!-- contem: failed -->
```bash
docker compose run --rm testes pytest -m unit
```

Algo que funcionava deixou de funcionar: é uma **regressão**. Descubra em que arquivo e em que linha
antes de abrir a resposta.

<details>
<summary>Travou? Veja a correção</summary>

Em `app/regras.py`, função `calcular_encargos`, o arredondamento foi trocado por truncamento:

<!-- editar: app/regras.py -->
```diff
-    return encargos.quantize(CENTAVO, rounding=ROUND_DOWN)
+    return encargos.quantize(CENTAVO, rounding=ROUND_HALF_UP)
```

</details>

<!-- contem: passed -->
```bash
docker compose run --rm testes pytest -m unit
```

Resultado esperado: tudo verde de novo.

## 4. Conhecer as funções do banco

<!-- contem: fn_encargos -->
<!-- contem: fn_saldo_titulo -->
```bash
docker compose exec -T db psql -U contas contas_teste -c "\df fn_*"
```

<!-- contem: 20.33 -->
```bash
docker compose exec -T db psql -U contas contas_teste -c "SELECT fn_encargos(1000.00, '2026-11-10', '2026-11-11')"
```

<!-- contem: 2026-11-16 -->
```bash
docker compose exec -T db psql -U contas contas_teste -c "SELECT fn_proximo_dia_util('2026-11-14')"
```

Para um terminal SQL interativo (saia com `\q`):

<!-- manual -->
```bash
docker compose exec db psql -U contas contas_teste
```

## 5. Testes das funções e dos triggers

Crie `tests/banco/test_funcoes.py`. A fixture `conexao` vem de `tests/conftest.py`: abre uma
transação no banco de **teste** e desfaz tudo no fim de cada teste.

<!-- arquivo: tests/banco/test_funcoes.py -->
```python
from datetime import date
from decimal import Decimal

import psycopg
import pytest

from app.regras import calcular_encargos


def novo_titulo(conexao, valor, status="aberto"):
    return conexao.execute(
        "INSERT INTO titulos (tipo, descricao, valor, vencimento, status) "
        "VALUES ('pagar', 'Aluguel', %s, '2026-11-10', %s) RETURNING id",
        (Decimal(valor), status),
    ).fetchone()[0]


def baixar(conexao, titulo_id, valor):
    conexao.execute(
        "INSERT INTO baixas (titulo_id, valor, data_baixa) VALUES (%s, %s, '2026-11-05')",
        (titulo_id, Decimal(valor)),
    )


def test_saldo_desconta_baixa_parcial(conexao):
    titulo_id = novo_titulo(conexao, "1000.00")
    baixar(conexao, titulo_id, "400.00")

    saldo = conexao.execute("SELECT fn_saldo_titulo(%s)", (titulo_id,)).fetchone()[0]

    assert saldo == Decimal("600.00")


def test_trigger_impede_baixa_em_titulo_cancelado(conexao):
    titulo_id = novo_titulo(conexao, "1000.00", status="cancelado")

    with pytest.raises(psycopg.errors.RaiseException):
        baixar(conexao, titulo_id, "100.00")


def test_banco_rejeita_titulo_com_valor_zero(conexao):
    with pytest.raises(psycopg.errors.CheckViolation):
        novo_titulo(conexao, "0.00")


CASOS = [
    ("1000.00", date(2026, 11, 10), date(2026, 11, 10)),   # no vencimento
    ("1000.00", date(2026, 11, 10), date(2026, 11, 11)),   # 1 dia de atraso
    # acrescente valores quebrados e vencimentos em fim de semana
]


@pytest.mark.parametrize("valor, vencimento, pagamento", CASOS)
def test_banco_e_python_calculam_os_mesmos_encargos(conexao, valor, vencimento, pagamento):
    no_banco = conexao.execute(
        "SELECT fn_encargos(%s, %s, %s)", (Decimal(valor), vencimento, pagamento)
    ).fetchone()[0]

    assert no_banco == calcular_encargos(Decimal(valor), vencimento, pagamento)
```

<!-- contem: 5 passed -->
```bash
docker compose run --rm testes pytest -v -m banco
```

Resultado esperado: `5 passed`. Complete com os casos da tabela do roteiro.

## 6. Testes da API

Crie `tests/integracao/test_api.py`. A fixture `cliente` é a aplicação ligada ao banco de teste.

<!-- arquivo: tests/integracao/test_api.py -->
```python
TITULO = {
    "tipo": "receber", "descricao": "Mensalidade", "pessoa": "Cliente A",
    "valor": "1000.00", "vencimento": "2026-11-10",
}


def test_criar_titulo_devolve_201_e_grava_no_banco(cliente):
    resposta = cliente.post("/api/titulos", json=TITULO)

    assert resposta.status_code == 201
    criado = resposta.get_json()
    assert criado["saldo"] == "1000.00"
    assert cliente.get(f"/api/titulos/{criado['id']}").get_json() == criado


def test_baixa_acima_do_saldo_devolve_400_e_nao_altera_o_titulo(cliente):
    titulo_id = cliente.post("/api/titulos", json=TITULO).get_json()["id"]

    resposta = cliente.post(f"/api/titulos/{titulo_id}/baixas", json={"valor": "1000.01"})

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()
    assert cliente.get(f"/api/titulos/{titulo_id}").get_json()["saldo"] == "1000.00"
```

<!-- contem: 2 passed -->
```bash
docker compose run --rm testes pytest -v -m integracao
```

Resultado esperado: `2 passed`.

## 7. Camadas e placar do banco

Compare o tempo de cada camada (última linha de cada execução):

<!-- contem: passed -->
```bash
docker compose run --rm testes pytest -m unit
docker compose run --rm testes pytest -m banco
docker compose run --rm testes pytest -m integracao
```

Placar dos oito defeitos plantados nas funções do banco (`defeitos/banco/`):

<!-- contem: Placar: 2 de 8 defeitos detectados. -->
```bash
docker compose run --rm testes python validar_testes.py banco
```

Resultado esperado com os testes deste playbook (o seu placar sobe conforme você escreve mais testes):

```text
Placar: 2 de 8 defeitos detectados.
Escaparam dos seus testes: b01, b04, b05, b06, b07, b08
```

## 8. Guardar o trabalho e encerrar

```bash
git add -A
git commit -m "Aula 4: testes de banco e de integração"
docker compose stop
```

<!-- manual -->
```bash
git push meu meu-trabalho
```
