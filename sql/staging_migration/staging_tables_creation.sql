CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS staging;
COMMENT ON SCHEMA staging IS
'Cleaned and normalized data';

-- CREATE TABLE BATIMENTS (Buildings)
CREATE TABLE IF NOT EXISTS staging.batiments 
(
    id_batiment UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- identifiant unique du bâtiment
    code_insee VARCHAR(5) NOT NULL,
    nom_batiment VARCHAR(255),
    type_batiment VARCHAR(3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 2154) NOT NULL,

    CONSTRAINT chk_batiments_code_insee_length
    CHECK (length(code_insee) = 5)
);

CREATE INDEX IF NOT EXISTS idx_batiments_geom
    ON staging.batiments
        USING GIST (geom);


-- CREATE TABLE COMMUNES (Municipalities)
CREATE TABLE IF NOT EXISTS staging.communes
(
    code_insee VARCHAR(5) PRIMARY KEY,
    nom_commune VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 2154) NOT NULL,

    CONSTRAINT chk_communes_code_insee_length
    CHECK (length(code_insee) = 5)
);

CREATE INDEX IF NOT EXISTS idx_communes_geom
    ON staging.communes
        USING GIST (geom);


-- CREATE TABLE PARCELLES (Cadastral Parcels)
CREATE TABLE IF NOT EXISTS staging.parcelles
(
    id_parcelle varchar(15) PRIMARY KEY,
    code_insee VARCHAR(5) NOT NULL,
    prefixe_parcelle VARCHAR(3) NOT NULL,
    code_section VARCHAR(3) NOT NULL,
    numero_parcelle VARCHAR(3) NOT NULL,
    contenance bigint,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 2154) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_parcelles_geom
    ON staging.parcelles
        USING GIST (geom);


-- CREATE TABLE ADDRESSES
CREATE TABLE IF NOT EXISTS staging.address
(
    uuid UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    id_address int NOT NULL,
    numero int,
    nom_voie VARCHAR(255),
    code_postal VARCHAR(5) NOT NULL,
    code_insee VARCHAR(5) NOT NULL,
    nom_commune VARCHAR(255) NOT NULL,
    type_position VARCHAR(30),
    source_position VARCHAR(30),
    source_nom_voie VARCHAR(30),
    cad_parcelle VARCHAR(15),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(POINT, 2154) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_address_geom
    ON staging.address
        USING GIST (geom);

-- CREATE ASSOCIATION TABLE ADRESSES-PARCELLES
CREATE TABLE IF  NOT EXISTS staging.address_parcelle
(
    id_address int NOT NULL,
    id_parcelle VARCHAR(15) NOT NULL,
    source VARCHAR(30) NOT NULL,
    PRIMARY KEY (id_address, id_parcelle)
    
);