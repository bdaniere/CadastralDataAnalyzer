SELECT count(*)
FROM {schema_name}.{table_name}
WHERE 
    ST_IsEmpty({geometry_field})
    AND ST_Area({geometry_field}) = 0
;