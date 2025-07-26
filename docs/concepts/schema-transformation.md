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

## Table Creation Heuristics

YamlQL uses two key configuration parameters to control table creation:

### MAX_DEPTH = 5

**Purpose**: Prevents excessive table creation in deeply nested YAML structures.

**How it works**: 
- YamlQL tracks nesting depth as it processes your YAML
- Once depth reaches 5 levels, it stops creating separate tables and flattens everything into the current table
- This prevents scenarios where deeply nested YAML creates hundreds of tiny tables

**Example**:
```yaml
# This would create tables at depths 0, 1, 2, 3, 4
level1:                    # depth 0 - creates 'level1' table
  level2:                  # depth 1 - creates 'level1_level2' table  
    level3:                # depth 2 - creates 'level1_level2_level3' table
      level4:              # depth 3 - creates 'level1_level2_level3_level4' table
        level5:            # depth 4 - creates 'level1_level2_level3_level4_level5' table
          level6:          # depth 5 - STOPS HERE, flattens into parent table
            value: "deep"  # becomes 'level6_value' column in level5 table
```

**Practical Impact**:
- ✅ **Kubernetes manifests**: Rarely exceed 5 levels, so all important structures get tables
- ✅ **Docker Compose**: Typically 2-3 levels deep, fully supported
- ✅ **Complex configs**: Prevents runaway table creation from overly nested data

### MIN_DICT_SIZE_FOR_TABLE = 2

**Purpose**: Only creates separate tables for dictionaries that have enough content to justify it.

**How it works**:
- Before creating a separate table for a nested dictionary, YamlQL counts its key-value pairs
- If the dictionary has fewer than 2 keys, it's flattened into the parent table instead
- If it has 2 or more keys, it gets its own table (unless depth limit is reached)

**Example**:
```yaml
# Dictionary with 1 key - gets flattened
service:
  config:
    port: 8080                    # Only 1 key, flattens to 'config_port' column

# Dictionary with 2+ keys - gets separate table  
service:
  database:
    host: localhost               # 2+ keys, creates 'service_database' table
    port: 5432
    name: myapp
```

**Before/After Comparison**:

**Input YAML**:
```yaml
services:
  web:
    image: nginx:latest
    config:                     # 1 key - will flatten
      port: 80
    resources:                  # 2 keys - will create table
      cpu: "100m"
      memory: "128Mi"
```

**Tables Created**:
```sql
-- Main services table (includes flattened single-key data)
CREATE TABLE services (
    web_image VARCHAR,          -- Direct field
    web_config_port BIGINT,     -- Flattened from config (1 key)
    web_resources_cpu VARCHAR,  -- Also flattened for data preservation
    web_resources_memory VARCHAR
);

-- Separate table for multi-key dictionary
CREATE TABLE services_web_resources (
    cpu VARCHAR,
    memory VARCHAR
);
```

## Heuristics in Practice

### Example 1: Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:                        # depth 0, 3 keys → separate table
  name: nginx
  namespace: default
  labels:                        # depth 1, 1 key → flattened
    app: nginx
spec:                            # depth 0, 3 keys → separate table  
  replicas: 3
  selector:                      # depth 1, 1 key → flattened
    matchLabels:                 # depth 2, 1 key → flattened
      app: nginx
  template:                      # depth 1, 2 keys → separate table
    metadata:                    # depth 2, 1 key → flattened
      labels:                    # depth 3, 1 key → flattened
        app: nginx
    spec:                        # depth 2, 1 key → flattened (but contains containers)
      containers:                # depth 3, array → separate table
      - name: nginx
        image: nginx:1.14.2
```

**Resulting Tables**:
- `metadata` - deployment metadata 
- `spec` - deployment spec with flattened selector
- `spec_template_spec_containers` - container array becomes table

### Example 2: Docker Compose with Deep Nesting

```yaml
services:
  web:                          # depth 0 → creates services_web table
    image: nginx
    environment:                # depth 1, many keys → separate table  
      NODE_ENV: production
      DEBUG: false
      LOG_LEVEL: info
    volumes:                    # depth 1, array → separate table
      - "./app:/app"
    networks:                   # depth 1, 1 key → flattened
      default:
        aliases: ["web"]
```

**Tables Created**:
- `services` - main table with flattened data
- `services_web` - web service details
- `services_web_environment` - environment variables (3+ keys)
- `services_web_volumes` - volume mounts (array)
- Networks data flattened into `services_web` as `networks_default_aliases`

### Example 3: Configuration with Deep Nesting

```yaml
application:
  database:                     # depth 1, 4 keys → separate table
    primary:                    # depth 2, 3 keys → separate table  
      host: db1.example.com
      port: 5432
      ssl: true
    replica:                    # depth 2, 2 keys → separate table
      host: db2.example.com  
      port: 5432
    connection:                 # depth 2, 1 key → flattened
      timeout: 30
  cache:                        # depth 1, 1 key → flattened
    redis:                      # depth 2, 2 keys → would create table, but flattens due to parent
      host: cache.example.com
      port: 6379
```

**Tables Created**:
- `application` - main table with flattened cache and connection data
- `application_database` - database configuration
- `application_database_primary` - primary database details  
- `application_database_replica` - replica database details

## Tuning the Heuristics

### When MAX_DEPTH = 5 Might Be Too Low

If you have legitimate deeply nested structures that you want as separate tables:

```yaml
# Very deep but logical structure
organization:
  departments:
    engineering:
      teams:
        backend:
          services:
            api:              # This is at depth 5
              config:         # This gets flattened due to depth limit
                port: 8080
```

**Workaround**: Restructure your YAML to be less deeply nested, or accept that the deepest levels will be flattened.

### When MIN_DICT_SIZE_FOR_TABLE = 2 Might Be Too Low

If you want even single-key dictionaries to become tables:

```yaml
service:
  config:          # Only 1 key, but you want it as a separate table
    port: 8080
```

**Current Behavior**: Creates `service_config_port` column
**Alternative**: YamlQL prioritizes practical table structures over perfect hierarchical representation

## Data Preservation Guarantee

**Key Promise**: Regardless of these heuristics, YamlQL preserves ALL your data.

Even when a nested dictionary gets its own table due to the heuristics, its scalar fields are ALSO flattened into the parent table:

```yaml
services:
  web:
    database:                   # 2 keys → gets separate table
      host: localhost
      port: 5432
```

**Results in BOTH**:
1. `services` table with columns: `web_database_host`, `web_database_port`
2. `services_web_database` table with columns: `host`, `port`

This ensures you can query the data either way without losing information.

## Debugging Heuristic Decisions

### Use yamlql discover

To understand how heuristics affected your YAML:

```bash
yamlql discover -f your-file.yml
```

This shows you exactly which tables were created and what got flattened.

### Check Table Patterns

Look for these patterns to understand heuristic decisions:

- **Flattened data**: Columns with underscores (e.g., `config_port`, `metadata_labels_app`)
- **Separate tables**: Tables with hierarchical names (e.g., `services_web`, `spec_template_spec_containers`)
- **Depth-limited flattening**: Very long column names indicating deep nesting was flattened

### Example Analysis

```bash
yamlql discover -f complex-k8s.yml
```

Output:
```
╭─────── metadata ───────╮
│ name: VARCHAR          │
│   labels_app: VARCHAR  │  ← Single-key 'labels' was flattened
╰────────────────────────╯

╭─── spec_template_spec_containers ───╮  ← Deep nesting created long table name
│ name: VARCHAR                       │
│   resources_limits_cpu: VARCHAR     │  ← But resources were flattened due to depth
╰─────────────────────────────────────╯
```

This tells you:
- `labels` had only 1 key, so was flattened into `metadata`
- `containers` was deep enough that `resources` got flattened instead of becoming a separate table

## Related Topics

- [SQL Query Command](../commands/sql.md)
- [Docker Compose Guide](../guides/docker-compose.md)
- [Kubernetes Guide](../guides/kubernetes.md) 