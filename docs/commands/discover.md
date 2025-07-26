# Discover Command

The `discover` command helps you understand the structure of your YAML file by showing available tables, their columns, and data types.

## Basic Usage

```bash
yamlql discover -f your-file.yml
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | YAML file to analyze | Required |

## Understanding the Output

The discover command shows you exactly what tables and columns YamlQL has created from your YAML structure.

### Table Display Format

Each table is displayed with its name and all available columns with their data types:

```
╭────── services ──────╮
│ web_image: VARCHAR   │
│ web_ports: VARCHAR[] │
│ db_image: VARCHAR    │
╰──────────────────────╯
```

### Data Types

YamlQL uses these DuckDB data types:
- `VARCHAR` - String values
- `BIGINT` - Integer numbers  
- `DOUBLE` - Floating point numbers
- `BOOLEAN` - True/false values
- `VARCHAR[]` - Arrays of strings (all array elements converted to strings for type safety)

## Example Outputs

### Docker Compose File

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: myapp
```

Running `yamlql discover -f docker-compose.yml` shows:

```
╭─────── services ───────╮
│ web_image: VARCHAR     │
│   web_ports: VARCHAR[] │
│   db_image: VARCHAR    │
╰────────────────────────╯
╭───── services_web ─────╮
│ image: VARCHAR         │
╰────────────────────────╯
╭─────────── services_db ────────────╮
│ image: VARCHAR                     │
│   environment_POSTGRES_DB: VARCHAR │
╰────────────────────────────────────╯
╭─ services_web_ports ─╮
│ value: VARCHAR       │
╰──────────────────────╯
```

### Kubernetes Deployment

```yaml
# deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        resources:
          limits:
            cpu: "200m"
        ports:
        - containerPort: 80
```

Running `yamlql discover -f deployment.yml` shows:

```
╭────── metadata ──────╮
│ name: VARCHAR        │
│   namespace: VARCHAR │
╰──────────────────────╯
╭────── spec ──────╮
│ replicas: BIGINT │
╰──────────────────╯
╭──── spec_template_spec_containers ────╮
│ name: VARCHAR                         │
│   image: VARCHAR                      │
│   resources_limits_cpu: VARCHAR       │
╰───────────────────────────────────────╯
╭── spec_template_spec_containers_ports ──╮
│ containerPort: BIGINT                   │
╰─────────────────────────────────────────╯
```

### Complex Configuration

```yaml
# config.yml
application:
  name: user-service
  database:
    host: db.example.com
    port: 5432
  features:
    - name: login
      enabled: true
    - name: signup
      enabled: false
```

Running `yamlql discover -f config.yml` shows:

```
╭───────── application ──────────╮
│ name: VARCHAR                  │
│   database_host: VARCHAR       │
│   database_port: BIGINT        │
╰────────────────────────────────╯
╭─ application_features ─╮
│ name: VARCHAR          │
│   enabled: BOOLEAN     │
╰────────────────────────╯
```

## Understanding Table Names

YamlQL creates table names based on your YAML structure:

### 1. Root-Level Objects
Top-level keys in your YAML become table names:
- `services` → `services` table
- `metadata` → `metadata` table
- `spec` → `spec` table

### 2. Nested Objects
Nested structures create separate tables with underscore-separated names:
- `services.web` → `services_web` table
- `spec.template.spec.containers` → `spec_template_spec_containers` table

### 3. Arrays
Arrays create separate tables for their contents:
- `services.web.ports` → `services_web_ports` table
- `spec.template.spec.containers.ports` → `spec_template_spec_containers_ports` table

### 4. Flattened Columns
Simple nested values become flattened columns in parent tables:
- `database.host` → `database_host` column
- `environment.POSTGRES_DB` → `environment_POSTGRES_DB` column

## Using Discover Output

### 1. Planning Queries

Use the table and column information to write SQL queries:

```bash
# After seeing tables from discover
yamlql sql -f docker-compose.yml "SELECT web_image, db_image FROM services"
yamlql sql -f deployment.yml "SELECT name, namespace FROM metadata"
```

### 2. Understanding Data Distribution

The discover output shows you:
- **Main tables**: Overview data with flattened columns
- **Detail tables**: Complete configuration for specific components  
- **Array tables**: List data in normalized form

### 3. Finding Your Data

If you can't find a field:
1. Check flattened columns in parent tables (with underscore notation)
2. Look in detail tables for the specific component
3. Remember all original data is preserved somewhere

## Common Patterns

### 1. Docker Compose
- `services` - Main table with flattened service data
- `services_[name]` - Detail table for each service
- `services_[name]_[array]` - Array data for each service

### 2. Kubernetes
- `metadata` - Resource metadata
- `spec` - Resource specification
- `spec_[path]_[object]` - Nested objects in spec

### 3. Configuration Files
- `[section]` - Main configuration sections
- `[section]_[subsection]` - Nested configuration
- `[section]_[array]` - Lists within sections

## Tips

### 1. Always Run Discover First
Before writing any queries, understand your schema:
```bash
yamlql discover -f your-file.yml
```

### 2. Look for Patterns
YamlQL follows consistent naming patterns - once you understand them for one file type, you can predict them for similar files.

### 3. Use List Output for Complex Tables
For wide tables, use list output to see all columns:
```bash
yamlql sql -f your-file.yml "SELECT * FROM complex_table LIMIT 1" --output list
```

### 4. Remember Data Preservation
YamlQL preserves all your original data - if you can't find something, look for flattened columns or related tables.

## Related Topics

- [SQL Query Command](sql.md)
- [Schema Transformation](../concepts/schema-transformation.md)
- [Docker Compose Guide](../guides/docker-compose.md)
- [Kubernetes Guide](../guides/kubernetes.md) 