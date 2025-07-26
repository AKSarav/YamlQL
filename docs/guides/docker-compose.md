# Docker Compose Guide

YamlQL makes it easy to analyze and query Docker Compose files. This guide shows how to effectively query service configurations, networks, volumes, and more.

## Basic Structure

### Simple Docker Compose File

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: admin
```

Tables Created by YamlQL:
```bash
yamlql discover -f docker-compose.yml
```

Results in tables like:
- `services` - Flattened overview of all services
- `services_web` - Detailed web service configuration  
- `services_db` - Detailed db service configuration
- `services_web_ports` - Web service port mappings
- `services_db_environment` - Database environment variables

## Common Queries

### 1. Service Discovery

```sql
-- List all service images from the main services table
SELECT web_image, db_image 
FROM services;

-- Find services by image type
SELECT image 
FROM services_web 
WHERE image LIKE '%nginx%';

-- Get web service ports
SELECT value as port_mapping
FROM services_web_ports;
```

### 2. Environment Variables

```sql
-- List database environment variables
SELECT POSTGRES_DB, POSTGRES_USER
FROM services_db;

-- Check environment configuration from detail table
SELECT *
FROM services_db_environment;

-- Find services with specific environment settings
SELECT image
FROM services_db
WHERE environment_POSTGRES_DB = 'myapp';
```

### 3. Volume Mounts

```sql
-- List volume mounts for web service
SELECT value as volume_mount
FROM services_web_volumes;

-- Find services with bind mounts
SELECT image
FROM services_web
WHERE EXISTS (
    SELECT 1 FROM services_web_volumes v 
    WHERE v.value LIKE './%'
);
```

## Advanced Use Cases

### 1. Multi-Service Analysis

```sql
-- Compare service configurations
SELECT 
    'web' as service_name, 
    web_image as image,
    ARRAY_LENGTH(web_ports) as port_count
FROM services
UNION ALL
SELECT 
    'db' as service_name,
    db_image as image, 
    0 as port_count
FROM services;

-- Find services with port mappings
SELECT 
    CASE 
        WHEN web_ports IS NOT NULL THEN 'web'
        WHEN db_ports IS NOT NULL THEN 'db'
    END as service_with_ports
FROM services
WHERE web_ports IS NOT NULL OR db_ports IS NOT NULL;
```

### 2. Resource and Configuration Analysis

```sql
-- Analyze environment variable count by service
SELECT 
    'db' as service,
    COUNT(*) as env_var_count
FROM services_db_environment
UNION ALL
SELECT 
    'web' as service,
    0 as env_var_count;

-- Check for exposed ports across all services
SELECT 
    s.web_image as image,
    p.value as port
FROM services s
JOIN services_web_ports p ON true
WHERE s.web_image IS NOT NULL;
```

### 3. Dependency and Network Analysis

```sql
-- Find services that depend on databases
SELECT web_image as dependent_service
FROM services 
WHERE db_image LIKE '%postgres%' OR db_image LIKE '%mysql%';

-- Analyze service isolation (services without port exposure)
SELECT db_image as isolated_service
FROM services
WHERE db_ports IS NULL AND db_image IS NOT NULL;
```

## Complex Multi-Service Examples

### Large Docker Compose File

```yaml
# docker-compose-complex.yml
version: '3.8'
services:
  frontend:
    image: react-app:latest
    ports:
      - "3000:3000"
    depends_on:
      - backend
  backend:
    image: node-api:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/app
    depends_on:
      - db
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
```

Complex Queries:
```sql
-- Map service dependencies
SELECT 
    backend_image as service,
    'depends on database' as dependency_info
FROM services 
WHERE backend_environment_DATABASE_URL LIKE '%postgres%';

-- Find all exposed ports
SELECT 
    frontend_ports as frontend_ports,
    backend_ports as backend_ports
FROM services
WHERE frontend_ports IS NOT NULL OR backend_ports IS NOT NULL;

-- Service dependency chain analysis
SELECT 
    CASE 
        WHEN frontend_image IS NOT NULL THEN 'frontend -> backend -> db'
        WHEN backend_image IS NOT NULL THEN 'backend -> db'
        WHEN db_image IS NOT NULL THEN 'db (base service)'
    END as dependency_chain
FROM services;
```

## Best Practices

### 1. Schema Discovery First

Always start with understanding your table structure:
```bash
yamlql discover -f docker-compose.yml
```

This shows you:
- Which services became separate tables
- How environment variables are structured
- Where arrays like ports and volumes are stored

### 2. Working with Flattened Data

YamlQL flattens service configurations into the main `services` table:
```sql
-- Access flattened service data
SELECT 
    web_image,
    web_ports,
    db_image, 
    db_environment_POSTGRES_DB
FROM services;
```

### 3. Querying Detail Tables

Use detail tables for comprehensive service analysis:
```sql
-- Get complete service configuration
SELECT * FROM services_web;
SELECT * FROM services_db;

-- Analyze specific aspects
SELECT * FROM services_web_ports;
SELECT * FROM services_db_environment;
```

### 4. Handling Arrays

```sql
-- Unnest port arrays from detail tables
SELECT value as individual_port
FROM services_web_ports;

-- Check array lengths in flattened data
SELECT 
    web_image,
    ARRAY_LENGTH(web_ports) as port_count
FROM services
WHERE web_ports IS NOT NULL;
```

## Troubleshooting

### 1. Missing Services
If services don't appear as expected:
- Check for YAML syntax errors
- Verify service names are valid
- Use `yamlql discover` to see actual table structure

### 2. Environment Variables
Environment variables appear in multiple places:
- Flattened in main `services` table as `service_environment_KEY`
- Detailed in `services_servicename_environment` tables

### 3. Port and Volume Mapping
- Ports appear as arrays in flattened columns and as separate tables
- Volume mounts are stored as arrays and can be queried with UNNEST

## Integration Examples

### CI/CD Pipeline Analysis

```sql
-- Find services that expose public ports
SELECT 
    web_image as public_service,
    web_ports as exposed_ports
FROM services 
WHERE web_ports IS NOT NULL;

-- Check for hardcoded credentials (security audit)
SELECT 
    'Database service has hardcoded password' as security_issue
FROM services_db_environment
WHERE POSTGRES_PASSWORD IS NOT NULL;
```

### Infrastructure Planning

```sql
-- Resource requirements analysis
SELECT 
    COUNT(DISTINCT web_image) + 
    COUNT(DISTINCT db_image) as total_unique_images
FROM services;

-- Network topology mapping
SELECT 
    CASE 
        WHEN web_ports IS NOT NULL THEN 'public-facing'
        ELSE 'internal'
    END as service_type,
    COUNT(*) as service_count
FROM services
GROUP BY service_type;
```

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Kubernetes Guide](kubernetes.md)
- [Complex YAML Guide](complex-yaml.md)
- [SQL Query Command](../commands/sql.md) 