# Relationships

YamlQL automatically detects and maintains relationships between tables based on the YAML structure. Understanding these relationships is crucial for writing effective queries.

## Types of Relationships

### 1. Parent-Child

The most common relationship, representing nested structures:

```yaml
# Input YAML
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

Creates:
```sql
-- Parent table
CREATE TABLE services (
    _id VARCHAR PRIMARY KEY
);

-- Child table
CREATE TABLE services_redis (
    _id VARCHAR PRIMARY KEY,
    parent_id VARCHAR REFERENCES services(_id),
    image VARCHAR,
    ports VARCHAR[]
);
```

### 2. List Items

When a parent contains a list of objects:

```yaml
# Input YAML
spec:
  containers:
    - name: nginx
      image: nginx
    - name: redis
      image: redis
```

Creates:
```sql
-- Parent table
CREATE TABLE spec (
    _id VARCHAR PRIMARY KEY
);

-- List items table
CREATE TABLE spec_containers (
    _id VARCHAR PRIMARY KEY,
    parent_id VARCHAR REFERENCES spec(_id),
    name VARCHAR,
    image VARCHAR
);
```

### 3. References

When objects reference each other:

```yaml
# Input YAML
deployment:
  name: web
  configMap: logging-config
configMaps:
  - name: logging-config
    data:
      log_level: debug
```

Creates:
```sql
CREATE TABLE deployment (
    name VARCHAR,
    configMap VARCHAR  -- References configMaps.name
);

CREATE TABLE configMaps (
    name VARCHAR PRIMARY KEY,
    data_log_level VARCHAR
);
```

## Relationship Tracking

### 1. Metadata Table

Relationships are tracked in `__relationships`:

```sql
SELECT * FROM __relationships;
```
```
┌──────────────┬───────────────┬──────────────────┐
│ source_table │ target_table  │ relationship_type│
├──────────────┼───────────────┼──────────────────┤
│ services     │ services_redis│ parent-child     │
│ deployment   │ configMaps    │ reference        │
└──────────────┴───────────────┴──────────────────┘
```

### 2. Table Information

Table hierarchy in `__tables`:

```sql
SELECT * FROM __tables WHERE parent_table IS NOT NULL;
```
```
┌─────────────────┬──────────────┬─────────┐
│ table_name      │ parent_table │ type    │
├─────────────────┼──────────────┼─────────┤
│ services_redis  │ services     │ child   │
│ spec_containers │ spec         │ child   │
└─────────────────┴──────────────┴─────────┘
```

## Using Relationships

### 1. Simple Joins

Join parent and child tables:

```sql
-- Get service details
SELECT 
    s.name,
    c.image,
    c.ports
FROM services s
JOIN services_containers c ON c.parent_id = s._id;
```

### 2. Nested Data

Navigate through multiple levels:

```sql
-- Get container resources
SELECT 
    d.name as deployment,
    c.name as container,
    r.cpu,
    r.memory
FROM deployments d
JOIN spec s ON s.parent_id = d._id
JOIN spec_containers c ON c.parent_id = s._id
JOIN container_resources r ON r.container_id = c._id;
```

### 3. Reference Lookups

Follow reference relationships:

```sql
-- Get ConfigMap data for deployments
SELECT 
    d.name as deployment,
    cm.data_log_level
FROM deployment d
JOIN configMaps cm ON cm.name = d.configMap;
```

## Best Practices

### 1. Check Relationships First

Before writing complex queries:

```sql
-- Find all related tables
SELECT * FROM __relationships 
WHERE source_table = 'your_table'
   OR target_table = 'your_table';
```

### 2. Use Proper Join Types

Choose the right join based on data:

```sql
-- INNER JOIN for required relationships
SELECT ... FROM parent p
INNER JOIN child c ON c.parent_id = p._id;

-- LEFT JOIN for optional relationships
SELECT ... FROM parent p
LEFT JOIN child c ON c.parent_id = p._id;
```

### 3. Handle Multiple Levels

Use CTEs for complex hierarchies:

```sql
WITH RECURSIVE tree AS (
    -- Base case
    SELECT 
        table_name,
        parent_table,
        1 as level
    FROM __tables
    WHERE parent_table = 'root'

    UNION ALL

    -- Recursive case
    SELECT 
        t.table_name,
        t.parent_table,
        tr.level + 1
    FROM __tables t
    JOIN tree tr ON t.parent_table = tr.table_name
)
SELECT * FROM tree;
```

### 4. Validate References

Check reference integrity:

```sql
-- Find broken references
SELECT d.name, d.configMap
FROM deployment d
LEFT JOIN configMaps cm ON cm.name = d.configMap
WHERE cm.name IS NULL;
```

## Common Patterns

### 1. Parent-Child Queries

```sql
-- Get all children with parent info
SELECT 
    p.name as parent_name,
    c.* 
FROM parent p
JOIN child c ON c.parent_id = p._id;

-- Count children per parent
SELECT 
    p.name,
    COUNT(c._id) as child_count
FROM parent p
LEFT JOIN child c ON c.parent_id = p._id
GROUP BY p.name;
```

### 2. Hierarchical Queries

```sql
-- Get full path to each node
WITH RECURSIVE path AS (
    SELECT 
        table_name,
        ARRAY[table_name] as path
    FROM __tables
    WHERE parent_table IS NULL

    UNION ALL

    SELECT 
        t.table_name,
        p.path || t.table_name
    FROM __tables t
    JOIN path p ON t.parent_table = p.table_name
)
SELECT * FROM path;
```

### 3. Reference Chains

```sql
-- Follow reference chain
SELECT 
    s.name as service,
    c.name as config,
    v.name as volume
FROM services s
JOIN configs c ON c.name = s.config_name
JOIN volumes v ON v.name = s.volume_name;
```

## Troubleshooting

### 1. Missing Relationships

If relationships aren't showing:
- Check table names match exactly
- Verify parent-child structure
- Look for typos in references

### 2. Join Issues

If joins return unexpected results:
- Check join conditions
- Verify relationship types
- Look for NULL values

### 3. Performance

For better query performance:
- Use appropriate join types
- Add WHERE clauses before joins
- Consider indexing reference columns

## Related Topics

- [Schema Transformation](schema-transformation.md)
- [Metadata Tables](metadata-tables.md)
- [SQL Query Command](../commands/sql.md)
- [Complex YAML Guide](../guides/complex-yaml.md) 