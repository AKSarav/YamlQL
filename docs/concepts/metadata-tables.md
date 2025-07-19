# Metadata Tables

YamlQL creates special metadata tables to help you understand and navigate the schema. These tables start with `__` and provide information about table structure and relationships.

## Available Metadata Tables

### 1. `__tables`

Contains information about all available tables:

```sql
CREATE TABLE __tables (
    table_name VARCHAR,      -- Name of the table
    display_name VARCHAR,    -- User-friendly name
    parent_table VARCHAR,    -- Parent table (if any)
    type VARCHAR,           -- 'root', 'section', 'child'
    description VARCHAR     -- Human-readable description
);
```

Example data:
```sql
SELECT * FROM __tables;
```
```
┌─────────────────┬─────────────┬──────────────┬─────────┬────────────────────┐
│ table_name      │ display_name│ parent_table │ type    │ description        │
├─────────────────┼─────────────┼──────────────┼─────────┼────────────────────┤
│ root            │ root        │ NULL         │ root    │ Root level values  │
│ services        │ services    │ NULL         │ section │ Service definitions│
│ services_redis  │ redis       │ services     │ child   │ Redis service      │
└─────────────────┴─────────────┴──────────────┴─────────┴────────────────────┘
```

### 2. `__relationships`

Shows how tables are related to each other:

```sql
CREATE TABLE __relationships (
    source_table VARCHAR,     -- Parent table
    target_table VARCHAR,     -- Child table
    relationship_type VARCHAR -- Type of relationship
);
```

Example data:
```sql
SELECT * FROM __relationships;
```
```
┌──────────────┬───────────────────┬──────────────────┐
│ source_table │ target_table      │ relationship_type│
├──────────────┼───────────────────┼──────────────────┤
│ services     │ services_redis    │ parent-child     │
│ services     │ services_postgres │ parent-child     │
└──────────────┴───────────────────┴──────────────────┘
```

## Using Metadata Tables

### 1. List All Tables

```sql
-- Show all available tables
SELECT table_name, type, description 
FROM __tables 
ORDER BY type, table_name;
```

### 2. Find Child Tables

```sql
-- Find all children of a specific table
SELECT table_name, display_name 
FROM __tables 
WHERE parent_table = 'services';
```

### 3. Trace Relationships

```sql
-- Show table hierarchy
WITH RECURSIVE hierarchy AS (
  -- Start with root tables
  SELECT 
    table_name,
    0 as level,
    ARRAY[table_name] as path
  FROM __tables 
  WHERE parent_table IS NULL

  UNION ALL

  -- Add child tables
  SELECT 
    c.table_name,
    p.level + 1,
    p.path || c.table_name
  FROM __tables c
  JOIN hierarchy p ON c.parent_table = p.table_name
)
SELECT 
  REPEAT('  ', level) || table_name as structure,
  level,
  path
FROM hierarchy
ORDER BY path;
```

### 4. Find Related Tables

```sql
-- Find directly related tables
SELECT r.target_table, t.type, t.description
FROM __relationships r
JOIN __tables t ON r.target_table = t.table_name
WHERE r.source_table = 'services';
```

## Table Types

### 1. Root Tables
- `type = 'root'`
- Contains top-level scalar values
- No parent table

### 2. Section Tables
- `type = 'section'`
- Created from top-level objects
- May have child tables

### 3. Child Tables
- `type = 'child'`
- Created from nested objects/arrays
- Has a parent table

## Relationship Types

### 1. Parent-Child
- Most common relationship
- Shows structural hierarchy
- Example: services → services_redis

### 2. Reference
- Links related tables
- Not necessarily hierarchical
- Example: deployment → configmap

## Best Practices

### 1. Start with Discovery

Always check available tables:
```sql
SELECT table_name, type, description 
FROM __tables 
ORDER BY type;
```

### 2. Check Relationships

Before joining tables:
```sql
SELECT * FROM __relationships 
WHERE source_table = 'your_table' 
   OR target_table = 'your_table';
```

### 3. Use Display Names

For user-friendly output:
```sql
SELECT t1.display_name, t2.display_name
FROM your_table t1
JOIN other_table t2 ON /* ... */;
```

### 4. Validate Structure

Before complex queries:
```sql
-- Check table existence
SELECT COUNT(*) FROM __tables WHERE table_name = 'your_table';

-- Check relationships
SELECT COUNT(*) FROM __relationships 
WHERE source_table = 'table1' AND target_table = 'table2';
```

## Common Queries

### 1. Schema Overview

```sql
-- Get a summary of all tables
SELECT 
  type,
  COUNT(*) as count,
  STRING_AGG(table_name, ', ') as tables
FROM __tables 
GROUP BY type;
```

### 2. Relationship Map

```sql
-- Show all relationships with descriptions
SELECT 
  r.source_table,
  r.target_table,
  r.relationship_type,
  t1.description as source_desc,
  t2.description as target_desc
FROM __relationships r
JOIN __tables t1 ON r.source_table = t1.table_name
JOIN __tables t2 ON r.target_table = t2.table_name;
```

### 3. Orphan Tables

```sql
-- Find tables without relationships
SELECT table_name, type, description
FROM __tables t
WHERE NOT EXISTS (
  SELECT 1 FROM __relationships r
  WHERE r.source_table = t.table_name
     OR r.target_table = t.table_name
);
```

## Troubleshooting

### 1. Missing Tables
If a table is not in `__tables`:
- Table might be empty
- Table might not exist
- Check YAML structure

### 2. Missing Relationships
If relationships are not showing:
- Check table names
- Verify parent-child structure
- Check YAML nesting

### 3. Incorrect Types
If table types look wrong:
- Check YAML structure
- Verify transformation rules
- Look for nested objects

## Related Topics

- [Schema Transformation](schema-transformation.md)
- [Relationships](relationships.md)
- [Discover Command](../commands/discover.md)
- [SQL Query Command](../commands/sql.md) 