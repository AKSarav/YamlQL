# Discover Command

The `discover` command helps you understand the structure of your YAML file by showing available tables, their columns, and relationships.

## Basic Usage

```bash
yamlql discover -f your-file.yml
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | YAML file to analyze | Required |

## Understanding the Output

The discover command output is organized into sections:

### 1. Metadata Tables

```
Metadata Tables:
╭────── __tables ──────╮
│ table_name: VARCHAR  │
│ parent_table: VARCHAR│
│ type: VARCHAR        │
╰──────────────────────╯

╭──── __relationships ────╮
│ source_table: VARCHAR  │
│ target_table: VARCHAR  │
╰────────────────────────╯
```

### 2. Data Tables

```
Data Tables:
╭────── services ──────╮
│ name: VARCHAR        │
│ image: VARCHAR       │
│ ports: VARCHAR[]     │
╰──────────────────────╯
```

## Example Outputs

### Docker Compose File

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
    ports:
      - "5432:5432"
```

Discover output:
```
Metadata Tables:
- __tables (Lists all available tables)
- __relationships (Shows table relationships)

Data Tables:
- root (version)
- services (name, image, ports)
```

### Kubernetes Deployment

```yaml
# deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nginx
        image: nginx
```

Discover output:
```
Metadata Tables:
- __tables
- __relationships

Data Tables:
- root (apiVersion, kind)
- metadata (name)
- spec (replicas)
- spec_template_spec_containers (name, image)
```

## Understanding Table Types

### 1. Root Tables
- Contains top-level scalar values
- Named `root` by default
- Example: `version`, `apiVersion`, `kind`

### 2. Section Tables
- Created from top-level objects
- Named after the section
- Example: `services`, `metadata`, `spec`

### 3. Child Tables
- Created from nested objects or arrays
- Named with parent prefix
- Example: `spec_template_spec_containers`

### 4. Metadata Tables
- Start with `__`
- Provide schema information
- Example: `__tables`, `__relationships`

## Using Discover Results

### 1. Planning Queries

The discover output helps you:
- Identify available tables
- Understand column names and types
- See relationships between tables

Example:
```bash
# First discover the schema
yamlql discover -f docker-compose.yml

# Then write queries using the discovered structure
yamlql sql -f docker-compose.yml "SELECT name, image FROM services"
```

### 2. Understanding Relationships

The `__relationships` table shows how tables are connected:
```bash
yamlql sql -f config.yml "SELECT * FROM __relationships"
```

Output:
```
┌──────────────┬─────────────┬──────────────────┐
│ source_table │ target_table│ relationship_type│
├──────────────┼─────────────┼──────────────────┤
│ spec         │ containers  │ parent-child     │
└──────────────┴─────────────┴──────────────────┘
```

### 3. Finding Child Tables

Use `__tables` to find all child tables of a parent:
```bash
yamlql sql -f config.yml "
  SELECT table_name 
  FROM __tables 
  WHERE parent_table = 'services'
"
```

## Best Practices

### 1. Always Discover First
Run discover before writing queries to understand the schema:
```bash
yamlql discover -f your-file.yml
```

### 2. Note Column Types
Pay attention to column types for:
- String comparisons (VARCHAR)
- Numeric operations (INTEGER, FLOAT)
- Array handling (VARCHAR[])

### 3. Check Relationships
Use metadata tables to understand table connections:
```bash
yamlql sql -f your-file.yml "SELECT * FROM __relationships"
```

### 4. Understand Naming Patterns
- Nested fields use underscores
- Arrays are flattened with indices
- Special characters are escaped

## Common Issues

### 1. Missing Tables
If expected tables are missing:
- Check if they contain any data
- Verify the YAML structure
- Look for nested objects

### 2. Unexpected Column Names
If column names look different:
- Check for special character handling
- Understand nesting conversion
- Verify array handling

### 3. Type Confusion
If column types are unexpected:
- Check the original YAML values
- Understand type inference rules
- Consider explicit type casting

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Metadata Tables](../concepts/metadata-tables.md)
- [SQL Query Command](sql.md)
- [Complex YAML Guide](../guides/complex-yaml.md) 