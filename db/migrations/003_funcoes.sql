-- Regras de negócio implementadas dentro do PostgreSQL.
-- Este arquivo pode ser executado várias vezes (CREATE OR REPLACE / DROP IF EXISTS).

-- Saldo do título: valor menos a soma das baixas. NULL se o título não existe.
CREATE OR REPLACE FUNCTION fn_saldo_titulo(p_titulo_id integer) RETURNS numeric
LANGUAGE sql STABLE AS $$
    SELECT t.valor - COALESCE((SELECT SUM(b.valor) FROM baixas b WHERE b.titulo_id = t.id), 0)
      FROM titulos t
     WHERE t.id = p_titulo_id;
$$;

-- Regra 5: sábado e domingo são prorrogados para segunda-feira.
CREATE OR REPLACE FUNCTION fn_proximo_dia_util(p_data date) RETURNS date
LANGUAGE sql IMMUTABLE AS $$
    SELECT p_data + CASE EXTRACT(ISODOW FROM p_data)::int
                        WHEN 6 THEN 2
                        WHEN 7 THEN 1
                        ELSE 0
                    END;
$$;

-- Regra 4: multa de 2% mais juros de 0,033% ao dia, só para pagamento em atraso.
CREATE OR REPLACE FUNCTION fn_encargos(p_valor numeric, p_vencimento date, p_pagamento date)
RETURNS numeric
LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE
               WHEN p_pagamento <= fn_proximo_dia_util(p_vencimento) THEN 0.00
               ELSE round(
                        p_valor * 0.02
                        + p_valor * 0.00033 * (p_pagamento - fn_proximo_dia_util(p_vencimento)),
                        2)
           END;
$$;

-- Regra 3: impede baixa inválida, qualquer que seja o programa que tente gravá-la.
CREATE OR REPLACE FUNCTION fn_valida_baixa() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    v_status text;
BEGIN
    SELECT status INTO v_status FROM titulos WHERE id = NEW.titulo_id FOR UPDATE;

    IF v_status IN ('cancelado', 'quitado') THEN
        RAISE EXCEPTION 'Título % não pode receber baixa', v_status;
    END IF;
    IF NEW.valor <= 0 THEN
        RAISE EXCEPTION 'O valor da baixa deve ser maior que zero';
    END IF;
    IF NEW.valor > fn_saldo_titulo(NEW.titulo_id) THEN
        RAISE EXCEPTION 'O valor da baixa não pode ser maior que o saldo do título';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_valida_baixa ON baixas;
CREATE TRIGGER trg_valida_baixa
    BEFORE INSERT ON baixas
    FOR EACH ROW EXECUTE FUNCTION fn_valida_baixa();

-- Regra 2: depois de cada baixa, o status do título acompanha o saldo.
CREATE OR REPLACE FUNCTION fn_atualiza_status() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE titulos
       SET status = CASE WHEN fn_saldo_titulo(NEW.titulo_id) = 0 THEN 'quitado' ELSE 'parcial' END
     WHERE id = NEW.titulo_id;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_atualiza_status ON baixas;
CREATE TRIGGER trg_atualiza_status
    AFTER INSERT ON baixas
    FOR EACH ROW EXECUTE FUNCTION fn_atualiza_status();

-- Regra 7: saldo projetado do período = a receber menos a pagar,
-- considerando os saldos dos títulos abertos ou parciais que vencem no período.
CREATE OR REPLACE FUNCTION fn_fluxo_caixa(p_inicio date, p_fim date) RETURNS numeric
LANGUAGE sql STABLE AS $$
    SELECT COALESCE(SUM(CASE t.tipo WHEN 'receber' THEN 1 ELSE -1 END * fn_saldo_titulo(t.id)), 0.00)
      FROM titulos t
     WHERE t.vencimento BETWEEN p_inicio AND p_fim
       AND t.status IN ('aberto', 'parcial');
$$;
