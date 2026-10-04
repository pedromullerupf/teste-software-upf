# Playbook da aula 2: testes unitários das regras

Copie e cole cada bloco, na ordem. Exercícios completos: [`docs/aulas/aula2.md`](../aulas/aula2.md).

## 1. Chegar à versão desta aula

Escolha **um** dos caminhos.

### Caminho A: mesma máquina, a pasta da aula passada ainda existe

Abra o terminal dentro da pasta `teste-software-upf` e rode:

<!-- caminho: A -->
```bash
git add -A
git commit --allow-empty -m "Meu trabalho antes da aula 2"
git fetch turma
git merge -X theirs turma/aula-2 -m "Atualiza para a aula 2"
```

`-X theirs` significa: se você e a versão oficial mexeram no mesmo trecho, vale o oficial.
Os seus arquivos de teste não são tocados.

### Caminho B: máquina zerada

<!-- caminho: B -->
```bash
git clone -o turma -b aula-2 https://github.com/pedromullerupf/teste-software-upf.git
cd teste-software-upf
git switch -c meu-trabalho
git config user.name "Seu Nome"
git config user.email "seu.email@upf.br"
```

Se você guardou o trabalho no seu GitHub na aula passada, clone o **seu** repositório no lugar do oficial
e depois traga a versão da aula:

<!-- manual -->
```bash
git clone -o meu -b meu-trabalho https://github.com/SEU-USUARIO/contas-upf.git teste-software-upf
cd teste-software-upf
git remote add turma https://github.com/pedromullerupf/teste-software-upf.git
git fetch turma
git merge -X theirs turma/aula-2 -m "Atualiza para a aula 2"
```

## 2. Subir o ambiente e conferir

```bash
docker compose up -d
```

<!-- espera: qualquer -->
```bash
docker compose run --rm testes pytest -v
```

Se você trouxe da aula 1 testes que apontam defeitos, eles continuam falhando. É o esperado: os
defeitos ainda estão no código.

O que chegou de novo: a pasta `defeitos/regras/` (dez versões defeituosas das regras) e o
`validar_testes.py`, que mede a qualidade dos seus testes.

## 3. Testes parametrizados de encargos

Substitua o conteúdo de `tests/unit/test_regras.py` por este ponto de partida
(se quiser manter os seus testes da aula 1, cole-os no fim do arquivo depois):

<!-- arquivo: tests/unit/test_regras.py -->
```python
from datetime import date
from decimal import Decimal

import pytest

from app.regras import (
    RegraVioladaError,
    calcular_encargos,
    gerar_parcelas,
    proximo_dia_util,
    validar_titulo,
)

VENCIMENTO = date(2026, 11, 10)   # terça-feira


def test_vencimento_no_sabado_e_prorrogado_para_segunda():
    sabado = date(2026, 10, 10)

    resultado = proximo_dia_util(sabado)

    assert resultado == date(2026, 10, 12)


def test_vencimento_em_dia_util_nao_muda():
    sexta = date(2026, 10, 9)

    resultado = proximo_dia_util(sexta)

    assert resultado == sexta


@pytest.mark.parametrize("pagamento, esperado", [
    (date(2026, 11, 10), Decimal("0.00")),    # no dia do vencimento
    (date(2026, 11, 11), Decimal("20.33")),   # 1 dia de atraso
    (date(2026, 12, 10), Decimal("29.90")),   # 30 dias de atraso
])
def test_encargos_sobre_titulo_de_mil_reais(pagamento, esperado):
    valor = Decimal("1000.00")

    encargos = calcular_encargos(valor, VENCIMENTO, pagamento)

    assert encargos == esperado
```

<!-- espera: falha -->
<!-- contem: 1 failed, 4 passed -->
```bash
docker compose run --rm testes pytest -v tests/unit/test_regras.py
```

Resultado esperado: `1 failed, 4 passed`. O caso "no dia do vencimento" falha por causa de um defeito da aula 1.

## 4. Parcelas e exceções

Acrescente ao fim de `tests/unit/test_regras.py`:

<!-- acrescentar: tests/unit/test_regras.py -->
```python
@pytest.mark.parametrize("quantidade", [0, -1])
def test_quantidade_de_parcelas_invalida_e_rejeitada(quantidade):
    with pytest.raises(RegraVioladaError):
        gerar_parcelas(Decimal("100.00"), quantidade)


def test_tipo_desconhecido_e_rejeitado_com_mensagem_clara():
    with pytest.raises(RegraVioladaError, match="pagar"):
        validar_titulo("emprestar", "Aluguel", Decimal("10.00"))


def test_titulo_valido_e_aceito():
    validar_titulo("receber", "Mensalidade", Decimal("0.01"))


@pytest.mark.parametrize("valor, quantidade, esperado", [
    ("100.00", 1, ["100.00"]),
    ("100.00", 3, ["33.34", "33.33", "33.33"]),
])
def test_parcelas_com_resto_na_primeira(valor, quantidade, esperado):
    parcelas = gerar_parcelas(Decimal(valor), quantidade)

    assert parcelas == [Decimal(p) for p in esperado]
```

<!-- espera: falha -->
<!-- contem: 2 failed, 9 passed -->
```bash
docker compose run --rm testes pytest -v tests/unit/test_regras.py
```

Resultado esperado: `2 failed, 9 passed`. As duas falhas são dois dos cinco defeitos da aula 1.

## 5. Corrigir os defeitos que os testes apontam

Em `app/regras.py`, função `calcular_encargos`: pagamento no dia do vencimento não tem encargos.

<!-- editar: app/regras.py -->
```diff
-    if pagamento < vencimento_efetivo:
+    if pagamento <= vencimento_efetivo:
```

Em `app/regras.py`, função `gerar_parcelas`: o resto da divisão vai para a primeira parcela.

<!-- editar: app/regras.py -->
```diff
-    return [parcela] * quantidade
+    resto = valor - parcela * quantidade
+    return [parcela + resto] + [parcela] * (quantidade - 1)
```

<!-- contem: 11 passed -->
```bash
docker compose run --rm testes pytest -v tests/unit/test_regras.py
```

Resultado esperado: `11 passed`.

Ainda há três defeitos da aula 1 em `validar_titulo` e `validar_baixa`. Escreva o teste de cada um
(ele falha), corrija o código (ele passa).

## 6. Medir a qualidade dos seus testes

O `validar_testes.py` roda a sua suíte contra dez versões das regras, cada uma com um defeito.
Teste bom é o que falha quando o código está errado.

<!-- contem: Placar: 5 de 10 defeitos detectados. -->
```bash
docker compose run --rm testes python validar_testes.py
```

Resultado esperado com os testes deste playbook (o seu placar sobe conforme você escreve mais testes):

```text
Placar: 5 de 10 defeitos detectados.
Escaparam dos seus testes: d02, d03, d04, d08, d10
```

Para cada defeito que escapou, abra `defeitos/regras/dNN.py`, entenda o defeito e escreva o teste que faltava.

Se aparecer "Sua suíte falha com o código atual", algum teste seu está vermelho: deixe tudo verde antes de validar.

## 7. Guardar o trabalho e encerrar

```bash
git add -A
git commit -m "Aula 2: testes unitários das regras"
docker compose stop
```

Se você usa o seu repositório no GitHub:

<!-- manual -->
```bash
git push meu meu-trabalho
```
