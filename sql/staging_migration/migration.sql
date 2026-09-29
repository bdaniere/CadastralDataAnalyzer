-- INSERT INTO ADRESSES-PARCELLES TABLE
INSERT INTO staging.address_parcelle (id_address, id_parcelle, source)
SELECT
    a.id_address,
    p.id_parcelle,
    'BAN' AS source
FROM
    staging.address a
JOIN
    staging.parcelles p
ON
    a.cad_parcelle = p.id_parcelle;

-- INSERT INTO ADRESSES-PARCELLES TABLE USING SPATIAL JOIN
INSERT INTO staging.address_parcelle (id_address, id_parcelle, source)
SELECT 
    a.id_address, 
    p.id_parcelle, 
    'Spatial join' AS source
FROM 
    staging.address a
JOIN 
    staging.parcelles p
ON 
    a.cad_parcelle IS NULL
    AND ST_Contains(p.geom, a.geom);