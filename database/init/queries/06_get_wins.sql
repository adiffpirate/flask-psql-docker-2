---------------------------------------
-- Queries utilizadas no Relatório 5 --
---------------------------------------


-- Cria índice B-Tree pelo id do piloto na tabela results
CREATE INDEX idx_driverid ON Results (driverid);

-- Função que retorna a quantidade de vitórias por ano e corrida de um piloto
CREATE OR REPLACE FUNCTION get_wins (input_driverid INT)
	RETURNS TABLE (
		year INT,
		name TEXT,
		wins BIGINT
	)
AS $$
BEGIN
	RETURN QUERY
	SELECT
		races.year,
		races.name,
		COUNT(1)
	FROM results
	JOIN races ON results.raceid = races.raceid
	WHERE driverid = input_driverid AND position = '1'
	GROUP BY ROLLUP (races.year, races.name)
	ORDER BY races.year, races.name NULLS FIRST;
	END;
$$ LANGUAGE plpgsql;
