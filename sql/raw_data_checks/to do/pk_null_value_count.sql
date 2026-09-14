SELECT count(*) 
FROM {schema_name}.{table_name}
WHERE {pk_field} IS NULL;