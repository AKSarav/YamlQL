# Schema Transformation

YamlQL transforms YAML files into a relational database schema that can be queried using SQL. This guide explains how different YAML structures are converted into tables.

## Basic Principles

1. **Scalar Values**: Simple key-value pairs become columns
2. **Objects**: Nested objects become separate tables or flattened columns
3. **Arrays**: Lists become either separate tables or array columns
4. **Relationships**: Parent-child relationships are tracked in metadata

## Transformation Rules

### 1. Root-Level Structures

#### Dictionary Root
If the YAML root is a dictionary (the most common case), its top-level keys are treated as tables.

**Heuristic for Single Keys**: To create a more intuitive schema, if there is only one top-level key and its value is a *dictionary* (common in files like Kubernetes manifests), YamlQL will "step inside" that key and use its children as the main tables. In all other cases (e.g., a single key pointing to a list, or multiple top-level keys), the keys themselves are used to form the table names.

```yaml
# Input YAML
version: '3.8'
services:
  ...
```
This would result in tables like `services`.

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

When YamlQL encounters a nested dictionary (object), it applies one of two strategies:

1.  **Standard Flattening**: For a simple nested object, its keys are flattened into the parent table's columns with an underscore prefix.
2.  **Dictionary of Objects**: As a core principle, if a dictionary's values are **all** themselves dictionaries (a common pattern for defining a collection of named items, like in a Docker Compose `services` block), YamlQL creates a **new, separate table for each entry**. The table name is a combination of the parent and child keys (e.g., `services_postgres`).

```yaml
# Example of a Dictionary of Objects
services:
  postgres:
    image: postgres:14
    ports: ["5432:5432"]
  redis:
    image: redis:7
```
This structure will result in two tables: `services_postgres` and `services_redis`.

Two approaches based on depth:

1. **Flattened** (for simple nesting):
```sql
CREATE TABLE database (
    host VARCHAR,
    port INTEGER,
    credentials_username VARCHAR,
    credentials_password VARCHAR
);
```

2. **Separate Tables** (for complex nesting):
```sql
CREATE TABLE database (
    host VARCHAR,
    port INTEGER
);

CREATE TABLE database_credentials (
    _id VARCHAR,  -- Reference to parent
    username VARCHAR,
    password VARCHAR
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

If a list contains only simple scalar values (strings, numbers, booleans), it will be loaded as a native DuckDB `LIST` type. To ensure type safety and prevent errors from mixed-type lists (e.g., `[True, 'A', 123]`), **all elements are automatically converted to strings (VARCHAR)**.

This creates a column of type `VARCHAR[]` (a list of strings). For a top-level list like the `tags` example, it creates a single-column table:
```sql
CREATE TABLE tags (
    value VARCHAR[]
);
```
For a list inside an object, it becomes a `VARCHAR[]` column in that object's table. You can then use DuckDB's powerful array functions on it.

However, if a list of scalars is found under a key that is part of a larger object structure being flattened, a new table is created instead. For a key `rds-mysql` inside an `amazon-rds` object, this creates a new table `amazon_rds_rds_mysql`.

### 4. Arrays of Objects

```yaml
# Input YAML
services:
  - name: web
    port: 80
    env:
      - key: NODE_ENV
        value: production
  - name: api
    port: 3000
    env:
      - key: DEBUG
        value: true
```

Becomes multiple related tables:
```sql
CREATE TABLE services (
    _id VARCHAR,
    name VARCHAR,
    port INTEGER
);

CREATE TABLE services_env (
    service_id VARCHAR,  -- References services._id
    key VARCHAR,
    value VARCHAR
);
```

### 5. Mixed Content

```yaml
# Input YAML
spec:
  replicas: 3
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        - containerPort: 80
  volumes:
    data: /var/lib/data
```

Becomes:
```sql
CREATE TABLE spec (
    replicas INTEGER,
    volumes_data VARCHAR
);

CREATE TABLE spec_containers (
    _id VARCHAR,
    name VARCHAR,
    image VARCHAR
);

CREATE TABLE spec_containers_ports (
    container_id VARCHAR,  -- References spec_containers._id
    containerPort INTEGER
);
```

## Special Cases

### 1. Environment Variables

```yaml
environment:
  NODE_ENV: production
  DEBUG: "true"
  PORT: "3000"
```

Becomes:
```sql
CREATE TABLE environment (
    key VARCHAR,
    value VARCHAR
);
```

### 2. Port Mappings

```yaml
ports:
  - "3000:80"
  - "8080"
```

Becomes:
```sql
CREATE TABLE ports (
    value VARCHAR,  -- Keeps original format
    host_port INTEGER,  -- Parsed value
    container_port INTEGER  -- Parsed value
);
```

### 3. Volume Mounts

```yaml
volumes:
  - ./data:/var/lib/data:ro
  - /tmp:/tmp
```

Becomes:
```sql
CREATE TABLE volumes (
    value VARCHAR,  -- Original string
    source VARCHAR,  -- Parsed source path
    target VARCHAR,  -- Parsed target path
    mode VARCHAR    -- Parsed mode (if any)
);
```

## Naming Conventions

1. **Table Names**:
   - Root level: `root`
   - Top-level objects: Object name (e.g., `services`)
   - Nested objects: Parent_Child (e.g., `spec_containers`)

2. **Column Names**:
   - Simple fields: Field name (e.g., `name`)
   - Nested fields: Parent_Child (e.g., `resources_limits_cpu`)
   - **Special Character Sanitization**: Any characters that are not valid in unquoted SQL identifiers (like spaces, periods, and hyphens) are replaced with underscores. For example, a YAML key `service-name` becomes the column `service_name`.
   - Case is preserved.

3. **Special Columns**:
   - `_id`: Primary key for child tables
   - `parent_id`: Reference to parent table
   - `value`: For simple array items

## Metadata Generation

### 1. Table Information

```sql
CREATE TABLE __tables (
    table_name VARCHAR,
    parent_table VARCHAR,
    type VARCHAR,  -- 'root', 'section', 'child'
    description VARCHAR
);
```

### 2. Relationships

```sql
CREATE TABLE __relationships (
    source_table VARCHAR,
    target_table VARCHAR,
    relationship_type VARCHAR  -- 'parent-child', 'reference'
);
```

## Best Practices

### 1. Structure Your YAML

Good:
```yaml
service:
  name: api
  config:
    port: 3000
    env: production
```

Avoid:
```yaml
service-name: api
service-config-port: 3000
service-config-env: production
```

### 2. Use Consistent Types

Good:
```yaml
port: 3000  # Number
debug: true  # Boolean
name: "api"  # String
```

Avoid:
```yaml
port: "3000"  # String that should be number
debug: "true"  # String that should be boolean
```

### 3. Array Handling

Good:
```yaml
ports:
  - containerPort: 80
    hostPort: 8080
```

Avoid:
```yaml
ports: "80:8080, 443:8443"  # String that should be structured
```

## Common Issues

### 1. Type Inference

YamlQL tries to infer types:
- Numbers → INTEGER/FLOAT
- true/false → BOOLEAN
- Everything else → VARCHAR

### 2. Array Flattening

Arrays are handled based on content:
- Scalar arrays → Single table with `value` column
- Object arrays → Separate tables with relationships
- Mixed arrays → Preserved as JSON strings

### 3. Name Collisions

Column names from nested structures:
- Use parent prefix to avoid collisions
- Special characters replaced with underscore
- Case sensitivity preserved

## Related Topics

- [Metadata Tables](metadata-tables.md)
- [Relationships](relationships.md)
- [SQL Query Command](../commands/sql.md)
- [Complex YAML Guide](../guides/complex-yaml.md) 