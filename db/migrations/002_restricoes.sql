-- Regra 1 também no banco. NOT VALID: vale para linhas novas e não reprova
-- os títulos inválidos que já existam no banco de desenvolvimento.
ALTER TABLE titulos ADD CONSTRAINT titulos_valor_positivo CHECK (valor > 0) NOT VALID;
