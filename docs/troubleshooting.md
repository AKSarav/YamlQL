# Troubleshooting Guide

This guide helps you diagnose and fix common issues when using YamlQL.

## Common Issues

### 1. Installation Problems

#### Package Not Found
```
ERROR: Could not find a version that satisfies the requirement yamlql
```

Solutions:
1. Check Python version (requires 3.8+)
2. Update pip: `pip install --upgrade pip`
3. Install from source:
   ```bash
   git clone https://github.com/yamlql/yamlql.git
   cd yamlql
   pip install -e .
   ```

#### DuckDB Installation Failed
```
ERROR: Failed building wheel for duckdb
```

Solutions:
1. Install build dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install build-essential python3-dev

   # macOS
   xcode-select --install
   ```
2. Try binary wheel:
   ```bash
   pip install --only-binary :all: duckdb
   ```

### 2. YAML Loading Issues

#### Invalid YAML Syntax
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

Solutions:
1. Validate YAML syntax:
   ```bash
   yamlql validate -f config.yml
   ```
2. Check indentation (must use spaces, not tabs)
3. Use online YAML validator

#### File Not Found
```
FileNotFoundError: [Errno 2] No such file or directory: 'config.yml'
```

Solutions:
1. Check file path is correct
2. Use absolute path if needed
3. Verify file permissions

### 3. Query Problems

#### Table Not Found
```
Error: Table 'services' does not exist
```

Solutions:
1. List available tables:
   ```bash
   yamlql discover -f config.yml
   ```
2. Check table naming:
   - Root level: `root`
   - Nested objects: `parent_child`
   - Arrays: `parent_items`

#### Column Not Found
```
Error: Column 'name' does not exist
```

Solutions:
1. Check column names:
   ```sql
   SELECT * FROM __tables;
   ```
2. Use correct path for nested fields:
   - Nested object: `object_field`
   - Multiple levels: `object_nested_field`

#### Invalid SQL Syntax
```
Error: syntax error at or near "FROM"
```

Solutions:
1. Verify SQL syntax
2. Check for missing commas or quotes
3. Use proper table/column names

### 4. Memory Issues

#### Out of Memory
```
MemoryError: Unable to allocate array with shape (1000000, 10)
```

Solutions:
1. Process data in chunks:
   ```python
   for chunk in db.query_iter("SELECT * FROM large_table"):
       process_chunk(chunk)
   ```
2. Use file-backed database:
   ```python
   db = Database(temp_dir='/path/to/disk')
   ```
3. Limit query results:
   ```sql
   SELECT * FROM large_table LIMIT 1000
   ```

#### Temporary File Issues
```
OSError: [Errno 28] No space left on device
```

Solutions:
1. Free up disk space
2. Use different temp directory:
   ```python
   db = Database(temp_dir='/path/with/space')
   ```
3. Clean up old temp files

### 5. Performance Issues

#### Slow Queries
```
Query taking too long to execute
```

Solutions:
1. Add indexes:
   ```sql
   CREATE INDEX idx_name ON services(name);
   ```
2. Optimize joins:
   ```sql
   -- Use proper join types
   SELECT * FROM a 
   LEFT JOIN b ON b.id = a.id  -- Instead of cross join
   ```
3. Use EXPLAIN to analyze query:
   ```sql
   EXPLAIN SELECT * FROM services;
   ```

#### High Memory Usage
```
Process using too much memory
```

Solutions:
1. Use streaming queries:
   ```python
   for row in db.query_iter("SELECT * FROM large_table"):
       process_row(row)
   ```
2. Create temporary tables:
   ```sql
   CREATE TEMP TABLE results AS
   SELECT * FROM large_table
   WHERE size > 1000;
   ```
3. Limit result sets

### 6. Resource Management

#### Database Connection Issues
```
Error: Connection is closed
```

Solutions:
1. Use context manager:
   ```python
   with YamlQL('config.yml') as yql:
       results = yql.query("SELECT * FROM services")
   ```
2. Explicitly close connections:
   ```python
   try:
       yql = YamlQL('config.yml')
       results = yql.query("SELECT * FROM services")
   finally:
       yql.close()
   ```

#### Temporary File Cleanup
```
Warning: Temporary files not cleaned up
```

Solutions:
1. Use context manager (auto-cleanup)
2. Call close() explicitly
3. Set cleanup handler:
   ```python
   import atexit
   atexit.register(cleanup_function)
   ```

## Best Practices

### 1. Error Prevention

1. Always validate YAML first:
   ```bash
   yamlql validate -f config.yml
   ```

2. Check available tables:
   ```bash
   yamlql discover -f config.yml
   ```

3. Use proper resource management:
   ```python
   with YamlQL('config.yml') as yql:
       # Work with database
   ```

### 2. Debugging

1. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Check metadata tables:
   ```sql
   SELECT * FROM __tables;
   SELECT * FROM __relationships;
   ```

3. Validate transformations:
   ```python
   transformer = Transformer()
   tables = transformer.transform(yaml_data)
   for table in tables:
       print(f"{table.name}:")
       print(table.data)
   ```

### 3. Performance

1. Use appropriate indexes:
   ```sql
   CREATE INDEX idx_name ON services(name);
   ```

2. Optimize large queries:
   ```python
   # Process in chunks
   for chunk in results.groupby(results.index // 1000):
       process_chunk(chunk)
   ```

3. Clean up resources:
   ```python
   # Delete temporary tables
   db.query("DROP TABLE IF EXISTS temp_results")
   ```

## Getting Help

### 1. Diagnostic Information

Gather information:
```python
import yamlql
import sys
import duckdb

print(f"YamlQL version: {yamlql.__version__}")
print(f"Python version: {sys.version}")
print(f"DuckDB version: {duckdb.__version__}")
```

### 2. Common Checks

1. YAML validity:
   ```bash
   yamlql validate -f config.yml
   ```

2. Table structure:
   ```bash
   yamlql discover -f config.yml
   ```

3. Database state:
   ```sql
   SELECT * FROM __tables;
   ```

### 3. Support Resources

1. Documentation: [yamlql.github.io](https://yamlql.github.io)
2. GitHub Issues: [github.com/yamlql/yamlql/issues](https://github.com/AKSarav/YamlQL/issues)
3. Example Repository: [github.com/yamlql/examples](https://github.com/AKSarav/YamlQL/tree/main/tests/test_data)

## Related Topics

- [Installation Guide](getting-started/installation.md)
- [Configuration Guide](getting-started/configuration.md)
- [SQL Query Command](commands/sql.md)
- [Schema Transformation](concepts/schema-transformation.md) 