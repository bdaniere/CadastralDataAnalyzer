SELECT
    '{table_name}_DUPLICATE_GEOM' AS control_name,
    COUNT(*) = 0 AS success,
    COUNT(*) AS error_count
FROM (
    SELECT
        md5(ST_AsBinary({geometry_field})) AS geom_hash
    FROM {schema_name}.{table_name}
    GROUP BY geom_hash
    HAVING COUNT(*) > 1
) AS duplicates;


