# YamlQL Class

The `YamlQL` class is the main entry point for using YamlQL as a library. It handles loading YAML files, transforming them into a relational schema, and executing queries.

## Basic Usage

```python
from yamlql_library import YamlQL

# Initialize with a YAML file
yql = YamlQL(file_path='config.yml')

# Run a query
results = yql.query("SELECT * FROM services")

# Close when done
yql.close()
```

## Constructor

### `YamlQL(file_path: str)`

Creates a new YamlQL instance for querying a YAML file.

Parameters:
- `file_path` (str): Path to the YAML file to query

Example:
```python
yql = YamlQL(file_path='docker-compose.yml')
```

## Methods

### `query(sql_query: str) -> pd.DataFrame`

Executes a SQL query against the loaded YAML data.

Parameters:
- `sql_query` (str): The SQL query to execute

Returns:
- `pd.DataFrame`: Query results as a pandas DataFrame

Example:
```python
# Simple query
results = yql.query("SELECT * FROM services")

# Complex query with joins
results = yql.query("""
    SELECT 
        s.name,
        c.image,
        c.ports
    FROM services s
    JOIN containers c ON c.service_id = s._id
""")
```

### `close()`

Closes the database connection and frees resources.

Example:
```python
yql.close()
```

### `list_tables() -> List[str]`

Lists all available tables in the schema.

Returns:
- `List[str]`: List of table names

Example:
```python
tables = yql.list_tables()
print("Available tables:", tables)
```

## Properties

### `tables: List[Tuple[str, pd.DataFrame]]`

Gets the list of tables and their corresponding DataFrames.

Returns:
- `List[Tuple[str, pd.DataFrame]]`: List of (table_name, data) tuples

Example:
```python
for table_name, df in yql.tables:
    print(f"Table {table_name}:")
    print(df.head())
```

### `db: Database`

Gets the underlying Database instance.

Returns:
- `Database`: The DuckDB database instance

Example:
```python
# Direct database access
yql.db.con.execute("CREATE VIEW service_summary AS SELECT ...")
```

## Context Manager Support

The YamlQL class supports the context manager protocol:

```python
with YamlQL(file_path='config.yml') as yql:
    results = yql.query("SELECT * FROM services")
    # Connection automatically closed after with block
```

## Error Handling

### Common Exceptions

1. **FileNotFoundError**
   ```python
   try:
       yql = YamlQL(file_path='missing.yml')
   except FileNotFoundError as e:
       print(f"File not found: {e}")
   ```

2. **SQL Errors**
   ```python
   try:
       results = yql.query("SELECT * FROM nonexistent_table")
   except Exception as e:
       print(f"Query error: {e}")
   ```

3. **Resource Management**
   ```python
   try:
       yql = YamlQL(file_path='config.yml')
       results = yql.query("SELECT * FROM services")
   finally:
       yql.close()  # Always close the connection
   ```

## Best Practices

### 1. Resource Management

Always close connections:
```python
# Using context manager (recommended)
with YamlQL('config.yml') as yql:
    results = yql.query("SELECT * FROM services")

# Or manually with try-finally
try:
    yql = YamlQL('config.yml')
    results = yql.query("SELECT * FROM services")
finally:
    yql.close()
```

### 2. Query Execution

Handle large results:
```python
# Process results in chunks
results = yql.query("SELECT * FROM large_table")
for chunk in results.groupby(results.index // 1000):
    process_chunk(chunk)
```

### 3. Table Discovery

Check available tables:
```python
# List all tables
tables = yql.list_tables()

# Check metadata
metadata = yql.query("SELECT * FROM __tables")
```

## Examples

### 1. Basic Queries

```python
from yamlql_library import YamlQL

with YamlQL('docker-compose.yml') as yql:
    # Get service names
    services = yql.query("SELECT name FROM services")
    
    # Find specific service
    nginx = yql.query("""
        SELECT * FROM services 
        WHERE image LIKE '%nginx%'
    """)
```

### 2. Complex Queries

```python
with YamlQL('kubernetes.yml') as yql:
    # Join multiple tables
    results = yql.query("""
        WITH container_resources AS (
            SELECT 
                name,
                CAST(REPLACE(resources_limits_cpu, 'm', '') AS INTEGER) as cpu_millicores,
                CAST(REPLACE(resources_limits_memory, 'Mi', '') AS INTEGER) as memory_mb
            FROM spec_template_spec_containers
        )
        SELECT 
            name,
            cpu_millicores,
            memory_mb
        FROM container_resources
        WHERE cpu_millicores > 500
    """)
```

### 3. Metadata Queries

```python
with YamlQL('config.yml') as yql:
    # Get schema information
    tables = yql.query("""
        SELECT 
            table_name,
            parent_table,
            type,
            description
        FROM __tables
        ORDER BY type, table_name
    """)
    
    # Check relationships
    relationships = yql.query("""
        SELECT 
            source_table,
            target_table,
            relationship_type
        FROM __relationships
    """)
```

## Related Topics

- [Database Class](database.md)
- [Transformer Class](transformer.md)
- [Schema Transformation](../concepts/schema-transformation.md)
- [SQL Query Command](../commands/sql.md) 