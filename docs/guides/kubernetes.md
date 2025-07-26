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

Discover the schema:
```bash
yamlql discover -f deployment.yml
```

Typical tables created:
- `metadata` - Deployment metadata (name, namespace, labels)
- `spec` - Deployment specification (replicas, selector)
- `spec_template_spec_containers` - Container definitions with resources
- `spec_template_spec_containers_ports` - Container port configurations

Common Queries:
```sql
-- Get deployment metadata
SELECT name, namespace 
FROM metadata;

-- Get replica count
SELECT replicas 
FROM spec;

-- Get container resource limits
SELECT 
    name,
    image,
    resources_limits_cpu,
    resources_limits_memory
FROM spec_template_spec_containers;

-- Find containers by image
SELECT name, image 
FROM spec_template_spec_containers 
WHERE image LIKE '%nginx%';
```

### 2. Services

```yaml
# service.yml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: default
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
-- Get service metadata
SELECT name, namespace
FROM metadata;

-- Get service type and selector
SELECT type, selector_app
FROM spec;

-- List service ports (if stored as separate table)
SELECT port, targetPort
FROM spec_ports;

-- Find services by type
SELECT name 
FROM metadata m
JOIN spec s ON true
WHERE s.type = 'ClusterIP';
```

### 3. ConfigMaps

```yaml
# configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  database_url: postgresql://localhost:5432/myapp
  redis_url: redis://localhost:6379
  feature_flags: |
    debug=true
    logging=verbose
```

Common Queries:
```sql
-- Get ConfigMap metadata
SELECT name, namespace
FROM metadata;

-- Access configuration data
SELECT database_url, redis_url, feature_flags
FROM data;

-- Find ConfigMaps with specific settings
SELECT name
FROM metadata m
JOIN data d ON true
WHERE d.database_url LIKE '%postgresql%';
```

## Advanced Queries

### 1. Resource Analysis

```sql
-- Find containers without resource limits
SELECT name, image
FROM spec_template_spec_containers 
WHERE resources_limits_cpu IS NULL 
   OR resources_limits_memory IS NULL;

-- Compare requests vs limits
SELECT 
    name,
    resources_requests_cpu,
    resources_limits_cpu,
    resources_requests_memory,
    resources_limits_memory
FROM spec_template_spec_containers
WHERE resources_limits_cpu IS NOT NULL;

-- Aggregate resource usage across containers
SELECT 
    COUNT(*) as total_containers,
    COUNT(DISTINCT image) as unique_images,
    SUM(CASE WHEN resources_limits_cpu IS NOT NULL THEN 1 ELSE 0 END) as containers_with_limits
FROM spec_template_spec_containers;
```

### 2. Multi-Resource Analysis

For multiple Kubernetes files, you can analyze patterns:

```sql
-- Find all deployments in specific namespace
SELECT name 
FROM metadata 
WHERE namespace = 'production';

-- Count replicas across all deployments
SELECT 
    m.name,
    s.replicas
FROM metadata m
JOIN spec s ON true
ORDER BY s.replicas DESC;

-- Security analysis - find containers running as root
SELECT name, image
FROM spec_template_spec_containers c
JOIN spec_template_spec s ON true
WHERE s.securityContext_runAsUser = 0 
   OR s.securityContext_runAsUser IS NULL;
```

### 3. Label and Selector Queries

```sql
-- Find resources with specific labels
SELECT name
FROM metadata
WHERE labels_app = 'nginx';

-- Match selectors to labels
SELECT 
    m.name as deployment,
    s.selector_app as selector
FROM metadata m
JOIN spec s ON true
WHERE s.selector_app IS NOT NULL;
```

## Complex Scenarios

### 1. Microservices Architecture Analysis

```yaml
# Multiple services with different configurations
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    tier: frontend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: web
        image: frontend:v1.2.0
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
---
apiVersion: apps/v1
kind: Deployment  
metadata:
  name: backend
  labels:
    tier: backend
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: api
        image: backend:v2.1.0
        resources:
          limits:
            cpu: "1000m"
            memory: "1Gi"
```

Analysis queries:
```sql
-- Service tier analysis
SELECT 
    labels_tier as tier,
    COUNT(*) as deployment_count,
    SUM(replicas) as total_replicas
FROM metadata m
JOIN spec s ON true
GROUP BY labels_tier;

-- Resource allocation by tier
SELECT 
    m.labels_tier as tier,
    c.image,
    c.resources_limits_cpu,
    c.resources_limits_memory
FROM metadata m
JOIN spec s ON true
JOIN spec_template_spec_containers c ON true
ORDER BY m.labels_tier;
```

### 2. Version and Image Analysis

```sql
-- Extract image versions
SELECT 
    name,
    image,
    REGEXP_EXTRACT(image, ':(.+)$') as version
FROM spec_template_spec_containers;

-- Find outdated images
SELECT 
    name,
    image
FROM spec_template_spec_containers
WHERE image LIKE '%:v1.%' 
   OR image LIKE '%:latest';

-- Image security analysis
SELECT 
    image,
    COUNT(*) as usage_count
FROM spec_template_spec_containers
GROUP BY image
ORDER BY usage_count DESC;
```

### 3. Port and Network Configuration

```sql
-- Find all exposed ports
SELECT 
    c.name as container,
    p.containerPort
FROM spec_template_spec_containers c
JOIN spec_template_spec_containers_ports p 
  ON c.name = p.spec_template_spec_containers_name;

-- Network policy analysis
SELECT 
    m.name,
    s.type,
    COUNT(p.port) as port_count
FROM metadata m
JOIN spec s ON true
LEFT JOIN spec_ports p ON true
GROUP BY m.name, s.type;
```

## Best Practices

### 1. Schema Discovery

Always start by understanding the structure:
```bash
yamlql discover -f k8s-manifest.yml
```

Kubernetes manifests typically create:
- `metadata` table for resource metadata
- `spec` table for specifications
- Nested tables for complex objects (containers, ports, volumes)

### 2. Joining Related Data

```sql
-- Join deployment metadata with container specs
SELECT 
    m.name as deployment,
    m.namespace,
    c.name as container,
    c.image
FROM metadata m
JOIN spec_template_spec_containers c ON true;
```

### 3. Resource Validation

```sql
-- Check for required fields
SELECT name
FROM spec_template_spec_containers
WHERE image IS NULL OR name IS NULL;

-- Validate resource specifications
SELECT name, image
FROM spec_template_spec_containers
WHERE resources_limits_memory IS NULL 
  AND image NOT LIKE '%system%';
```

### 4. Multi-File Analysis

When working with multiple files:
```bash
# Combine multiple manifests
cat *.yaml | yamlql sql "SELECT COUNT(*) as total_resources FROM metadata"
```

## Common Patterns

### 1. Health Check Analysis

```sql
-- Find containers without health checks
SELECT name, image
FROM spec_template_spec_containers c
WHERE NOT EXISTS (
    SELECT 1 FROM spec_template_spec_containers 
    WHERE livenessProbe_httpGet_path IS NOT NULL
);
```

### 2. Security Compliance

```sql
-- Find containers running privileged
SELECT name, image
FROM spec_template_spec_containers
WHERE securityContext_privileged = true;

-- Check for non-root users
SELECT 
    name,
    securityContext_runAsUser,
    securityContext_runAsNonRoot
FROM spec_template_spec_containers;
```

### 3. Resource Quotas

```sql
-- Calculate total resource requests
SELECT 
    SUM(CAST(REPLACE(resources_requests_cpu, 'm', '') AS INT)) as total_cpu_millicores,
    COUNT(*) as container_count
FROM spec_template_spec_containers
WHERE resources_requests_cpu IS NOT NULL;
```

## Troubleshooting

### 1. Missing Tables
If expected tables don't appear:
- Check YAML syntax and structure
- Verify resource definitions are complete
- Use `yamlql discover` to see actual schema

### 2. Complex Nested Objects
For deeply nested Kubernetes objects:
- Look for flattened columns with underscore separators
- Check for separate tables created for arrays
- Use table and list output formats to explore data

### 3. Multi-Document YAML
Kubernetes files with multiple resources:
- Each resource may create its own set of tables
- Use metadata to distinguish between resources
- Consider processing files separately if needed

## Related Topics

- [Schema Transformation](../concepts/schema-transformation.md)
- [Docker Compose Guide](docker-compose.md)
- [Complex YAML Guide](complex-yaml.md)
- [SQL Query Command](../commands/sql.md) 