SELECT count(*)
FROM {schema_name}.{table_name}
GROUP BY {pk_field}
HAVING count(*) > 1;