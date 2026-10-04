# Playbook da aula 3: fixtures, dublês de teste e cobertura

Copie e cole cada bloco, na ordem. Exercícios completos: [`docs/aulas/aula3.md`](../aulas/aula3.md).

## 1. Chegar à versão desta aula

Escolha **um** dos caminhos.

### Caminho A: mesma máquina, a pasta da aula passada ainda existe

<!-- caminho: A -->
```bash
git add -A
git commit --allow-empty -m "Meu trabalho antes da aula 3"
git fetch turma
git merge -X theirs turma/aula-3 -m "Atualiza para a aula 3"
```

Nesta versão o `app/regras.py` volta à versão oficial, com os cinco defeitos corrigidos.
Por causa do `-X theirs`, onde a sua correção e a oficial diferem, fica a oficial.

### Caminho B: máquina zerada

<!-- caminho: B -->
```bash
git clone -o turma -b aula-3 https://github.com/pedromullerupf/teste-software-upf.git
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
git merge -X theirs turma/aula-3 -m "Atualiza para a aula 3"
```

## 2. Subir o ambiente e conferir que a suíte está verde

```bash
docker compose up -d
```

<!-- contem: passed -->
```bash
docker compose run --rm testes pytest
```

Resultado esperado: tudo verde. Se algum teste seu falhar agora, o defeito está no teste: o código das regras está correto.

## 3. Fixtures do serviço de baixa

O alvo de hoje é `app/servicos.py`, classe `ServicoBaixa(repositorio, relogio, notificador)`.
Nenhum teste de hoje usa o banco.

Crie `tests/unit/test_servico_baixa.py`:

<!-- arquivo: tests/unit/test_servico_baixa.py -->
```python
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.regras import RegraVioladaError
from app.servicos import ServicoBaixa, TituloNaoEncontradoError

VENCIMENTO = date(2026, 11, 10)   # terça-feira


@pytest.fixture
def titulo():
    return {
        "id": 7, "tipo": "pagar", "descricao": "Aluguel", "pessoa": "Imobiliária",
        "valor": Decimal("1000.00"), "vencimento": VENCIMENTO,
        "status": "aberto", "saldo": Decimal("1000.00"),
    }


@pytest.fixture
def repositorio(titulo):
    repositorio = Mock()
    repositorio.buscar_titulo.return_value = titulo
    return repositorio


@pytest.fixture
def relogio():
    relogio = Mock()
    relogio.hoje.return_value = VENCIMENTO
    return relogio


@pytest.fixture
def notificador():
    return Mock()


@pytest.fixture
def servico(repositorio, relogio, notificador):
    return ServicoBaixa(repositorio, relogio, notificador)
```

## 4. Testes com dublês

Acrescente ao fim de `tests/unit/test_servico_baixa.py`:

<!-- acrescentar: tests/unit/test_servico_baixa.py -->
```python
def test_baixa_total_em_dia_quita_o_titulo(servico):
    resultado = servico.baixar(7, Decimal("1000.00"))

    assert resultado.status == "quitado"
    assert resultado.saldo_restante == Decimal("0.00")


def test_baixa_total_avisa_que_o_titulo_foi_quitado(servico, notificador):
    servico.baixar(7, Decimal("1000.00"))

    notificador.titulo_quitado.assert_called_once_with(7, "Aluguel")


def test_titulo_inexistente_levanta_erro_e_nao_grava_nada(servico, repositorio):
    repositorio.buscar_titulo.return_value = None

    with pytest.raises(TituloNaoEncontradoError):
        servico.baixar(99, Decimal("10.00"))

    repositorio.registrar_baixa.assert_not_called()


def test_baixa_em_atraso_usa_a_data_do_relogio(servico, relogio):
    relogio.hoje.return_value = date(2026, 11, 11)   # um dia depois do vencimento

    resultado = servico.baixar(7, Decimal("1000.00"))

    assert resultado.encargos == Decimal("20.33")
```

<!-- contem: 4 passed -->
```bash
docker compose run --rm testes pytest -v tests/unit/test_servico_baixa.py
```

Resultado esperado: `4 passed`.

Faltam, do roteiro: baixa parcial (notificador **não** chamado), conferência do que foi gravado com
`assert_called_once_with`, e baixa maior que o saldo (`RegraVioladaError`, nada gravado).

## 5. Cobertura

<!-- contem: app/servicos.py -->
<!-- contem: TOTAL -->
```bash
docker compose run --rm testes pytest tests/unit --cov=app.servicos --cov=app.regras --cov-branch --cov-report=term-missing
```

A coluna `Missing` mostra as linhas e os desvios que nenhum teste exercitou. Escreva os testes que faltam.

## 6. Para pensar: cobertura não é qualidade

Acrescente ao fim de `tests/unit/test_servico_baixa.py` um teste sem nenhum `assert`:

<!-- acrescentar: tests/unit/test_servico_baixa.py -->
```python
def test_que_nao_verifica_nada(servico):
    servico.baixar(7, Decimal("400.00"))
```

<!-- contem: 5 passed -->
```bash
docker compose run --rm testes pytest tests/unit/test_servico_baixa.py --cov=app.servicos --cov-branch --cov-report=term-missing
```

A cobertura subiu e o teste não detecta defeito nenhum. Depois de observar, apague esse teste.

## 7. Guardar o trabalho e encerrar

```bash
git add -A
git commit -m "Aula 3: fixtures, dublês e cobertura"
docker compose stop
```

<!-- manual -->
```bash
git push meu meu-trabalho
```
