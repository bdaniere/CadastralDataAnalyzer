SELECT
    '{table_name}_COUNT_INVALID_GEOM' AS control_name,
    COUNT(*) = 0 AS success,
    COUNT(*) AS error_count
FROM {schema_name}.{table_name}
WHERE NOT ST_IsValid({geometry_field});