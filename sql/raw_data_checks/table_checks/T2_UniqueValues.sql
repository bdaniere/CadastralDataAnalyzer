SELECT
    '{table_name}_{table_field}_NOT_NULL' AS control_name,
    COUNT(*) = 0 AS success,
    COUNT(*) AS error_count
FROM {schema_name}.{table_name}
WHERE {table_field} IS NULL;
