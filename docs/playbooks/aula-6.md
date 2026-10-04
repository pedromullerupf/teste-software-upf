# Playbook da aula 6: caixa-preta, TDD, caixa-branca, aceitação e carga

Copie e cole cada bloco, na ordem. Exercícios completos e o enunciado da regra 9:
[`docs/aulas/aula6.md`](../aulas/aula6.md).

## 1. Chegar à versão desta aula

Escolha **um** dos caminhos.

### Caminho A: mesma máquina, a pasta da aula passada ainda existe

<!-- caminho: A -->
```bash
git add -A
git commit --allow-empty -m "Meu trabalho antes da aula 6"
git fetch turma
git merge -X theirs turma/aula-6 -m "Atualiza para a aula 6"
```

### Caminho B: máquina zerada

<!-- caminho: B -->
```bash
git clone -o turma -b aula-6 https://github.com/pedromullerupf/teste-software-upf.git
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
git merge -X theirs turma/aula-6 -m "Atualiza para a aula 6"
```

## 2. Subir o ambiente e conferir que a suíte está verde

```bash
docker compose up -d
docker compose restart app
```

<!-- contem: passed -->
```bash
docker compose run --rm testes pytest
```

Hoje não chega código novo na aplicação. Quem implementa a regra 9 é você, com TDD.

## 3. TDD, ciclo 1: vermelho

Crie `tests/unit/test_desconto.py`. A função `calcular_valor_pagamento` ainda não existe.

<!-- arquivo: tests/unit/test_desconto.py -->
```python
from datetime import date
from decimal import Decimal

from app.regras import calcular_valor_pagamento

VENCIMENTO = date(2026, 11, 10)   # terça-feira


def test_pagamento_no_vencimento_e_valor_cheio():
    valor = calcular_valor_pagamento(Decimal("1000.00"), VENCIMENTO, VENCIMENTO)

    assert valor == Decimal("1000.00")
```

<!-- espera: falha -->
<!-- contem: cannot import name 'calcular_valor_pagamento' -->
```bash
docker compose run --rm testes pytest tests/unit/test_desconto.py
```

Resultado esperado: **vermelho**, com `ImportError: cannot import name 'calcular_valor_pagamento'`.

## 4. TDD, ciclo 1: verde com o mínimo

Acrescente ao fim de `app/regras.py`:

<!-- acrescentar: app/regras.py -->
```python
def calcular_valor_pagamento(valor: Decimal, vencimento: date, pagamento: date) -> Decimal:
    """Regra 9: desconto por antecipação, valor cheio ou valor com encargos."""
    return valor
```

<!-- contem: 1 passed -->
```bash
docker compose run --rm testes pytest tests/unit/test_desconto.py
```

Resultado esperado: `1 passed`. Um commit por ciclo:

```bash
git add -A
git commit -m "Regra 9: pagamento no vencimento paga o valor cheio"
```

## 5. TDD, ciclo 2: vermelho de novo

Acrescente ao fim de `tests/unit/test_desconto.py`:

<!-- acrescentar: tests/unit/test_desconto.py -->
```python
def test_pagamento_com_dez_dias_de_antecedencia_tem_cinco_por_cento_de_desconto():
    valor = calcular_valor_pagamento(Decimal("1000.00"), VENCIMENTO, date(2026, 10, 31))

    assert valor == Decimal("950.00")
```

<!-- espera: falha -->
<!-- contem: 1 failed, 1 passed -->
```bash
docker compose run --rm testes pytest tests/unit/test_desconto.py
```

Resultado esperado: `1 failed, 1 passed`. Agora é com você: escreva o mínimo de código para ficar verde,
refatore, e siga a sua tabela de caixa-preta (9 dias antes, depois do vencimento, vencimento no fim de
semana, arredondamento do desconto). Nenhuma linha de produção sem um teste falhando antes.

## 6. Caixa-branca: há desvio sem teste?

<!-- espera: qualquer -->
<!-- contem: app/regras.py -->
```bash
docker compose run --rm testes pytest tests/unit --cov=app.regras --cov-branch --cov-report=term-missing
```

Olhe a coluna `Missing` nas linhas da função que você acabou de escrever.

## 7. Demonstração: teste de aceitação

`tests/aceitacao/desconto.feature` descreve a regra na linguagem do negócio. Para o pytest-bdd
executá-lo, crie `tests/aceitacao/test_desconto_aceitacao.py` ligando cada passo ao código:

<!-- arquivo: tests/aceitacao/test_desconto_aceitacao.py -->
```python
from datetime import date
from decimal import Decimal

from pytest_bdd import given, parsers, scenarios, then, when

from app.regras import calcular_valor_pagamento

scenarios("desconto.feature")


@given(parsers.parse("um título de {valor} com vencimento em {vencimento}"), target_fixture="titulo")
def titulo(valor, vencimento):
    return {"valor": Decimal(valor), "vencimento": date.fromisoformat(vencimento)}


@when(parsers.parse("o pagamento é feito em {pagamento}"), target_fixture="valor_a_pagar")
def pagar(titulo, pagamento):
    return calcular_valor_pagamento(
        titulo["valor"], titulo["vencimento"], date.fromisoformat(pagamento)
    )


@then(parsers.parse("o valor a pagar é {esperado}"))
def conferir_valor(valor_a_pagar, esperado):
    assert valor_a_pagar == Decimal(esperado)
```

<!-- espera: qualquer -->
<!-- contem: test_desconto_aceitacao.py -->
```bash
docker compose run --rm testes pytest -m aceitacao -v
```

São quatro exemplos. Só ficam todos verdes quando a regra 9 estiver completa: com a implementação
mínima do passo 4, passam dois e falham dois.

## 8. Demonstração: teste de carga

20 usuários simultâneos, 5 novos por segundo, durante 30 segundos, contra a API que está no ar:

<!-- contem: Aggregated -->
```bash
docker compose run --rm testes locust --headless -u 20 -r 5 -t 30s --host http://app:8000
```

Observe na tabela final: tempo médio, percentil 95 e a coluna de falhas (deve ficar em zero).
O teste cadastra títulos chamados "Carga" no banco de desenvolvimento.

## 9. Guardar o trabalho e encerrar

```bash
git add -A
git commit --allow-empty -m "Aula 6: regra 9 com TDD"
docker compose stop
```

<!-- manual -->
```bash
git push meu meu-trabalho
```

Para apagar tudo da máquina no fim da disciplina (contêineres, dados e imagens deste projeto):

<!-- manual -->
```bash
docker compose down -v --rmi local
```
