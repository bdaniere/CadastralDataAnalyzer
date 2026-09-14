SELECT count(*)
FROM {schema_name}.{table_name}
WHERE NOT ST_IsValid({geometry_field});
