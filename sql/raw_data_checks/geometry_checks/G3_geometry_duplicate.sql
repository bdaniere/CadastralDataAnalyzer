SELECT
    md5(ST_AsBinary({geometry_field})) AS geom_hash
FROM {schema_name}.{table_name}
GROUP BY geom_hash
HAVING COUNT(*) > 1;