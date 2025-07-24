# SQL Query Command

> **New in vX.X.X:** You can now run SQL queries directly with:
> ```bash
> yamlql -f file.yml "SELECT * FROM table_name"
> ```
> The `sql` subcommand is still available for compatibility:
> ```bash
> yamlql sql -f file.yml "SELECT * FROM table_name"
> ```

The `sql` command is the core feature of YamlQL, allowing you to query YAML files using standard SQL syntax.

## Basic Usage

```bash
yamlql -f file.yml "SELECT * FROM table_name"
# (or, equivalently)
yamlql sql -f file.yml "SELECT * FROM table_name"
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | YAML file to query | Required |
| `--output`, `-o` | Output format (`auto`, `table`, `list`) | `auto` |

## Query Examples

### Basic Queries

```bash
# Select all fields
yamlql sql -f docker-compose.yml "SELECT * FROM services"

# Select specific fields
yamlql sql -f docker-compose.yml "SELECT name, image FROM services"

# Filter results
yamlql sql -f docker-compose.yml "SELECT * FROM services WHERE image LIKE '%postgres%'"
```

### Working with Nested Data

```bash
# Query nested fields
yamlql sql -f config.yml "SELECT database_host, database_port FROM application"

# Query arrays
yamlql sql -f k8s.yml "SELECT name, ports FROM services"
```

### Joins

```bash
# Join parent and child tables
yamlql sql -f deployment.yml "
  SELECT c.name, c.image, s.replicas 
  FROM spec_template_spec_containers c 
  JOIN spec s ON true
"

# Using metadata relationships
yamlql sql -f config.yml "
  SELECT s.name, s.type, p.value 
  FROM services s 
  JOIN service_properties p ON p.service_id = s._id
"
```

### Aggregations

```bash
# Count services by image type
yamlql sql -f docker-compose.yml "
  SELECT 
    REGEXP_EXTRACT(image, '^[^:]+') as base_image,
    COUNT(*) as count 
  FROM services 
  GROUP BY base_image
"

# Find services with most environment variables
yamlql sql -f docker-compose.yml "
  SELECT 
    name,
    COUNT(*) as env_var_count 
  FROM services_environment 
  GROUP BY name 
  ORDER BY env_var_count DESC
"
```

### Using Metadata Tables

```bash
# List all available tables
yamlql sql -f config.yml "SELECT * FROM __tables"

# Show table relationships
yamlql sql -f config.yml "SELECT * FROM __relationships"

# Find child tables of a specific parent
yamlql sql -f config.yml "
  SELECT table_name 
  FROM __tables 
  WHERE parent_table = 'services'
"
```

## SQL Features Support

YamlQL uses DuckDB as its SQL engine, supporting most standard SQL features:

### Supported Features

- SELECT, WHERE, GROUP BY, HAVING, ORDER BY
- JOINs (INNER, LEFT, RIGHT, FULL OUTER)
- Subqueries and CTEs
- Window functions
- String functions (LIKE, REGEXP)
- Aggregation functions (COUNT, SUM, AVG)
- Type casting
- CASE expressions

### DuckDB-Specific Features

- REGEXP_EXTRACT for pattern matching
- Array functions for list handling
- JSON functions for complex values
- String splitting and concatenation
- Type inference and conversion

## Best Practices

### 1. Schema Discovery

Always start by discovering the schema:
```bash
yamlql discover -f your-file.yml
```

This helps you understand:
- Available tables
- Column names and types
- Table relationships

### 2. Column Naming

- Nested fields use underscores: `database_host`
- Array indices are preserved: `ports_0`, `ports_1`
- Special characters are escaped
- Case sensitivity is preserved

### 3. Working with Arrays

```bash
# Unnest array values
yamlql sql -f config.yml "
  SELECT name, UNNEST(ports) as port 
  FROM services
"

# Check array length
yamlql sql -f config.yml "
  SELECT name, ARRAY_LENGTH(ports) as port_count 
  FROM services
"
```

### 4. Complex Queries

Use CTEs for better readability:
```bash
yamlql sql -f docker-compose.yml "
  WITH service_stats AS (
    SELECT 
      name,
      ARRAY_LENGTH(ports) as port_count,
      ARRAY_LENGTH(volumes) as volume_count
    FROM services
  )
  SELECT * FROM service_stats 
  WHERE port_count > 0
"
```

### 5. Output Formatting

- Use `--output list` for wide tables:
  ```bash
  yamlql sql -f config.yml "SELECT * FROM services" --output list
  ```

- Use `--output table` for compact data:
  ```bash
  yamlql sql -f config.yml "SELECT name, port FROM services" --output table
  ```

## Common Issues

### 1. Column Not Found
```
Error: Column 'unknown_field' not found
```
Solution: Use `discover` command to verify column names

### 2. Type Mismatch
```
Error: Type mismatch in comparison
```
Solution: Use appropriate type casting (CAST or ::)

### 3. Array Access
```
Error: Array index out of bounds
```
Solution: Check array length before accessing indices

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Metadata Tables](../concepts/metadata-tables.md)
- [Relationships](../concepts/relationships.md)
- [Docker Compose Guide](../guides/docker-compose.md)
- [Kubernetes Guide](../guides/kubernetes.md) 