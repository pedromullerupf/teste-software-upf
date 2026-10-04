"""Teste de carga da API (requisito não funcional: desempenho).

Com a aplicação no ar:

    docker compose run --rm testes locust --headless -u 20 -r 5 -t 30s --host http://app:8000

    -u  usuários simultâneos      -r  novos usuários por segundo      -t  duração

Observe na saída: tempo médio, percentil 95 e a coluna de falhas.
"""
from locust import HttpUser, between, task


class UsuarioDaApi(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(5)
    def listar_titulos(self):
        self.client.get("/api/titulos")

    @task(2)
    def consultar_fluxo_de_caixa(self):
        self.client.get("/api/fluxo-caixa?inicio=2026-11-01&fim=2026-11-30")

    @task(1)
    def cadastrar_titulo(self):
        self.client.post("/api/titulos", json={
            "tipo": "receber", "descricao": "Carga", "pessoa": "Locust",
            "valor": "100.00", "vencimento": "2026-11-10",
        })
