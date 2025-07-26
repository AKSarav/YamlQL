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
   git clone https://github.com/AKSarav/YamlQL.git
   cd YamlQL
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
1. Validate YAML syntax using an online validator
2. Check indentation (must use spaces, not tabs)
3. Verify quotes and special characters are properly escaped

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
2. Check table naming conventions:
   - Root level objects become tables (e.g., `services`, `metadata`)
   - Nested objects create detailed tables (e.g., `services_web`, `services_db`)
   - Arrays create separate tables (e.g., `services_web_ports`)

#### Column Not Found
```
Error: Column 'name' does not exist
```

Solutions:
1. Check column names with discover:
   ```bash
   yamlql discover -f config.yml
   ```
2. Remember flattened naming:
   - Nested fields use underscores: `database_host`, `environment_NODE_ENV`
   - Special characters become underscores: `service-name` → `service_name`

#### Invalid SQL Syntax
```
Error: syntax error at or near "FROM"
```

Solutions:
1. Verify SQL syntax
2. Check for missing commas or quotes
3. Use proper table/column names from `yamlql discover`

### 4. Schema Understanding Issues

#### Unexpected Table Structure
```
Expected 'containers' table but got 'spec_template_spec_containers'
```

Solutions:
1. Always run `yamlql discover` first to understand actual schema
2. Remember YamlQL creates table names based on YAML structure:
   - Kubernetes: `spec_template_spec_containers` for deployment containers
   - Docker Compose: `services_web`, `services_db` for individual services
3. Use realistic examples from documentation

#### Missing Data
```
Some fields from YAML don't appear in any table
```

Solutions:
1. Check flattened columns in parent tables
2. Look for data preserved in main tables even when detail tables exist
3. YamlQL preserves all data - it may be flattened with underscore notation

### 5. Memory Issues

#### Out of Memory
```
MemoryError: Unable to allocate array with shape (1000000, 10)
```

Solutions:
1. Use file-backed database for large files
2. Limit query results:
   ```sql
   SELECT * FROM large_table LIMIT 1000
   ```
3. Process data in smaller chunks

#### Temporary File Issues
```
OSError: [Errno 28] No space left on device
```

Solutions:
1. Free up disk space
2. Clean up old temp files
3. Use different temp directory if needed

### 6. Performance Issues

#### Slow Queries
```
Query taking too long to execute
```

Solutions:
1. Use EXPLAIN to analyze query:
   ```sql
   EXPLAIN SELECT * FROM services;
   ```
2. Optimize joins by using proper table relationships
3. Limit result sets for exploration

#### Large Table Count
```
Too many tables created from complex YAML
```

Solutions:
1. This is normal for complex YAML structures
2. Use main tables for overview queries
3. Use detail tables for specific analysis
4. YamlQL's heuristics prevent excessive table creation

## Best Practices

### 1. Error Prevention

1. Always validate YAML first using online tools
2. Start with schema discovery:
   ```bash
   yamlql discover -f config.yml
   ```
3. Use realistic table and column names based on discovery output

### 2. Debugging

1. Check metadata information:
   ```sql
   -- See all available tables (may not exist in all versions)
   .tables  -- DuckDB command to list tables
   ```

2. Validate transformations by exploring table structures:
   ```bash
   yamlql sql -f config.yml "SELECT * FROM services LIMIT 5" --output list
   ```

### 3. Performance

1. Use appropriate table structures:
   - Main tables for aggregated views
   - Detail tables for specific service/component analysis
   - Array tables for list data

2. Start with simple queries and build complexity:
   ```sql
   -- Start simple
   SELECT * FROM services;
   
   -- Add complexity
   SELECT s.web_image, p.value as port 
   FROM services s 
   JOIN services_web_ports p ON true;
   ```

## Getting Help

### 1. Diagnostic Information

Gather information:
```bash
# Check YamlQL version
yamlql --version

# Check Python version
python --version

# Discover schema
yamlql discover -f your-file.yml
```

### 2. Common Checks

1. YAML validity:
   ```bash
   # Use online YAML validator or Python
   python -c "import yaml; yaml.safe_load(open('your-file.yml'))"
   ```

2. Table structure:
   ```bash
   yamlql discover -f your-file.yml
   ```

3. Sample queries:
   ```bash
   yamlql sql -f your-file.yml "SELECT * FROM services LIMIT 3"
   ```

### 3. Support Resources

1. Documentation: [YamlQL Documentation](https://yamlql.github.io)
2. GitHub Issues: [github.com/AKSarav/YamlQL/issues](https://github.com/AKSarav/YamlQL/issues)
3. Example Repository: [Test Data Examples](https://github.com/AKSarav/YamlQL/tree/main/tests/test_data)

## Common Error Messages and Solutions

### "Table does not exist"
- **Cause**: Incorrect table name
- **Solution**: Use `yamlql discover` to see actual table names

### "Column does not exist"  
- **Cause**: Incorrect column name or looking in wrong table
- **Solution**: Check flattened column names with underscore notation

### "Array index out of bounds"
- **Cause**: Accessing array element that doesn't exist
- **Solution**: Check array length with `ARRAY_LENGTH()` function

### "Type mismatch in comparison"
- **Cause**: Comparing incompatible types
- **Solution**: Use type casting: `CAST(column AS INTEGER)`

### "Syntax error near FROM"
- **Cause**: Invalid SQL syntax
- **Solution**: Check SQL syntax and table/column names

## Related Topics

- [Installation Guide](getting-started/installation.md)
- [SQL Query Command](commands/sql.md)
- [Schema Transformation](concepts/schema-transformation.md) 