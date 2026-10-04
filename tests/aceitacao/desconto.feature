# language: pt
Funcionalidade: Valor a pagar conforme a data do pagamento
  Como responsável pelo financeiro
  Quero saber quanto pagar em cada data
  Para aproveitar descontos e evitar encargos

  Esquema do Cenário: Pagamento de um título de 1000,00 que vence em 10/11/2026
    Dado um título de 1000.00 com vencimento em 2026-11-10
    Quando o pagamento é feito em <pagamento>
    Então o valor a pagar é <valor a pagar>

    Exemplos:
      | pagamento  | valor a pagar |
      | 2026-10-31 | 950.00        |
      | 2026-11-01 | 1000.00       |
      | 2026-11-10 | 1000.00       |
      | 2026-11-11 | 1020.33       |
