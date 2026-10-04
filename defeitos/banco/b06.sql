CREATE OR REPLACE FUNCTION fn_fluxo_caixa(p_inicio date, p_fim date) RETURNS numeric
LANGUAGE sql STABLE AS $$
    SELECT COALESCE(SUM(CASE t.tipo WHEN 'receber' THEN 1 ELSE -1 END * fn_saldo_titulo(t.id)), 0.00)
      FROM titulos t
     WHERE t.vencimento >= p_inicio AND t.vencimento < p_fim
       AND t.status IN ('aberto', 'parcial');
$$;
