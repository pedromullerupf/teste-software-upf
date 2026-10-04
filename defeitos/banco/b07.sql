CREATE OR REPLACE FUNCTION fn_atualiza_status() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE titulos
       SET status = CASE WHEN fn_saldo_titulo(NEW.titulo_id) < 0 THEN 'quitado' ELSE 'parcial' END
     WHERE id = NEW.titulo_id;
    RETURN NEW;
END;
$$;
