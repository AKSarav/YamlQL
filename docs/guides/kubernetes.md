# Kubernetes Files Guide

YamlQL is particularly useful for querying Kubernetes manifests. This guide shows how to effectively query different types of Kubernetes resources.

## Common Resource Types

### 1. Deployments

```yaml
# deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        resources:
          limits:
            cpu: "200m"
            memory: "256Mi"
          requests:
            cpu: "100m"
            memory: "128Mi"
        ports:
        - containerPort: 80
```

Common Queries:
```sql
-- Get container resource limits
SELECT 
    name,
    resources_limits_cpu,
    resources_limits_memory
FROM spec_template_spec_containers;

-- Find containers by image
SELECT name, image 
FROM spec_template_spec_containers 
WHERE image LIKE '%nginx%';

-- Get replica counts
SELECT name, spec_replicas 
FROM root 
JOIN spec ON true;
```

### 2. Services

```yaml
# service.yml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

Common Queries:
```sql
-- List service ports
SELECT 
    metadata_name as service,
    p.port,
    p.targetPort
FROM root
JOIN spec_ports p ON true;

-- Find services by type
SELECT metadata_name 
FROM root 
WHERE spec_type = 'ClusterIP';
```

### 3. ConfigMaps

```yaml
# configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.host: db.example.com
  database.port: "5432"
  log.level: debug
```

Common Queries:
```sql
-- Get all config values
SELECT key, value 
FROM data;

-- Find specific settings
SELECT value 
FROM data 
WHERE key LIKE 'database.%';
```

## Common Use Cases

### 1. Resource Management

```sql
-- Find pods with high resource requests
SELECT 
    metadata_name as pod,
    c.name as container,
    c.resources_requests_cpu,
    c.resources_requests_memory
FROM root
JOIN spec_template_spec_containers c ON true
WHERE CAST(REPLACE(c.resources_requests_cpu, 'm', '') AS INTEGER) > 500;
```

### 2. Image Auditing

```sql
-- Find containers using latest tag
SELECT 
    metadata_name as deployment,
    c.name as container,
    c.image
FROM root
JOIN spec_template_spec_containers c ON true
WHERE c.image LIKE '%:latest%';

-- Group by image version
SELECT 
    REGEXP_EXTRACT(c.image, ':(.*?)$') as version,
    COUNT(*) as count
FROM spec_template_spec_containers c
GROUP BY version;
```

### 3. Network Analysis

```sql
-- List all exposed ports
SELECT 
    metadata_name as service,
    p.port,
    p.targetPort,
    p.nodePort
FROM root
JOIN spec_ports p ON true
WHERE spec_type = 'NodePort';

-- Find internal services
SELECT metadata_name 
FROM root 
WHERE spec_type = 'ClusterIP';
```

## Multi-Resource Queries

### 1. Service-Deployment Matching

```sql
-- Find services without matching deployments
WITH service_selectors AS (
    SELECT 
        metadata_name as service,
        spec_selector_app as app
    FROM services
),
deployment_labels AS (
    SELECT 
        metadata_name as deployment,
        spec_template_metadata_labels_app as app
    FROM deployments
)
SELECT s.* 
FROM service_selectors s
LEFT JOIN deployment_labels d ON s.app = d.app
WHERE d.app IS NULL;
```

### 2. ConfigMap Usage

```sql
-- Find pods using configmaps
SELECT 
    d.metadata_name as deployment,
    v.configMap_name as configmap
FROM root d
JOIN spec_template_spec_volumes v ON true
WHERE v.configMap_name IS NOT NULL;
```

### 3. Resource Relationships

```sql
-- Show service to pod mappings
SELECT 
    s.metadata_name as service,
    d.metadata_name as deployment
FROM services s
JOIN deployments d ON s.spec_selector_app = d.spec_template_metadata_labels_app;
```

## Best Practices

### 1. Use Metadata Tables

Always check available tables first:
```sql
SELECT table_name, type 
FROM __tables 
ORDER BY type;
```

### 2. Handle Labels and Selectors

Labels often need special handling:
```sql
-- Find matching labels
SELECT * 
FROM metadata_labels l
JOIN spec_selector_matchLabels s 
  ON l.key = s.key 
  AND l.value = s.value;
```

### 3. Resource Limits

Convert resource values to comparable units:
```sql
-- Standardize CPU units
SELECT 
    name,
    CASE 
        WHEN resources_limits_cpu LIKE '%m' 
        THEN CAST(REPLACE(resources_limits_cpu, 'm', '') AS FLOAT) / 1000
        ELSE CAST(resources_limits_cpu AS FLOAT)
    END as cpu_cores
FROM spec_template_spec_containers;
```

## Common Patterns

### 1. Finding Resources

```sql
-- By namespace
SELECT metadata_name 
FROM root 
WHERE metadata_namespace = 'production';

-- By label
SELECT metadata_name 
FROM root 
WHERE metadata_labels_environment = 'prod';
```

### 2. Resource Validation

```sql
-- Find missing resource limits
SELECT 
    metadata_name as deployment,
    c.name as container
FROM root
JOIN spec_template_spec_containers c ON true
WHERE c.resources_limits_cpu IS NULL
   OR c.resources_limits_memory IS NULL;
```

### 3. Security Checks

```sql
-- Find privileged containers
SELECT 
    metadata_name as pod,
    c.name as container
FROM root
JOIN spec_template_spec_containers c ON true
WHERE c.securityContext_privileged = true;
```

## Troubleshooting

### 1. Missing Tables
- Check if resource exists in YAML
- Verify resource structure
- Look for empty sections

### 2. Label Queries
- Use correct label path
- Check for nested labels
- Handle label arrays properly

### 3. Resource Values
- Convert units appropriately
- Handle null/missing values
- Use proper type casting

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Docker Compose Guide](docker-compose.md)
- [Complex YAML Guide](complex-yaml.md)
- [SQL Query Command](../commands/sql.md) 