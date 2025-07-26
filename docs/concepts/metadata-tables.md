# Metadata Tables

> **Note**: Metadata tables (`__tables`, `__relationships`) are not currently implemented in the active version of YamlQL. This documentation is preserved for reference. For current schema discovery, use the `discover` command instead.

## Current Schema Discovery

YamlQL currently provides schema information through the `discover` command rather than metadata tables:

```bash
# Get schema information
yamlql discover -f your-file.yml
```

This command shows you:
- All available tables with their column names and types
- How YamlQL transformed your YAML structure
- What data is available for querying

## Alternative Approaches

### 1. Using the Discover Command

The `discover` command provides comprehensive schema information:

```bash
yamlql discover -f docker-compose.yml
```

Output shows:
```
╭─────── services ───────╮
│ web_image: VARCHAR     │
│   web_ports: VARCHAR[] │
│   db_image: VARCHAR    │
╰────────────────────────╯
╭───── services_web ─────╮
│ image: VARCHAR         │
╰────────────────────────╯
```

### 2. Exploring Table Structure

You can explore table contents directly:

```sql
-- See first few rows to understand structure
SELECT * FROM services LIMIT 3;

-- List output for wide tables
yamlql sql -f file.yml "SELECT * FROM services LIMIT 1" --output list
```

### 3. Understanding Naming Patterns

YamlQL follows predictable naming patterns:
- Root-level objects → table names (e.g., `services`, `metadata`)
- Nested objects → underscore-separated names (e.g., `services_web`, `spec_template_spec_containers`)
- Arrays → separate tables for their contents (e.g., `services_web_ports`)

## Table Relationships

While metadata tables don't exist, you can understand relationships through naming:

### Parent-Child Relationships

```
services              # Main table
├── services_web      # Web service details
│   └── services_web_ports  # Web service ports
└── services_db       # Database service details
    └── services_db_environment  # Database environment variables
```

### Implicit Joins

Most related tables can be joined using `ON true` since they have corresponding data:

```sql
-- Join main services with web service details
SELECT s.web_image, w.image 
FROM services s 
JOIN services_web w ON true;
```

## Future Implementation

Metadata tables may be implemented in future versions to provide:
- Programmatic schema discovery
- Table relationship information
- Schema documentation
- Query assistance

For now, use the `discover` command and direct table exploration for schema understanding.

## Related Topics

- [Discover Command](../commands/discover.md)
- [Schema Transformation](schema-transformation.md)
- [SQL Query Command](../commands/sql.md) 