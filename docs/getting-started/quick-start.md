# Quick Start Guide

This guide will help you get started with YamlQL by walking through common use cases and examples.

## Basic Usage

### 1. Discovering Schema

Before querying a YAML file, it's helpful to understand its structure. Use the `discover` command:

```bash
yamlql discover -f your-file.yml
```

This will show:
- Available tables
- Column names and types
- Relationships between tables
- Metadata tables for advanced querying

### 2. Running SQL Queries

Once you know the schema, you can run SQL queries:

```bash
# Simple SELECT (new default, recommended)
yamlql -f docker-compose.yml "SELECT * FROM services"

# Filtering
yamlql -f docker-compose.yml "SELECT name, image FROM services WHERE image LIKE '%postgres%'"

# Using list output for better readability
yamlql -f docker-compose.yml "SELECT * FROM services" --output list

# (Alternatively, you can use the explicit subcommand)
yamlql sql -f docker-compose.yml "SELECT * FROM services"
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
  postgres:
    image: postgres:14
    ports:
      - "5432:5432"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

Query:
```bash
# List all service ports
yamlql sql -f docker-compose.yml "SELECT name, ports FROM services"

# Find services using specific images
yamlql sql -f docker-compose.yml "SELECT * FROM services WHERE image LIKE '%postgres%'"
```

### Kubernetes Manifests

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
        image: nginx:latest
        resources:
          limits:
            cpu: "200m"
```

Query:
```bash
# Get container resource limits
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
yamlql sql -f config.yml "SELECT name FROM features WHERE enabled = true"
```

## Using Metadata Tables

YamlQL creates special metadata tables to help understand the data structure:

```bash
# List all available tables
yamlql sql -f your-file.yml "SELECT * FROM __tables"

# Show relationships between tables
yamlql sql -f your-file.yml "SELECT * FROM __relationships"
```

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

3. **Leverage Metadata Tables**
   - `__tables`: Lists all available tables
   - `__relationships`: Shows table relationships

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