# Schema Transformation

YamlQL transforms YAML files into a relational database schema that can be queried using SQL. This guide explains how different YAML structures are converted into tables.

## Basic Principles

1. **Scalar Values**: Simple key-value pairs become columns
2. **Objects**: Nested objects become separate tables or flattened columns based on intelligent heuristics
3. **Arrays**: Lists become either separate tables (for objects) or array columns (for scalars)
4. **Data Preservation**: Every field from your original YAML is preserved somewhere

## Transformation Rules

### 1. Root-Level Structures

#### Dictionary Root
If the YAML root is a dictionary (the most common case), YamlQL analyzes the structure to create an optimal schema.

**Single-Key Unwrapping**: If there is only one top-level key and its value is a *dictionary* (common in files like Kubernetes manifests), YamlQL will "step inside" that key and use its children as the main tables, creating a more intuitive schema.

```yaml
# Input YAML
version: '3.8'
services:
  web:
    image: nginx:latest
  db:
    image: postgres:14
```

This creates tables like:
- `services` (with flattened columns: `web_image`, `db_image`)
- `services_web` (detailed web service configuration)
- `services_db` (detailed db service configuration)

#### List Root
If the YAML root is a list of objects, it is treated as a single table named `root`.
```yaml
# Input YAML
- name: service-a
  image: nginx
- name: service-b
  image: apache
```
This creates a `root` table with columns `name` and `image`.

### 2. Nested Objects

YamlQL uses intelligent heuristics to decide how to handle nested dictionaries:

1. **Depth Limits**: To prevent over-granular tables, recursion stops at a maximum depth (currently 5 levels)
2. **Size Thresholds**: Small dictionaries (fewer than 2 key-value pairs) are more likely to be flattened
3. **Data Preservation**: Even when creating separate tables, scalar data is always flattened into parent tables to ensure no data loss

#### Example: Docker Compose Services

```yaml
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

Results in:
1. **Main `services` table** with flattened data:
   ```sql
   CREATE TABLE services (
       web_image VARCHAR,
       web_ports VARCHAR[],
       db_image VARCHAR,
       db_environment_POSTGRES_DB VARCHAR
   );
   ```

2. **Detail tables** for each service:
   ```sql
   CREATE TABLE services_web (
       image VARCHAR
   );
   
   CREATE TABLE services_db (
       image VARCHAR,
       environment_POSTGRES_DB VARCHAR
   );
   ```

3. **Array tables** for lists:
   ```sql
   CREATE TABLE services_web_ports (
       value VARCHAR
   );
   ```

### 3. Arrays of Scalars

```yaml
# Input YAML
tags:
  - production
  - backend
  - v1
```

Lists of scalar values (strings, numbers, booleans) are stored as native DuckDB `LIST` type. **All elements are automatically converted to strings** for type safety.

This creates:
```sql
CREATE TABLE tags (
    value VARCHAR[]  -- ['production', 'backend', 'v1']
);
```

### 4. Arrays of Objects

```yaml
# Input YAML
containers:
  - name: web
    image: nginx
  - name: db
    image: postgres
```

Lists of objects become separate tables with proper normalization:
```sql
CREATE TABLE containers (
    name VARCHAR,
    image VARCHAR
);
```

## Advanced Examples

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
  labels:
    app: nginx
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

Results in tables:
- `metadata` - deployment metadata
- `spec` - deployment specification
- `spec_template_spec_containers` - container configurations
- `spec_template_spec_containers_ports` - port configurations

### Complex Configuration

```yaml
application:
  name: user-service
  database:
    primary:
      host: db1.example.com
      port: 5432
    replica:
      host: db2.example.com
      port: 5432
  features:
    - name: login
      enabled: true
    - name: signup
      enabled: false
```

Results in tables:
- `application` - with flattened database configs
- `application_features` - feature configurations

## Heuristics and Decision Making

### When to Create Separate Tables

YamlQL creates separate tables when:
1. **Dictionary of Objects**: All values in a dictionary are themselves dictionaries (like Docker Compose services)
2. **Sufficient Size**: Nested dictionaries have 2 or more key-value pairs
3. **Depth Allowance**: Current nesting depth is below the maximum limit (5 levels)
4. **Arrays of Objects**: Lists contain dictionary objects rather than scalars

### When to Flatten

YamlQL flattens data when:
1. **Small Objects**: Nested dictionaries have fewer than 2 key-value pairs
2. **Deep Nesting**: Maximum depth limit is reached
3. **Scalar Preservation**: To ensure no data is lost, scalar values are always flattened to parent tables even when separate tables are created

### Column Naming

- Nested fields use underscores: `database_host`, `database_port`
- Special characters are sanitized: `service-name` becomes `service_name`
- Array table references include context: `services_web_ports`

## Data Type Handling

### Scalars
- Strings remain VARCHAR
- Numbers become appropriate numeric types (BIGINT, DOUBLE)
- Booleans become BOOLEAN
- Null values are preserved

### Arrays
- **Scalar arrays**: Converted to DuckDB LIST<VARCHAR> (all elements as strings)
- **Object arrays**: Become separate normalized tables
- **Mixed arrays**: All elements converted to strings for consistency

### Complex Values
- **Nested objects**: Flattened with underscore notation or separate tables
- **Mixed types**: Handled gracefully with string conversion when needed

## Best Practices

### 1. Understanding Your Schema

Always start with schema discovery:
```bash
yamlql discover -f your-file.yml
```

This shows you:
- What tables were created
- How your data was transformed
- Column names and types

### 2. Working with Flattened Data

```sql
-- Access flattened nested values
SELECT database_primary_host, database_replica_host 
FROM application;
```

### 3. Querying Separate Tables

```sql
-- Query detail tables for complete information
SELECT * FROM services_web;
SELECT * FROM services_db;
```

### 4. Array Handling

```sql
-- Unnest scalar arrays
SELECT UNNEST(tags.value) as tag 
FROM tags;

-- Query object arrays
SELECT name, enabled 
FROM application_features;
```

## Limitations and Considerations

### 1. Depth Limits
Very deeply nested structures (>5 levels) will be flattened rather than creating more tables.

### 2. Large Objects
Extremely large dictionaries may create many columns in flattened tables.

### 3. Dynamic Structures
YAML with highly variable structures may result in sparse tables with many null values.

### 4. Type Consistency
Mixed-type arrays are converted to strings, which may require type casting in queries.

## Related Topics

- [SQL Query Command](../commands/sql.md)
- [Docker Compose Guide](../guides/docker-compose.md)
- [Kubernetes Guide](../guides/kubernetes.md) 