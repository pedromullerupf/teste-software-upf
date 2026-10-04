# Aula 3: Fixtures, dublês de teste e cobertura

> Passo a passo para copiar e colar: [`docs/playbooks/aula-3.md`](../playbooks/aula-3.md).

Novidades desta versão:

- `app/regras.py` volta à versão oficial, com os cinco defeitos corrigidos.
- `app/servicos.py` traz a classe `ServicoBaixa`, que depende de um repositório,
  de um relógio e de um notificador.

Os testes de hoje vão em `tests/unit/test_servico_baixa.py`. Nenhum deles pode usar o banco.

## Exercício 1: fixtures

Crie fixtures para:

- um título aberto de 1.000,00 com vencimento em 10/11/2026, no formato que
  `repositorio.buscar_titulo` devolve (um dicionário com `id`, `tipo`, `descricao`,
  `pessoa`, `valor`, `vencimento`, `status` e `saldo`);
- um repositório falso (`Mock`) cujo `buscar_titulo` devolve esse título;
- um relógio falso com data fixa;
- o `ServicoBaixa` montado com os três dublês.

## Exercício 2: dublês

Escreva testes para os comportamentos abaixo.

1. Baixa total em dia: status `quitado`, sem encargos, notificador chamado uma vez
   com o número e a descrição do título.
2. Baixa parcial: status `parcial`, notificador **não** chamado.
3. Baixa em atraso: os encargos usam a data do relógio falso.
4. A baixa gravada no repositório tem o valor, os encargos e a data corretos
   (`assert_called_once_with`).
5. Título inexistente levanta `TituloNaoEncontradoError` e nada é gravado.
6. Baixa maior que o saldo levanta `RegraVioladaError` e nada é gravado.

## Exercício 3: cobertura

```
docker compose run --rm testes pytest tests/unit --cov=app.servicos --cov=app.regras --cov-branch --cov-report=term-missing
```

Encontre as linhas e os desvios não cobertos e escreva os testes que faltam.

## Para pensar

Escreva um teste que executa `baixar` e não tem nenhum `assert`. A cobertura muda?
O que isso diz sobre usar cobertura como medida de qualidade?
