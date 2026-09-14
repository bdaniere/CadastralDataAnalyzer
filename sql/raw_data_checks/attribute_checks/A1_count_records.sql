SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'OK'
        ELSE 'KO'
    END AS status,
    COUNT(*) AS metric_value,
    CASE 
        WHEN COUNT(*) > 0 THEN 'Volume conforme : ' || COUNT(*) || ' lignes trouvées.'
        ELSE 'ERREUR : La table est complètement vide !'
    END AS message
FROM {schema_name}.{table_name};