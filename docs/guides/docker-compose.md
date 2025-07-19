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

Tables Created:
```sql
-- Root level
SELECT * FROM root;  -- Contains version

-- Services
SELECT * FROM services;  -- List of services

-- Service details
SELECT * FROM services_web;    -- Web service config
SELECT * FROM services_db;     -- DB service config
```

## Common Queries

### 1. Service Discovery

```sql
-- List all services
SELECT display_name, image 
FROM __services;

-- Find services by image
SELECT display_name 
FROM __services 
WHERE image LIKE '%postgres%';

-- Get service ports
SELECT 
    s.display_name as service,
    p.value as port_mapping
FROM __services s
JOIN ports p ON true
WHERE p.value IS NOT NULL;
```

### 2. Environment Variables

```sql
-- List all environment variables
SELECT 
    s.display_name as service,
    e.key,
    e.value
FROM __services s
JOIN environment e ON true
ORDER BY service;

-- Find specific configs
SELECT display_name, environment_POSTGRES_DB
FROM services
WHERE environment_POSTGRES_DB IS NOT NULL;
```

### 3. Volume Mounts

```sql
-- List all volume mounts
SELECT 
    s.display_name as service,
    v.source,
    v.target
FROM __services s
JOIN volumes v ON true;

-- Find named volumes
SELECT DISTINCT volume_name
FROM volumes
WHERE volume_name NOT LIKE './%';
```

## Advanced Use Cases

### 1. Network Analysis

```sql
-- Find exposed ports
SELECT 
    s.display_name as service,
    p.host_port,
    p.container_port
FROM __services s
JOIN ports p ON true
WHERE p.host_port IS NOT NULL;

-- Services in networks
SELECT 
    s.display_name as service,
    n.value as network
FROM __services s
JOIN networks n ON true;
```

### 2. Dependency Mapping

```sql
-- Show service dependencies
SELECT 
    s.display_name as service,
    d.value as depends_on
FROM __services s
JOIN depends_on d ON true
ORDER BY service;

-- Build dependency tree
WITH RECURSIVE deps AS (
    -- Base services (no dependencies)
    SELECT 
        display_name as service,
        0 as level
    FROM __services s
    WHERE NOT EXISTS (
        SELECT 1 FROM depends_on d
        WHERE d.service_id = s._id
    )
    
    UNION ALL
    
    -- Services that depend on others
    SELECT 
        s.display_name,
        d.level + 1
    FROM __services s
    JOIN depends_on dep ON dep.service_id = s._id
    JOIN deps d ON d.service = dep.value
)
SELECT 
    REPEAT('  ', level) || service as dependency_tree,
    level
FROM deps
ORDER BY level, service;
```

### 3. Resource Usage

```sql
-- Memory limits
SELECT 
    display_name as service,
    deploy_resources_limits_memory as memory_limit,
    deploy_resources_reservations_memory as memory_reservation
FROM __services
WHERE deploy_resources_limits_memory IS NOT NULL
   OR deploy_resources_reservations_memory IS NOT NULL;

-- CPU allocation
SELECT 
    display_name as service,
    deploy_resources_limits_cpus as cpu_limit,
    deploy_resources_reservations_cpus as cpu_reservation
FROM __services
WHERE deploy_resources_limits_cpus IS NOT NULL
   OR deploy_resources_reservations_cpus IS NOT NULL;
```

## Common Patterns

### 1. Service Templates

```sql
-- Find services using the same image
SELECT 
    image,
    STRING_AGG(display_name, ', ') as services,
    COUNT(*) as count
FROM __services
GROUP BY image
HAVING COUNT(*) > 1;

-- Compare service configurations
SELECT 
    s1.display_name as service1,
    s2.display_name as service2
FROM __services s1
JOIN __services s2 
    ON s1.image = s2.image 
    AND s1.display_name < s2.display_name;
```

### 2. Health Checks

```sql
-- List health check configurations
SELECT 
    display_name as service,
    healthcheck_test,
    healthcheck_interval,
    healthcheck_timeout
FROM __services
WHERE healthcheck_test IS NOT NULL;

-- Find services without health checks
SELECT display_name
FROM __services s
WHERE NOT EXISTS (
    SELECT 1 FROM healthcheck h
    WHERE h.service_id = s._id
);
```

### 3. Volume Management

```sql
-- Named volumes
SELECT 
    volume_name,
    COUNT(*) as usage_count
FROM volumes
WHERE volume_name NOT LIKE './%'
GROUP BY volume_name;

-- Bind mounts
SELECT 
    s.display_name as service,
    v.source,
    v.target,
    v.mode
FROM __services s
JOIN volumes v ON true
WHERE v.source LIKE './%';
```

## Best Practices

### 1. Service Discovery

Always start with metadata:
```sql
-- Get service overview
SELECT 
    display_name,
    image,
    (SELECT COUNT(*) FROM ports p WHERE p.service_id = s._id) as port_count,
    (SELECT COUNT(*) FROM volumes v WHERE v.service_id = s._id) as volume_count
FROM __services s;
```

### 2. Environment Variables

Handle environment variables carefully:
```sql
-- Check for sensitive info
SELECT 
    s.display_name as service,
    e.key
FROM __services s
JOIN environment e ON true
WHERE LOWER(e.key) LIKE '%password%'
   OR LOWER(e.key) LIKE '%secret%'
   OR LOWER(e.key) LIKE '%key%';
```

### 3. Version Compatibility

Check version-specific features:
```sql
-- Get compose version
SELECT version FROM root;

-- Find version-specific configs
SELECT display_name
FROM __services
WHERE deploy_resources_limits_cpus IS NOT NULL  -- v3+ feature
```

## Troubleshooting

### 1. Missing Services
- Check service names
- Verify YAML structure
- Look for syntax errors

### 2. Port Mapping
- Check port format
- Verify host/container ports
- Handle port ranges

### 3. Volume Issues
- Verify volume syntax
- Check named volumes
- Handle relative paths

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Kubernetes Guide](kubernetes.md)
- [Complex YAML Guide](complex-yaml.md)
- [SQL Query Command](../commands/sql.md) 