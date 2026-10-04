CREATE OR REPLACE FUNCTION fn_saldo_titulo(p_titulo_id integer) RETURNS numeric
LANGUAGE sql STABLE AS $$
    SELECT t.valor - COALESCE((SELECT MAX(b.valor) FROM baixas b WHERE b.titulo_id = t.id), 0)
      FROM titulos t
     WHERE t.id = p_titulo_id;
$$;
