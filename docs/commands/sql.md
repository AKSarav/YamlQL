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
|---|---|---|
| `--file`, `-f` | YAML file to query | Required |
| `--output`, `-o` | Output format (`auto`, `table`, `list`) | `auto` |
| `--sql-file` | Path to a file containing the SQL query. | None |
| `--strategy` | The table creation strategy to use (`depth` or `adaptive`). | `depth` |
| `--max-depth`| Maximum recursion depth for the `depth` strategy. | `5` |

## Native List/Array Support

YamlQL stores YAML lists of scalars as DuckDB arrays (native LIST type). To ensure type safety and prevent errors, **all elements in these lists are converted to strings (VARCHAR)**. This allows you to reliably query lists with mixed types.

For example, given this YAML:
```yaml
mixed_list_options:
  - True
  - "Option A"
  - 123
```
The data will be stored as `['True', 'Option A', '123']`. You can then use DuckDB's array functions:

```sql
-- Safely access any element by index (it will be a string)
SELECT mixed_list_options[1] FROM my_table;

-- Unnest the array into individual rows
SELECT UNNEST(mixed_list_options) AS option FROM my_table;

-- Get the length of the array
SELECT ARRAY_LENGTH(mixed_list_options) FROM my_table;
```

## Running SQL from a File

For complex queries or to avoid shell quoting issues, use the `--sql-file` option:

```bash
yamlql sql -f file.yml --sql-file myquery.sql
```

## Query Examples

### Basic Queries

```bash
# Select all fields from a Docker Compose services table
yamlql sql -f docker-compose.yml "SELECT * FROM services"

# Select specific fields
yamlql sql -f docker-compose.yml "SELECT web_image, db_image FROM services"

# Filter results
yamlql sql -f docker-compose.yml "SELECT image FROM services_db WHERE image LIKE '%postgres%'"
```

### Working with Nested Data

```bash
# Query nested fields in Kubernetes manifests
yamlql sql -f deployment.yml "SELECT name, namespace FROM metadata"

# Query arrays stored as separate tables
yamlql sql -f docker-compose.yml "SELECT value FROM services_web_ports"
```

### Joins

```bash
# Join related tables in Docker Compose
yamlql sql -f docker-compose.yml "
  SELECT s.web_image, p.value as port 
  FROM services s 
  JOIN services_web_ports p ON true
"

# Join Kubernetes metadata and spec
yamlql sql -f deployment.yml "
  SELECT m.name, s.replicas 
  FROM metadata m 
  JOIN spec s ON true
"
```

### Aggregations

```bash
# Count services by image type (Docker Compose)
yamlql sql -f docker-compose.yml "
  SELECT 
    REGEXP_EXTRACT(web_image, '^[^:]+') as base_image,
    COUNT(*) as count 
  FROM services 
  GROUP BY base_image
"

# Analyze Kubernetes container resources
yamlql sql -f deployment.yml "
  SELECT 
    COUNT(*) as container_count,
    COUNT(DISTINCT image) as unique_images
  FROM spec_template_spec_containers
"
```

### Working with Arrays

```bash
# Unnest array values
yamlql sql -f docker-compose.yml "
  SELECT value as port
  FROM services_web_ports
"

# Check array length in flattened columns
yamlql sql -f docker-compose.yml "
  SELECT ARRAY_LENGTH(web_ports) as port_count 
  FROM services
  WHERE web_ports IS NOT NULL
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
- Available tables and their structures
- Column names and types
- How YamlQL transformed your YAML structure

### 2. Column Naming

- Nested fields use underscores: `web_image`, `db_image`
- Array tables have descriptive names: `services_web_ports`
- **Special characters are sanitized**: Hyphens, spaces, and periods in YAML keys are replaced with underscores (`_`). For example, `service-name` becomes `service_name`.
- Case sensitivity is preserved

### 3. Working with Tables

YamlQL creates different types of tables:
- **Main tables**: Direct mappings of YAML sections (e.g., `services`, `metadata`)
- **Detail tables**: Separate tables for complex nested objects (e.g., `services_web`, `services_db`)
- **Array tables**: Tables for arrays of scalars (e.g., `services_web_ports`)

### 4. Complex Queries

Use CTEs for better readability:
```bash
yamlql sql -f docker-compose.yml "
  WITH service_stats AS (
    SELECT 
      web_image,
      ARRAY_LENGTH(web_ports) as port_count
    FROM services
    WHERE web_ports IS NOT NULL
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
  yamlql sql -f config.yml "SELECT web_image, db_image FROM services" --output table
  ```

## Common Issues

### 1. Table Not Found
```
Error: Table 'unknown_table' not found
```
Solution: Use `discover` command to see available tables

### 2. Column Not Found
```
Error: Column 'unknown_field' not found
```
Solution: Use `discover` command to verify column names

### 3. Type Mismatch
```
Error: Type mismatch in comparison
```
Solution: Use appropriate type casting (CAST or ::)

### 4. Array Access
```
Error: Array index out of bounds
```
Solution: Check array length before accessing indices

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Docker Compose Guide](../guides/docker-compose.md)
- [Kubernetes Guide](../guides/kubernetes.md) 