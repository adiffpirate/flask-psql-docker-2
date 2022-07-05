---------------------------------------
-- Queries utilizadas no Relatório 2 --
---------------------------------------


-- Cria índice HASH pelo nome da cidade na tabela geocities15k
CREATE INDEX idx_name ON GeoCities15k USING hash (name);
-- Cria índice HASH pelo país na tabela airports
CREATE INDEX idx_isocountry ON Airports USING hash (isocountry);

-- Cria extenções utilizadas na função de calcular a distância
CREATE EXTENSION IF NOT EXISTS Cube ;
CREATE EXTENSION IF NOT EXISTS EarthDistance ; -- EarthDistance precisa de Cube

-- Função que retorna todos os aeroportos num raio de 100km da cidade brasileira buscada
CREATE OR REPLACE FUNCTION airports_near_city (input_city TEXT, input_distance INT)
	RETURNS TABLE (
		city_name TEXT,
		airport_iatacode CHARACTER(3),
		airport_name TEXT,
		airport_city TEXT,
		distance NUMERIC,
		airport_type CHARACTER(15)
	)
AS $$
BEGIN
	RETURN QUERY
	WITH distances AS (
		SELECT 
			C.name AS city_name,
			A.iatacode AS airport_iatacode,
			A.name AS airport_name,
			A.city AS airport_city,
      ROUND(earth_distance(ll_to_earth(A.lat, A.long), ll_to_earth(C.lat , C.long))::NUMERIC) AS distance,
			A.type AS airport_type
		FROM (
			-- Aeroportos brasileiros dos tipos medium ou large
			SELECT
				name,
				latdeg AS lat,
				longdeg AS long,
				iatacode,
				city,
				type
			FROM airports
			WHERE isocountry = 'BR' AND (type = 'medium_airport' OR type = 'large_airport')
		) A,
		(
			-- Cidades com nome buscado
			SELECT
				name,
				lat,
				long
			FROM geocities15k
			WHERE name = input_city
		) C
	)
	SELECT * FROM distances
	WHERE distances.distance <= input_distance;
END;
$$ LANGUAGE plpgsql;
