CREATE OR REPLACE FUNCTION fn_encargos(p_valor numeric, p_vencimento date, p_pagamento date)
RETURNS numeric
LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE
               WHEN p_pagamento < fn_proximo_dia_util(p_vencimento) THEN 0.00
               ELSE round(
                        p_valor * 0.02
                        + p_valor * 0.00033 * (p_pagamento - fn_proximo_dia_util(p_vencimento)),
                        2)
           END;
$$;
