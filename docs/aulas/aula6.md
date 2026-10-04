# Aula 6: Caixa-preta, TDD, caixa-branca, aceitação e carga

> Passo a passo para copiar e colar: [`docs/playbooks/aula-6.md`](../playbooks/aula-6.md).

Novidades desta versão: nenhum código novo na aplicação. Hoje quem implementa é você.

## A nova regra

> **Regra 9: valor a pagar.** Pagamento feito com 10 dias ou mais de antecedência em
> relação ao vencimento tem 5% de desconto sobre o valor pago. De 9 dias antes até o
> vencimento, paga-se o valor cheio. Depois do vencimento, valem os encargos da regra 4.
>
> A antecedência é contada sobre a data original do vencimento. A prorrogação de fim de
> semana (regra 5) continua valendo para os encargos. O desconto é arredondado para duas
> casas, com meio centavo para cima.

Função a criar em `app/regras.py`:

```python
def calcular_valor_pagamento(valor: Decimal, vencimento: date, pagamento: date) -> Decimal:
    ...
```

## Exercício 1: caixa-preta (sem abrir o código)

Só com o enunciado acima, monte a tabela:

| Classe de equivalência | Valor representativo | Valores limite | Resultado esperado |
|---|---|---|---|
| | | | |

## Exercício 2: TDD

Implemente a regra em ciclos, em `tests/unit/test_desconto.py`:

1. **Vermelho**: escreva um teste da tabela e veja falhar.
2. **Verde**: escreva o mínimo de código para passar.
3. **Refatorar**: melhore o código com os testes verdes.

Um commit por ciclo. Nenhuma linha de produção sem um teste falhando antes.

## Exercício 3: caixa-branca

```
docker compose run --rm testes pytest tests/unit --cov=app.regras --cov-branch --cov-report=term-missing
```

Há algum desvio não exercitado no código que você acabou de escrever? Crie o caso que falta.

## Demonstração: teste de aceitação

`tests/aceitacao/desconto.feature` descreve a regra na linguagem do negócio
(Dado, Quando, Então). Com os passos ligados ao código, o pytest-bdd executa o arquivo:

```
docker compose run --rm testes pytest -m aceitacao -v
```

## Demonstração: teste de carga

```
docker compose run --rm testes locust --headless -u 20 -r 5 -t 30s --host http://app:8000
```
