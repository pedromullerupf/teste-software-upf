CREATE OR REPLACE FUNCTION fn_proximo_dia_util(p_data date) RETURNS date
LANGUAGE sql IMMUTABLE AS $$
    SELECT p_data + CASE EXTRACT(ISODOW FROM p_data)::int
                        WHEN 6 THEN 1
                        WHEN 7 THEN 1
                        ELSE 0
                    END;
$$;
