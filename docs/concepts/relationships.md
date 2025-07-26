# Relationships

> **Note**: Formal relationship tracking (like `__relationships` metadata tables) is not currently implemented in YamlQL. This documentation explains how relationships work conceptually and how to work with related tables.

YamlQL creates table relationships based on YAML structure, but these are implicit rather than formally tracked. Understanding these relationships helps you write effective queries.

## How Relationships Work in YamlQL

### 1. Structural Relationships

YamlQL creates relationships through table naming conventions based on your YAML structure:

```yaml
# Input YAML
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

Creates related tables:
- `services` - Main table with flattened overview
- `services_web` - Web service details
- `services_web_ports` - Web service ports
- `services_db` - Database service details

### 2. Naming-Based Relationships

Tables are related through naming patterns:

```
services                    # Parent table
├── services_web           # Child table (web service)
│   └── services_web_ports # Grandchild table (web ports)
└── services_db            # Child table (db service)
```

### 3. Data Preservation Relationships

YamlQL ensures data is preserved in multiple places:
- **Flattened data** in parent tables (e.g., `web_image` in `services`)
- **Detailed data** in child tables (e.g., `image` in `services_web`)

## Working with Related Tables

### 1. Joining Related Tables

Most related tables can be joined using `ON true` since they represent the same logical entity:

```sql
-- Join main services with web service details
SELECT s.web_image, w.image 
FROM services s 
JOIN services_web w ON true;

-- Join Kubernetes metadata with spec
SELECT m.name, m.namespace, s.replicas
FROM metadata m
JOIN spec s ON true;
```

### 2. Parent-Child Data Access

You can access data either from flattened columns or detail tables:

```sql
-- Option 1: Use flattened data in parent table
SELECT web_image, db_image 
FROM services;

-- Option 2: Use detailed child tables
SELECT image FROM services_web
UNION ALL
SELECT image FROM services_db;
```

### 3. Array Relationships

Arrays create separate tables that relate to their parent:

```sql
-- Get ports for web service
SELECT value as port 
FROM services_web_ports;

-- Get container ports in Kubernetes
SELECT containerPort 
FROM spec_template_spec_containers_ports;
```

## Common Relationship Patterns

### 1. Docker Compose Structure

```
services                           # Main services overview
├── services_web                   # Web service configuration
│   ├── services_web_ports         # Web service ports
│   └── services_web_volumes       # Web service volumes
└── services_db                    # Database configuration
    └── services_db_environment    # Database environment variables
```

### 2. Kubernetes Structure

```
metadata                           # Resource metadata
spec                              # Resource specification
└── spec_template_spec_containers  # Container definitions
    └── spec_template_spec_containers_ports  # Container ports
```

### 3. Configuration Structure

```
application                        # Main application config
├── application_database           # Database configuration
├── application_features           # Feature flags
└── application_logging            # Logging configuration
```

## Understanding Implicit Relationships

### 1. By Table Naming

Tables starting with the same prefix are typically related:
- `services_*` tables all relate to services
- `spec_*` tables all relate to specifications
- `metadata_*` tables all relate to metadata

### 2. By Data Structure

Tables with similar data often represent different views of the same entity:
- Main table: Aggregated/flattened view
- Detail table: Complete configuration
- Array table: List items

### 3. By Query Context

Related tables often make sense to query together:

```sql
-- Service analysis across related tables
SELECT 
    s.web_image,
    COUNT(p.value) as port_count
FROM services s
LEFT JOIN services_web_ports p ON true
GROUP BY s.web_image;
```

## Best Practices for Working with Relationships

### 1. Use the Discover Command

Always start by understanding the table structure:

```bash
yamlql discover -f your-file.yml
```

This shows you all available tables and their relationships through naming.

### 2. Follow Naming Patterns

Understand the predictable patterns:
- `parent_child` for nested objects
- `parent_child_array` for arrays within objects
- Underscores separate nesting levels

### 3. Start Simple, Then Join

```sql
-- Step 1: Understand individual tables
SELECT * FROM services LIMIT 3;
SELECT * FROM services_web LIMIT 3;

-- Step 2: Join related tables
SELECT s.web_image, w.image 
FROM services s 
JOIN services_web w ON true;
```

### 4. Use Both Flattened and Detailed Data

Choose the right level of detail for your query:
- Flattened columns for quick overview queries
- Detail tables for comprehensive analysis

## Querying Strategies

### 1. Overview Queries

Use main tables for high-level analysis:

```sql
-- Service overview
SELECT web_image, db_image 
FROM services;

-- Deployment overview
SELECT name, namespace, replicas
FROM metadata m
JOIN spec s ON true;
```

### 2. Detailed Queries

Use child tables for specific analysis:

```sql
-- Detailed service configuration
SELECT * FROM services_web;
SELECT * FROM services_db;

-- Container details
SELECT name, image, resources_limits_cpu
FROM spec_template_spec_containers;
```

### 3. Cross-Table Analysis

Combine related tables for comprehensive insights:

```sql
-- Docker Compose: Services with their ports
SELECT 
    'web' as service,
    p.value as port
FROM services_web_ports p
UNION ALL
SELECT 
    'db' as service,
    'No external ports' as port
FROM services s
WHERE s.db_image IS NOT NULL;
```

## Limitations

### 1. No Formal Foreign Keys

YamlQL doesn't create formal foreign key relationships, so:
- Joins use `ON true` or logical conditions
- No referential integrity constraints
- Relationship validation is manual

### 2. No Automatic Relationship Discovery

You need to understand relationships through:
- Table naming patterns
- Schema discovery
- YAML structure knowledge

### 3. Limited Cross-Table Validation

YamlQL doesn't validate that related tables have matching data.

## Future Enhancements

Potential future improvements might include:
- Formal relationship metadata
- Foreign key constraints
- Automatic join suggestions
- Relationship visualization

For now, use naming conventions and the discover command to understand relationships.

## Related Topics

- [Schema Transformation](schema-transformation.md)
- [Discover Command](../commands/discover.md)
- [SQL Query Command](../commands/sql.md)
- [Docker Compose Guide](../guides/docker-compose.md)
- [Kubernetes Guide](../guides/kubernetes.md) 