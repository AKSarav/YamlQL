# Quick Start Guide

This guide will help you get started with YamlQL by walking through common use cases and examples.

## Basic Usage

### 1. Discovering Schema

Before querying a YAML file, it's helpful to understand its structure. Use the `discover` command:

```bash
yamlql discover -f your-file.yml
```

This will show the tables and columns created by YamlQL's default `depth` transformation strategy.

**Advanced Tip:** YamlQL offers two transformation strategies: `depth` (default) and `adaptive`. The `adaptive` strategy is great for complex files like Kubernetes manifests. You can learn more in our guide to [Schema Transformation](../concepts/schema-transformation.md).

```bash
# Try the adaptive strategy on a complex file
yamlql discover -f k8s.yaml --strategy adaptive
```

### 2. Running SQL Queries

Once you know the schema, you can run SQL queries:

```bash
# Simple SELECT
yamlql sql -f docker-compose.yml "SELECT * FROM services"

# Filtering
yamlql sql -f docker-compose.yml "SELECT web_image, db_image FROM services WHERE web_image LIKE '%nginx%'"

# Using list output for better readability
yamlql sql -f docker-compose.yml "SELECT * FROM services" --output list

# For complex queries, use a SQL file
yamlql sql -f docker-compose.yml --sql-file myquery.sql
```

### Working with Lists/Arrays

If your YAML contains a list of scalars (strings, numbers, booleans), it is stored as a native DuckDB `LIST` type. To ensure type safety, especially for lists with mixed types, **all list elements are automatically converted to strings**.

For example, given this YAML with a mixed-type list:
```yaml
config:
  - name: feature_A
    options: [True, 'A', 123]
```
The `options` column will be stored as a `LIST<VARCHAR>` (a list of strings). You can then use DuckDB's array functions to query it:
```sql
-- Safely access any element by index (it will be a string)
SELECT name, options[1] AS first_option FROM config;

-- Unnest the array into individual rows
SELECT name, UNNEST(options) AS option FROM config;
```

### 3. Using AI Queries

Ask questions in natural language:

```bash
# First set up your LLM provider
export YAMLQL_LLM_PROVIDER="OpenAI"
export OPENAI_API_KEY="your-api-key"

# Then ask questions
yamlql ai -f deployment.yml "What is the CPU limit for the nginx container?"
```

## Common Use Cases

### Docker Compose Files

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

Discover schema:
```bash
yamlql discover -f docker-compose.yml
# Results in tables like: services, services_web, services_db, services_web_ports
```

Query:
```bash
# List all service images from the main services table
yamlql sql -f docker-compose.yml "SELECT web_image, db_image FROM services"

# Get detailed web service info
yamlql sql -f docker-compose.yml "SELECT * FROM services_web"

# Find services using specific images
yamlql sql -f docker-compose.yml "SELECT image FROM services_db WHERE image LIKE '%postgres%'"
```

### Kubernetes Manifests

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
        image: nginx:latest
        resources:
          limits:
            cpu: "200m"
```

Query:
```bash
# Get deployment metadata
yamlql sql -f deployment.yml "SELECT name, namespace FROM metadata"

# Get replica count
yamlql sql -f deployment.yml "SELECT replicas FROM spec"

# Get container resource limits (if containers table is created)
yamlql sql -f deployment.yml "SELECT name, resources_limits_cpu FROM spec_template_spec_containers"

# Or use AI
yamlql ai -f deployment.yml "What containers are defined and what are their resource limits?"
```

### Complex Configuration Files

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

Query:
```bash
# Get application details
yamlql sql -f config.yml "SELECT name FROM application"

# List enabled features
yamlql sql -f config.yml "SELECT name FROM application_features WHERE enabled = true"
```

## Understanding Table Names

YamlQL creates table names based on your YAML structure:

1. **Root-level keys** become table names (e.g., `services`, `metadata`, `spec`)
2. **Nested objects** become separate tables with underscore-separated names (e.g., `services_web`, `services_db`)  
3. **Arrays of objects** create separate tables for each item (e.g., `services_web_ports`)
4. **Flattened fields** appear as columns with underscore-separated names (e.g., `web_image`, `db_image`)

## Tips and Best Practices

1. **Always Start with Discover**
   ```bash
   yamlql discover -f your-file.yml
   ```
   This helps you understand the schema before writing queries.

2. **Use List Output for Wide Tables**
   ```bash
   yamlql sql -f your-file.yml "SELECT * FROM complex_table" --output list
   ```

3. **Work with Arrays**
   ```bash
   # Unnest array values
   yamlql sql -f config.yml "SELECT name, UNNEST(ports) as port FROM services_web_ports"
   
   # Check array length
   yamlql sql -f config.yml "SELECT ARRAY_LENGTH(web_ports) as port_count FROM services"
   ```

4. **Use Environment Variables for Repeated Queries**
   ```bash
   export YAMLQL_FILE="your-file.yml"
   export YAMLQL_MODE="SQL"
   yamlql -e "SELECT * FROM services"
   ```

## Next Steps

- Learn about [Configuration](configuration.md)
- Explore [SQL Commands](../commands/sql.md)
- Understand [Schema Transformation](../concepts/schema-transformation.md)
- Check out [Advanced Guides](../guides/complex-yaml.md) 