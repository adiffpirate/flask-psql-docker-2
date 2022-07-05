CREATE TYPE user_tipo AS ENUM('Administrador', 'Escuderia', 'Piloto');

CREATE TABLE Users(
    Userid SERIAL PRIMARY KEY,
    Login VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(50) NOT NULL,
    Tipo user_tipo NOT NULL,
    IdOriginal int
);

-- Trigger para transformar a senha em md5 a cada nova inserção na tabela de usuários
CREATE OR REPLACE FUNCTION md5_password() RETURNS trigger AS $$
BEGIN
    new.password := md5(new.password);
    RETURN new;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_md5_password
    BEFORE INSERT ON Users
    FOR EACH ROW
    EXECUTE PROCEDURE md5_password();

-- Cria usuário admin
INSERT INTO Users (login, password, tipo)
    VALUES ('admin', 'admin', 'Administrador');

-- Cria usuários das escuderias
INSERT INTO Users (login, password, tipo, idoriginal)
    SELECT concat(constructorref, '_c'), constructorref, 'Escuderia', constructorid
    FROM Constructors
    ON CONFLICT DO NOTHING;

-- Cria usuários dos pilotos
INSERT INTO Users (login, password, tipo, idoriginal)
    SELECT concat(driverref, '_c'), driverref, 'Piloto', driverid
    FROM Driver
    ON CONFLICT DO NOTHING;

-- Trigger para criar usuário quando uma escuderia é adicionada
CREATE OR REPLACE FUNCTION create_constructor_user() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO
        Users(login, password, tipo, idoriginal)
        VALUES(concat(new.constructorref, '_c'), new.constructorref, 'Escuderia', new.constructorid);

           RETURN new;
END;
$$ language plpgsql;

CREATE TRIGGER trigger_create_constructor_user
     AFTER INSERT ON Constructors
     FOR EACH ROW
     EXECUTE PROCEDURE create_constructor_user();

-- Trigger para criar usuário quando um piloto é adicionado
CREATE OR REPLACE FUNCTION create_driver_user() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO
        Users(login, password, tipo, idoriginal)
        VALUES(concat(new.driverref, '_c'), new.driverref, 'Piloto', new.driverid);

           RETURN new;
END;
$$ language plpgsql;

CREATE TRIGGER trigger_create_driver_user
     AFTER INSERT ON Driver
     FOR EACH ROW
     EXECUTE PROCEDURE create_driver_user();
