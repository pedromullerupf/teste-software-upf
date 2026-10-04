# Teste de Software (UPF): aulas práticas

Aplicação de estudo: um pequeno sistema de **contas a pagar e a receber** (Python, Flask e PostgreSQL,
tudo em Docker). Ela é pequena de propósito: o objetivo é testar, não programar.

## Mapa das aulas

Cada aula tem uma **branch** com o projeto como ele deve estar no início da aula, um **playbook**
(passo a passo para copiar e colar) e um **roteiro** (os exercícios).

| Aula | Data | Tema | Branch | Playbook | Roteiro |
|---|---|---|---|---|---|
| 1 | 06/10 | Caça ao bug e primeiro teste | [`aula-1`](../../tree/aula-1) | [aula-1.md](docs/playbooks/aula-1.md) | [aula1.md](../../blob/aula-1/docs/aulas/aula1.md) |
| 2 | 20/10 | Testes unitários das regras | [`aula-2`](../../tree/aula-2) | [aula-2.md](docs/playbooks/aula-2.md) | [aula2.md](../../blob/aula-2/docs/aulas/aula2.md) |
| 3 | 27/10 | Fixtures, dublês de teste e cobertura | [`aula-3`](../../tree/aula-3) | [aula-3.md](docs/playbooks/aula-3.md) | [aula3.md](../../blob/aula-3/docs/aulas/aula3.md) |
| 4 | 03/11 | Integração e testes no banco de dados | [`aula-4`](../../tree/aula-4) | [aula-4.md](docs/playbooks/aula-4.md) | [aula4.md](../../blob/aula-4/docs/aulas/aula4.md) |
| 5 | 10/11 | Testes de ponta a ponta e automação | [`aula-5`](../../tree/aula-5) | [aula-5.md](docs/playbooks/aula-5.md) | [aula5.md](../../blob/aula-5/docs/aulas/aula5.md) |
| 6 | 17/11 | Caixa-preta, TDD, caixa-branca, aceitação e carga | [`aula-6`](../../tree/aula-6) | [aula-6.md](docs/playbooks/aula-6.md) | [aula6.md](../../blob/aula-6/docs/aulas/aula6.md) |

O que cada branch acrescenta à anterior:

| Branch | Novidade |
|---|---|
| `aula-1` | Projeto inicial: cadastro, parcelamento e baixa de títulos, com cinco defeitos plantados |
| `aula-2` | `defeitos/regras/` e `validar_testes.py`, que dá o placar de defeitos que os seus testes detectam |
| `aula-3` | `app/regras.py` corrigido e `app/servicos.py` (serviço de baixa com dependências injetadas) |
| `aula-4` | Funções e triggers no PostgreSQL, API REST, fixtures de banco e `defeitos/banco/` |
| `aula-5` | Login, tela de fluxo de caixa, estrutura de testes E2E e pipeline do GitHub Actions |
| `aula-6` | Enunciado da regra de desconto (você implementa com TDD), cenário de aceitação e teste de carga |

Esta branch `main` tem o projeto inicial (igual à `aula-1`) e os playbooks de todas as aulas.

## Como funciona

Requisitos: **Git** e **Docker** (com Docker Compose). Não é preciso instalar Python nem PostgreSQL.

**Na primeira aula**, baixe o projeto e crie a sua branch de trabalho:

```
git clone -o turma -b aula-1 https://github.com/pedromullerupf/teste-software-upf.git
cd teste-software-upf
git switch -c meu-trabalho
docker compose up -d
```

- Aplicação: http://localhost:8000
- Testes: `docker compose run --rm testes pytest -v`

**A cada aula seguinte**, traga a versão nova por cima do seu trabalho (troque `N` pelo número da aula):

```
git add -A
git commit --allow-empty -m "Meu trabalho antes da aula N"
git fetch turma
git merge -X theirs turma/aula-N -m "Atualiza para a aula N"
```

Os seus arquivos de teste ficam como estão. Onde você e a versão oficial alteraram o mesmo trecho
(acontece em `app/regras.py`), vale a oficial.

**Em uma máquina zerada**, clone direto a branch da aula:

```
git clone -o turma -b aula-N https://github.com/pedromullerupf/teste-software-upf.git
```

O playbook de cada aula traz esses comandos já com o número certo.

## Comandos do dia a dia

```
docker compose up -d                                   sobe banco e aplicação
docker compose ps                                      mostra o que está no ar
docker compose run --rm testes pytest -v               roda os testes
docker compose run --rm testes pytest -m unit          só uma camada (unit, banco, integracao, aceitacao)
docker compose run --rm testes pytest -k encargos      só testes com "encargos" no nome
docker compose logs -f app                             log da aplicação
docker compose exec db psql -U contas contas           terminal SQL
docker compose stop                                    para tudo, mantendo os dados
docker compose down -v                                 apaga tudo e recomeça do zero
```

## Onde fica cada coisa

| Caminho | Conteúdo |
|---|---|
| `app/regras.py` | Regras de negócio, em funções puras |
| `app/repositorio.py` | Todo o SQL da aplicação |
| `app/web.py` | Rotas e telas |
| `db/migrations/` | Scripts SQL do banco, aplicados em ordem |
| `tests/` | Testes, separados por camada |
| `docs/regras_de_negocio.md` | O que o sistema deve fazer (a especificação) |
| `docs/aulas/` | Roteiro de cada aula, com os exercícios |
| `docs/playbooks/` | Passo a passo de cada aula, para copiar e colar |
