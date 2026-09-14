SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'KO'
    END AS status,
    COUNT(*) AS metric_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'Aucune géométrie invalide trouvée.'
        ELSE 'ERREUR : Des géométries invalides ont été trouvées.'
    END AS message
FROM {schema_name}.{table_name}
WHERE NOT ST_IsValid({geometry_field});