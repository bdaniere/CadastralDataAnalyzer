SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'KO'
    END AS status,
    COUNT(*) AS metric_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'Aucune géométrie vide trouvée.'
        ELSE 'ERREUR : Des géométries vides ont été trouvées.'
    END AS message
FROM {schema_name}.{table_name}
WHERE 
    ST_IsEmpty({geometry_field})
    AND ST_Area({geometry_field}) = 0;