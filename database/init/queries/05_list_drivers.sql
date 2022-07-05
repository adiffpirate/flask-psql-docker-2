---------------------------------------
-- Queries utilizadas no Relatório 3 --
---------------------------------------


-- Cria índice B-Tree pelo id da escuderia na tabela results
CREATE INDEX idx_constructorid ON Results (constructorid);
-- Cria índice parcial com somente os pilotos vencedores na tabela results
CREATE INDEX idx_winners ON Results (position) WHERE position = '1';

-- Função que retorna os pilotos de uma determinada escuderia
CREATE OR REPLACE FUNCTION list_drivers (input_id INT)
	RETURNS TABLE (
		name TEXT,
		wins BIGINT)
AS $$
BEGIN
	RETURN QUERY
	SELECT DISTINCT
		CONCAT(driver.forename, ' ', driver.surname) AS name,
		COUNT(1) FILTER (WHERE position = '1') OVER (PARTITION BY results.driverid)
	FROM results
	JOIN driver ON results.driverid = driver.driverid
	WHERE constructorid = input_id;
	END;
$$ LANGUAGE plpgsql;
