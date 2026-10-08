-- Listé les erreurs et leur raisons en amont
SELECT id, ST_IsValidReason({geometry_field}) 
FROM {schema_name}.{table_name} 
WHERE NOT ST_IsValid({geometry_field});

UPDATE {schema_name}.{table_name} 
SET {geometry_field} = ST_Multi(ST_CollectionExtract(ST_MakeValid({geometry_field})), 3))
WHERE NOT ST_IsValid({geometry_field});