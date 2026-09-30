SELECT
    '{table_name}_COUNT_RECORD' AS control_name,
    COUNT(*) > 0 AS success,
    COUNT(*) AS error_count
FROM {schema_name}.{table_name}