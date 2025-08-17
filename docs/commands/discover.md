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
| `--strategy` | The table creation strategy to use (`depth` or `adaptive`). | `depth` |
| `--max-depth` | Maximum recursion depth for the `depth` strategy. | `5` |

## Transformation Strategies

YamlQL provides two different strategies for transforming your YAML file into database tables. You can choose the one that best suits the structure of your data.

### `depth` Strategy (Default)

This is the default strategy. It creates tables by recursing through your YAML file up to a specified depth.

*   **How it works:** It walks through your nested objects and creates a new table for each one, until it reaches the limit specified by `--max-depth`.
*   **Best for:** Files with a consistent, predictable structure.
*   **Controls:**
    *   `--strategy depth`: Explicitly select the depth strategy.
    *   `--max-depth <number>`: Control how many levels deep the transformer will go before it starts flattening objects. A lower number (e.g., 2) will create fewer, wider tables. A higher number will create more, smaller tables.

```bash
# Use the default depth of 5
yamlql discover -f your-file.yml

# Limit the recursion to 2 levels for a flatter schema
yamlql discover -f your-file.yml --max-depth 2
```

### `adaptive` Strategy

This strategy intelligently analyzes the content of your YAML file to create a more intuitive schema.

*   **How it works:** It follows a simple set of rules:
    1.  Top-level key-value pairs that are not objects are collected into a single `root` table.
    2.  Each top-level object (dictionary or list) becomes its own base table (e.g., `metadata`, `spec`).
    3.  As it processes nested objects, it creates new tables with hierarchical names (e.g., `spec_template`).
*   **Best for:** Complex or inconsistently structured files, like Kubernetes manifests.
*   **Controls:**
    *   `--strategy adaptive`: Select the adaptive strategy. The `--max-depth` flag is ignored in this mode.

```bash
# Use the adaptive strategy for a complex Kubernetes file
yamlql discover -f k8s.yaml --strategy adaptive
```

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
- `spec.template.spec.containers` → `