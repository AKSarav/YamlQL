# Complex YAML Guide

This guide shows how YamlQL handles complex YAML structures and provides strategies for querying them effectively.

## Complex Structures

### 1. Deep Nesting

```yaml
# deeply-nested.yml
application:
  config:
    database:
      primary:
        host: db1.example.com
        port: 5432
        credentials:
          username: admin
          password: secret
      replica:
        host: db2.example.com
        port: 5432
        credentials:
          username: readonly
          password: secret
```

Querying Approaches:

```sql
-- Using flattened columns
SELECT 
    database_primary_host,
    database_primary_port,
    database_primary_credentials_username
FROM config;

-- Using relationships
SELECT 
    p.host as primary_host,
    r.host as replica_host
FROM database_primary p
JOIN database_replica r ON true;
```

### 2. Mixed Arrays

```yaml
# mixed-content.yml
services:
  - name: web
    ports: 
      - 80
      - 443
    env:
      - name: NODE_ENV
        value: production
      - name: DEBUG
        value: "false"
  - name: api
    ports: [8080, 8081]
    env: 
      DEBUG: true
      NODE_ENV: development
```

Handling Different Formats:

```sql
-- Array of scalars (ports)
SELECT 
    s.name as service,
    p.value as port
FROM services s
JOIN ports p ON true;

-- Mixed environment formats
SELECT 
    s.name as service,
    COALESCE(e.name, e.key) as env_name,
    COALESCE(e.value, e.value) as env_value
FROM services s
LEFT JOIN env_array e ON e.service_id = s._id
LEFT JOIN env_object o ON o.service_id = s._id;
```

### 3. References and Anchors

```yaml
# anchors.yml
defaults: &defaults
  timeout: 30
  retry: 3

services:
  web: 
    <<: *defaults
    host: web.example.com
  api:
    <<: *defaults
    host: api.example.com
```

YamlQL resolves anchors automatically:

```sql
-- Query resolved values
SELECT 
    name,
    timeout,  -- From defaults
    retry,    -- From defaults
    host      -- Service specific
FROM services;
```

## Advanced Querying

### 1. Dynamic Paths

```yaml
# dynamic.yml
resources:
  ${environment}:
    cpu: 2
    memory: 4Gi
  ${region}:
    zone: us-east-1a
    subnet: subnet-123
```

Handling Variable Paths:

```sql
-- Find all environment sections
SELECT table_name 
FROM __tables 
WHERE table_name LIKE 'resources_%';

-- Query specific sections
SELECT *
FROM resources_production  -- For environment=production
WHERE cpu IS NOT NULL;
```

### 2. Conditional Sections

```yaml
# conditional.yml
deployment:
  name: app
  spec:
    {{if .Values.monitoring}}
    monitoring:
      enabled: true
      endpoint: /metrics
    {{end}}
    {{if .Values.ingress}}
    ingress:
      enabled: true
      host: app.example.com
    {{end}}
```

Handling Optional Sections:

```sql
-- Check which sections exist
SELECT table_name 
FROM __tables 
WHERE parent_table = 'spec';

-- Query with NULL handling
SELECT 
    name,
    monitoring_enabled,
    ingress_enabled
FROM deployment
LEFT JOIN spec_monitoring ON true
LEFT JOIN spec_ingress ON true;
```

### 3. Custom Types

```yaml
# custom-types.yml
durations:
  timeout: 5m
  interval: 2h30m
  delay: 45s

sizes:
  memory: 2Gi
  storage: 500Mi
  cache: 128Ki
```

Parsing Custom Types:

```sql
-- Parse durations to seconds
SELECT 
    key,
    CASE 
        WHEN value LIKE '%h%' 
        THEN CAST(REGEXP_EXTRACT(value, '(\d+)h') AS INTEGER) * 3600
        WHEN value LIKE '%m%' 
        THEN CAST(REGEXP_EXTRACT(value, '(\d+)m') AS INTEGER) * 60
        WHEN value LIKE '%s%' 
        THEN CAST(REGEXP_EXTRACT(value, '(\d+)s') AS INTEGER)
    END as seconds
FROM durations;

-- Convert sizes to bytes
SELECT 
    key,
    CASE 
        WHEN value LIKE '%Gi%' 
        THEN CAST(REGEXP_EXTRACT(value, '(\d+)Gi') AS INTEGER) * 1024 * 1024 * 1024
        WHEN value LIKE '%Mi%' 
        THEN CAST(REGEXP_EXTRACT(value, '(\d+)Mi') AS INTEGER) * 1024 * 1024
        WHEN value LIKE '%Ki%' 
        THEN CAST(REGEXP_EXTRACT(value, '(\d+)Ki') AS INTEGER) * 1024
    END as bytes
FROM sizes;
```

## Best Practices

### 1. Handle Deep Nesting

Use CTEs for complex paths:
```sql
WITH RECURSIVE path AS (
    -- Start at root
    SELECT 
        table_name,
        1 as depth,
        ARRAY[table_name] as path
    FROM __tables
    WHERE parent_table IS NULL

    UNION ALL

    -- Follow relationships
    SELECT 
        t.table_name,
        p.depth + 1,
        p.path || t.table_name
    FROM __tables t
    JOIN path p ON t.parent_table = ANY(p.path)
)
SELECT * FROM path ORDER BY depth, table_name;
```

### 2. Type Conversion

Create helper functions:
```sql
-- Memory conversion
CREATE FUNCTION parse_memory(value VARCHAR) RETURNS BIGINT AS $$
    SELECT 
        CASE 
            WHEN value LIKE '%Gi%' THEN REGEXP_EXTRACT(value, '(\d+)Gi')::BIGINT * 1024^3
            WHEN value LIKE '%Mi%' THEN REGEXP_EXTRACT(value, '(\d+)Mi')::BIGINT * 1024^2
            WHEN value LIKE '%Ki%' THEN REGEXP_EXTRACT(value, '(\d+)Ki')::BIGINT * 1024
            ELSE NULL
        END;
$$ LANGUAGE SQL;
```

### 3. Handle Missing Data

Use COALESCE and defaults:
```sql
SELECT 
    name,
    COALESCE(timeout, 30) as timeout,
    COALESCE(retry, 3) as retry_count,
    NULLIF(value, '') as clean_value
FROM services;
```

## Common Patterns

### 1. Recursive Structures

```yaml
# recursive.yml
menu:
  - name: Home
    link: /
  - name: Products
    link: /products
    submenu:
      - name: Hardware
        link: /products/hw
      - name: Software
        link: /products/sw
        submenu:
          - name: Desktop
            link: /products/sw/desktop
```

Query with recursion:
```sql
WITH RECURSIVE menu_items AS (
    -- Base items
    SELECT 
        name,
        link,
        1 as level,
        ARRAY[name] as path
    FROM menu
    WHERE parent_id IS NULL

    UNION ALL

    -- Submenu items
    SELECT 
        m.name,
        m.link,
        mi.level + 1,
        mi.path || m.name
    FROM submenu m
    JOIN menu_items mi ON m.parent_id = mi.id
)
SELECT 
    REPEAT('  ', level-1) || name as menu_structure,
    link,
    level,
    path
FROM menu_items
ORDER BY path;
```

### 2. Dynamic Fields

```yaml
# dynamic-fields.yml
metrics:
  cpu_${timestamp}: 85
  memory_${timestamp}: 512
  disk_${timestamp}: 1024
```

Query with pattern matching:
```sql
-- Group metrics by type
SELECT 
    REGEXP_EXTRACT(key, '^([^_]+)') as metric_type,
    AVG(CAST(value AS FLOAT)) as avg_value
FROM metrics
GROUP BY REGEXP_EXTRACT(key, '^([^_]+)');
```

### 3. Mixed Data Types

```yaml
# mixed-types.yml
values:
  - string: "text"
  - number: 123
  - boolean: true
  - null: null
  - object:
      key: value
  - array: [1, 2, 3]
```

Handle different types:
```sql
SELECT 
    key,
    CASE 
        WHEN value IS NULL THEN 'null'
        WHEN TYPEOF(value) = 'varchar' THEN 'string'
        WHEN TYPEOF(value) = 'boolean' THEN 'boolean'
        WHEN TYPEOF(value) = 'bigint' THEN 'number'
        WHEN value LIKE '[%]' THEN 'array'
        WHEN value LIKE '{%}' THEN 'object'
    END as value_type,
    value
FROM values;
```

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Metadata Tables](../concepts/metadata-tables.md)
- [Kubernetes Guide](kubernetes.md)
- [Docker Compose Guide](docker-compose.md) 