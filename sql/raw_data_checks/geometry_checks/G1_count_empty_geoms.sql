SELECT
    '{table_name}_COUNT_EMPTY_GEOM' AS control_name,
    COUNT(*) = 0 AS success,
    COUNT(*) AS error_count
FROM {schema_name}.{table_name}
WHERE ST_IsEmpty({geometry_field})
    AND ST_Area({geometry_field}) = 0;