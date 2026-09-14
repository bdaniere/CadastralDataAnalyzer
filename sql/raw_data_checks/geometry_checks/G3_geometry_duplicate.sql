SELECT
    CASE 
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'KO'
    END AS status,
    COUNT(*) AS metric_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'Aucune géométrie dupliquée trouvée.'
        ELSE 'ERREUR : Des géométries dupliquées ont été trouvées.'
    END AS message
FROM (
    SELECT
        md5(ST_AsBinary({geometry_field})) AS geom_hash
    FROM {schema_name}.{table_name}
    GROUP BY geom_hash
    HAVING COUNT(*) > 1
) AS duplicates;