CREATE OR REPLACE FUNCTION fn_valida_baixa() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    v_status text;
BEGIN
    SELECT status INTO v_status FROM titulos WHERE id = NEW.titulo_id FOR UPDATE;

    IF v_status IN ('quitado') THEN
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
