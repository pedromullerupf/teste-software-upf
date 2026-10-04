# Playbook da aula 5: testes de ponta a ponta e automação

Copie e cole cada bloco, na ordem. Exercícios completos: [`docs/aulas/aula5.md`](../aulas/aula5.md).

## 1. Chegar à versão desta aula

Escolha **um** dos caminhos.

### Caminho A: mesma máquina, a pasta da aula passada ainda existe

<!-- caminho: A -->
```bash
git add -A
git commit --allow-empty -m "Meu trabalho antes da aula 5"
git fetch turma
git merge -X theirs turma/aula-5 -m "Atualiza para a aula 5"
```

### Caminho B: máquina zerada

<!-- caminho: B -->
```bash
git clone -o turma -b aula-5 https://github.com/pedromullerupf/teste-software-upf.git
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
git merge -X theirs turma/aula-5 -m "Atualiza para a aula 5"
```

## 2. Subir o ambiente

```bash
docker compose up -d
docker compose restart app
```

<!-- contem: passed -->
```bash
docker compose run --rm testes pytest
```

Abra a aplicação. Agora ela pede login: usuário `admin`, senha `admin123`. Há também a tela **Fluxo de caixa**.

<!-- manual -->
```text
http://localhost:8000
```

## 3. Primeiros testes de ponta a ponta

**Atenção:** os testes E2E usam a aplicação que está no ar e **apagam os títulos do banco de
desenvolvimento** antes de cada teste.

Crie `tests/e2e/test_login.py`:

<!-- arquivo: tests/e2e/test_login.py -->
```python
import re

import pytest
from playwright.sync_api import Page, expect


def test_sem_login_a_aplicacao_redireciona_para_a_tela_de_entrada(page: Page):
    page.goto("/")

    expect(page).to_have_url(re.compile(r"/login$"))


def test_senha_errada_mostra_mensagem_de_erro(page: Page):
    page.goto("/login")
    page.get_by_label("Usuário").fill("admin")
    page.get_by_label("Senha").fill("errada")
    page.get_by_role("button", name="Entrar").click()

    expect(page.get_by_role("alert")).to_have_text("Usuário ou senha inválidos.")


@pytest.fixture
def pagina(page: Page) -> Page:
    """Página já autenticada."""
    page.goto("/login")
    page.get_by_label("Usuário").fill("admin")
    page.get_by_label("Senha").fill("admin123")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("heading", name="Títulos")).to_be_visible()
    return page


def test_titulo_cadastrado_aparece_na_lista(pagina: Page):
    pagina.get_by_role("link", name="Novo título").click()
    pagina.get_by_label("Tipo").select_option(label="A receber")
    pagina.get_by_label("Descrição").fill("Mensalidade")
    pagina.get_by_label("Valor").fill("1000,00")
    pagina.get_by_label("Vencimento").fill("2026-11-10")
    pagina.get_by_role("button", name="Salvar").click()

    expect(pagina.get_by_role("status")).to_have_text("Título cadastrado.")
    linha = pagina.get_by_role("row").filter(has_text="Mensalidade")
    expect(linha.locator("[data-campo=saldo]")).to_have_text("1000.00")
    expect(linha.locator("[data-campo=status]")).to_have_text("aberto")
```

Rode dentro do contêiner, sem janela de navegador. Na primeira vez o Docker constrói a imagem com o
Chromium (alguns minutos e cerca de 1,5 GB).

<!-- contem: 3 passed -->
```bash
docker compose run --rm e2e pytest -m e2e
```

Resultado esperado: `3 passed`.

## 4. Exercício: o fluxo da baixa

Crie `tests/e2e/test_fluxo_baixa.py` com este ponto de partida e complete o que falta
(saldo 600,00 e status `parcial` na lista; saldo projetado na tela de fluxo de caixa):

<!-- arquivo: tests/e2e/test_fluxo_baixa.py -->
```python
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def pagina(page: Page) -> Page:
    """Página já autenticada."""
    page.goto("/login")
    page.get_by_label("Usuário").fill("admin")
    page.get_by_label("Senha").fill("admin123")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("heading", name="Títulos")).to_be_visible()
    return page


def test_baixa_parcial_e_registrada(pagina: Page):
    pagina.get_by_role("link", name="Novo título").click()
    pagina.get_by_label("Tipo").select_option(label="A receber")
    pagina.get_by_label("Descrição").fill("Mensalidade")
    pagina.get_by_label("Valor").fill("1000,00")
    pagina.get_by_label("Vencimento").fill("2026-11-10")
    pagina.get_by_role("button", name="Salvar").click()

    linha = pagina.get_by_role("row").filter(has_text="Mensalidade")
    linha.get_by_role("link", name="Baixar").click()

    pagina.get_by_label("Valor da baixa").fill("400,00")
    pagina.get_by_label("Data do pagamento").fill("2026-11-05")
    pagina.get_by_role("button", name="Registrar baixa").click()

    expect(pagina.get_by_role("status")).to_contain_text("Baixa registrada")
```

<!-- contem: 4 passed -->
```bash
docker compose run --rm e2e pytest -m e2e
```

Resultado esperado: `4 passed`.

## 5. Depurar quando um teste E2E falha

Grava o rastro dos testes que falharem (linha do tempo, tela antes e depois de cada ação):

<!-- contem: 4 passed -->
```bash
docker compose run --rm e2e pytest -m e2e --tracing retain-on-failure
```

Os rastros ficam em `test-results/`. Para abrir um deles e para gravar suas ações como código, é
preciso o Playwright instalado **na máquina** (fora do contêiner):

<!-- manual -->
```bash
pip install -r requirements.txt
playwright install chromium
playwright show-trace test-results/PASTA-DO-TESTE/trace.zip
playwright codegen http://localhost:8000
python -m pytest -m e2e --headed --slowmo 500
```

## 6. Pipeline no GitHub Actions

O arquivo `.github/workflows/testes.yml` roda os testes a cada `push`. Ele só roda no **seu**
repositório no GitHub. Se ainda não criou, crie um repositório vazio na sua conta e ligue-o:

<!-- manual -->
```bash
git remote add meu https://github.com/SEU-USUARIO/contas-upf.git
```

Envie o trabalho e abra a aba **Actions** do seu repositório:

```bash
git add -A
git commit -m "Aula 5: testes de ponta a ponta"
```

<!-- manual -->
```bash
git push -u meu meu-trabalho
```

O token ou login usado no `push` precisa da permissão `workflow`, porque o envio inclui um arquivo de pipeline.

Depois quebre um teste unitário de propósito, envie e veja o pipeline ficar vermelho; corrija, envie
e confirme o verde:

<!-- manual -->
```bash
git commit -am "Quebra um teste de propósito"
git push
git commit -am "Corrige o teste"
git push
```

## 7. Encerrar

```bash
docker compose stop
```
