# Aula 5: Testes de ponta a ponta e automação

> Passo a passo para copiar e colar: [`docs/playbooks/aula-5.md`](../playbooks/aula-5.md).

Novidades desta versão:

- Tela de login (usuário `admin`, senha `admin123`) e tela de fluxo de caixa.
- `tests/e2e/conftest.py`: endereço da aplicação e limpeza do banco antes de cada teste.
- `.github/workflows/testes.yml`: pipeline que roda os testes a cada push.
- `Dockerfile.e2e` e serviço `e2e` no Compose, com navegador.

Depois de atualizar o projeto:

```
docker compose up -d
```

Atenção: os testes E2E usam a aplicação que está no ar e **apagam os títulos do banco
de desenvolvimento** antes de cada teste.

## Como rodar

Dentro do contêiner (sem janela de navegador):

```
docker compose run --rm e2e pytest -m e2e
docker compose run --rm e2e pytest -m e2e --tracing on
```

Na máquina, para ver o navegador (precisa de Python e do Playwright instalados):

```
pip install -r requirements.txt
playwright install chromium                          ou use um navegador já instalado:
python -m pytest -m e2e --headed --browser-channel msedge
```

## Exercício 1: gravar e criticar

```
playwright codegen http://localhost:8000
```

Grave o login e o cadastro de um título. Leia o código gerado: os seletores são
estáveis? O que quebraria se o layout mudasse?

## Exercício 2: fluxo completo (`tests/e2e/test_fluxo_baixa.py`)

Escreva à mão: login, cadastrar um título a receber de 1.000,00, baixar 400,00,
conferir saldo 600,00 e status `parcial` na lista, e conferir o saldo projetado
na tela de fluxo de caixa.

Use `get_by_label`, `get_by_role` e `expect`. Não use `time.sleep`.

## Exercício 3: cenário negativo e fixture

1. Baixa maior que o saldo mostra a mensagem de erro e o saldo não muda.
2. Extraia o login para uma fixture.

## Exercício 4: pipeline

1. Faça um push para o seu repositório no GitHub e abra a aba Actions.
2. Quebre um teste de propósito, faça outro push e veja o pipeline falhar.
3. Corrija e confirme que voltou a ficar verde.

## Depuração

```
python -m pytest -m e2e --tracing on
playwright show-trace test-results/<pasta do teste>/trace.zip
```
