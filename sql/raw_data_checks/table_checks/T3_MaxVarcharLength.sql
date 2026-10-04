SELECT
    '{table_name}_{table_field}_MAX_LENGTH' AS control_name,
    COUNT(*) = 0 AS success,
    COUNT(*) AS error_count
FROM {schema_name}.{table_name}
WHERE LENGTH({table_field}) > {max_length};