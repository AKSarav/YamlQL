# Database Class

The `Database` class manages the DuckDB connection and table operations for YamlQL. It handles creating tables, executing queries, and managing database resources.

## Basic Usage

```python
from yamlql_library import Database

# Create database
db = Database()

# Create table
db.create_table('services', ['name', 'image'], data)

# Execute query
results = db.query("SELECT * FROM services")

# Close when done
db.close()
```

## Constructor

### `Database(temp_dir: Optional[str] = None)`

Creates a new Database instance.

Parameters:
- `temp_dir` (Optional[str]): Directory for temporary database files. If None, uses system temp directory.

Example:
```python
# Default temp directory
db = Database()

# Custom temp directory
db = Database(temp_dir='/path/to/temp')
```

## Methods

### `create_table(name: str, columns: List[str], data: pd.DataFrame) -> None`

Creates a new table in the database.

Parameters:
- `name` (str): Table name
- `columns` (List[str]): Column names
- `data` (pd.DataFrame): Table data

Example:
```python
# Create simple table
db.create_table(
    name='services',
    columns=['name', 'image'],
    data=pd.DataFrame([
        ['web', 'nginx'],
        ['db', 'postgres']
    ])
)
```

### `query(sql: str) -> pd.DataFrame`

Executes a SQL query and returns results.

Parameters:
- `sql` (str): SQL query to execute

Returns:
- `pd.DataFrame`: Query results

Example:
```python
# Simple query
results = db.query("SELECT * FROM services")

# Complex query
results = db.query("""
    SELECT s.name, COUNT(p.port) as port_count
    FROM services s
    LEFT JOIN ports p ON p.service_id = s._id
    GROUP BY s.name
""")
```

### `close() -> None`

Closes the database connection and cleans up resources.

Example:
```python
db.close()
```

### `list_tables() -> List[str]`

Gets a list of all tables in the database.

Returns:
- `List[str]`: List of table names

Example:
```python
tables = db.list_tables()
print("Available tables:", tables)
```

### `table_exists(name: str) -> bool`

Checks if a table exists.

Parameters:
- `name` (str): Table name to check

Returns:
- `bool`: True if table exists, False otherwise

Example:
```python
if db.table_exists('services'):
    print("Services table exists")
```

## Properties

### `con: duckdb.DuckDBPyConnection`

Gets the underlying DuckDB connection.

Returns:
- `duckdb.DuckDBPyConnection`: DuckDB connection object

Example:
```python
# Direct connection access
db.con.execute("CREATE INDEX idx_name ON services(name)")
```

### `temp_file: str`

Gets the path to the temporary database file.

Returns:
- `str`: Path to database file

Example:
```python
print(f"Database file: {db.temp_file}")
```

## Resource Management

### Context Manager Support

The Database class supports the context manager protocol:

```python
with Database() as db:
    db.create_table('services', columns, data)
    results = db.query("SELECT * FROM services")
    # Connection automatically closed after with block
```

### Cleanup

Resources are automatically cleaned up when:
1. `close()` is called
2. Context manager exits
3. Object is garbage collected

```python
# Manual cleanup
try:
    db = Database()
    # ... use database
finally:
    db.close()
```

## Best Practices

### 1. Connection Management

Always close connections:
```python
# Using context manager (recommended)
with Database() as db:
    results = db.query("SELECT * FROM services")

# Or manually with try-finally
try:
    db = Database()
    results = db.query("SELECT * FROM services")
finally:
    db.close()
```

### 2. Query Performance

Optimize queries:
```python
# Create indexes for frequently queried columns
db.con.execute("""
    CREATE INDEX idx_service_name 
    ON services(name)
""")

# Use prepared statements for repeated queries
stmt = db.con.prepare("""
    SELECT * FROM services 
    WHERE name = ?
""")
results = stmt.execute(['web'])
```

### 3. Memory Management

Handle large datasets:
```python
# Process results in chunks
for chunk in db.query_iter("SELECT * FROM large_table"):
    process_chunk(chunk)

# Use temporary tables for intermediate results
db.con.execute("""
    CREATE TEMP TABLE tmp_results AS
    SELECT * FROM large_table
    WHERE size > 1000
""")
```

## Examples

### 1. Basic Operations

```python
from yamlql_library import Database
import pandas as pd

with Database() as db:
    # Create table
    db.create_table(
        'services',
        ['name', 'image'],
        pd.DataFrame([
            ['web', 'nginx'],
            ['db', 'postgres']
        ])
    )
    
    # Query data
    services = db.query("SELECT * FROM services")
    print(services)
```

### 2. Complex Queries

```python
with Database() as db:
    # Create multiple tables
    db.create_table('services', ['name', 'image'], services_data)
    db.create_table('ports', ['service_id', 'port'], ports_data)
    
    # Join tables
    results = db.query("""
        WITH service_ports AS (
            SELECT 
                s.name,
                COUNT(p.port) as port_count,
                STRING_AGG(p.port::VARCHAR, ',') as ports
            FROM services s
            LEFT JOIN ports p ON p.service_id = s._id
            GROUP BY s.name
        )
        SELECT * FROM service_ports
        WHERE port_count > 0
    """)
```

### 3. Schema Management

```python
with Database() as db:
    # Check table existence
    if not db.table_exists('services'):
        db.create_table('services', columns, data)
    
    # Get schema information
    schema = db.query("""
        SELECT 
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name = 'services'
    """)
```

## Error Handling

### Common Exceptions

1. **ConnectionError**
   ```python
   try:
       db = Database(temp_dir='/invalid/path')
   except ConnectionError as e:
       print(f"Failed to create database: {e}")
   ```

2. **SQLError**
   ```python
   try:
       results = db.query("SELECT * FROM nonexistent_table")
   except Exception as e:
       print(f"Query error: {e}")
   ```

3. **ResourceError**
   ```python
   try:
       db.create_table('services', columns, large_data)
   except Exception as e:
       print(f"Resource error: {e}")
   ```

## Related Topics

- [YamlQL Class](yamlql.md)
- [Transformer Class](transformer.md)
- [SQL Query Command](../commands/sql.md)
- [Schema Transformation](../concepts/schema-transformation.md) 