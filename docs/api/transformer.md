# Transformer Class

The `Transformer` class is responsible for converting YAML structures into relational tables. It handles the complex task of mapping nested YAML objects, arrays, and scalars into a normalized database schema.

## Basic Usage

```python
from yamlql_library import Transformer

# Create transformer
transformer = Transformer()

# Transform YAML data
yaml_data = {
    'services': {
        'web': {'image': 'nginx'},
        'db': {'image': 'postgres'}
    }
}
tables = transformer.transform(yaml_data)
```

## Constructor

### `Transformer()`

Creates a new Transformer instance.

Example:
```python
transformer = Transformer()
```

## Methods

### `transform(yaml_data: Dict) -> List[Table]`

Transforms YAML data into a list of relational tables.

Parameters:
- `yaml_data` (Dict): The parsed YAML data to transform

Returns:
- `List[Table]`: List of Table objects representing the relational schema

Example:
```python
yaml_data = yaml.safe_load(yaml_file)
tables = transformer.transform(yaml_data)
```

### `get_metadata_tables() -> List[Table]`

Gets the metadata tables (`__tables`, `__relationships`).

Returns:
- `List[Table]`: List of metadata Table objects

Example:
```python
metadata_tables = transformer.get_metadata_tables()
```

### `get_table_relationships() -> List[Relationship]`

Gets the relationships between tables.

Returns:
- `List[Relationship]`: List of table relationships

Example:
```python
relationships = transformer.get_table_relationships()
```

## Classes

### Table

Represents a relational table.

Attributes:
- `name` (str): Table name
- `columns` (List[str]): Column names
- `data` (pd.DataFrame): Table data
- `parent_table` (Optional[str]): Parent table name
- `type` (str): Table type ('root', 'section', 'child')

Example:
```python
for table in tables:
    print(f"Table: {table.name}")
    print(f"Columns: {table.columns}")
    print(f"Parent: {table.parent_table}")
```

### Relationship

Represents a relationship between tables.

Attributes:
- `source_table` (str): Source table name
- `target_table` (str): Target table name
- `type` (str): Relationship type ('parent-child', 'reference')

Example:
```python
for rel in relationships:
    print(f"{rel.source_table} -> {rel.target_table} ({rel.type})")
```

## Transformation Rules

### 1. Root Level

```python
# Input YAML
yaml_data = {
    'version': '3.8',
    'name': 'myapp'
}

# Creates
root_table = Table(
    name='root',
    columns=['version', 'name'],
    data=pd.DataFrame([['3.8', 'myapp']])
)
```

### 2. Nested Objects

```python
# Input YAML
yaml_data = {
    'database': {
        'host': 'localhost',
        'port': 5432
    }
}

# Creates
database_table = Table(
    name='database',
    columns=['host', 'port'],
    data=pd.DataFrame([['localhost', 5432]])
)
```

### 3. Arrays

```python
# Input YAML
yaml_data = {
    'services': [
        {'name': 'web', 'port': 80},
        {'name': 'api', 'port': 3000}
    ]
}

# Creates
services_table = Table(
    name='services',
    columns=['name', 'port'],
    data=pd.DataFrame([
        ['web', 80],
        ['api', 3000]
    ])
)
```

## Best Practices

### 1. Memory Management

Handle large YAML files:
```python
# Process in chunks
for chunk in transformer.transform_stream(yaml_file):
    process_chunk(chunk)
```

### 2. Custom Transformations

Extend transformation rules:
```python
class CustomTransformer(Transformer):
    def transform_special_type(self, data):
        # Custom transformation logic
        return transformed_data
```

### 3. Error Handling

Handle transformation errors:
```python
try:
    tables = transformer.transform(yaml_data)
except TransformationError as e:
    print(f"Failed to transform: {e}")
```

## Examples

### 1. Basic Transformation

```python
from yamlql_library import Transformer
import yaml

# Load YAML
with open('config.yml') as f:
    yaml_data = yaml.safe_load(f)

# Transform
transformer = Transformer()
tables = transformer.transform(yaml_data)

# Access tables
for table in tables:
    print(f"\nTable: {table.name}")
    print(table.data)
```

### 2. Complex Structures

```python
# Handle nested arrays
yaml_data = {
    'services': {
        'web': {
            'ports': [80, 443],
            'env': [
                {'key': 'DEBUG', 'value': 'true'},
                {'key': 'PORT', 'value': '80'}
            ]
        }
    }
}

transformer = Transformer()
tables = transformer.transform(yaml_data)

# Results in:
# - services_web table
# - services_web_ports table (array items)
# - services_web_env table (array of objects)
```

### 3. Metadata Usage

```python
# Transform and get metadata
transformer = Transformer()
tables = transformer.transform(yaml_data)
metadata = transformer.get_metadata_tables()

# Access metadata
tables_info = metadata[0]  # __tables
relationships = metadata[1]  # __relationships

# Print schema
for _, row in tables_info.data.iterrows():
    print(f"{row['table_name']} ({row['type']})")
    if row['parent_table']:
        print(f"  Parent: {row['parent_table']}")
```

## Error Handling

### Common Exceptions

1. **InvalidYAMLError**
   ```python
   try:
       tables = transformer.transform(invalid_yaml)
   except InvalidYAMLError as e:
       print(f"Invalid YAML structure: {e}")
   ```

2. **CircularReferenceError**
   ```python
   try:
       tables = transformer.transform(circular_yaml)
   except CircularReferenceError as e:
       print(f"Circular reference detected: {e}")
   ```

3. **TransformationError**
   ```python
   try:
       tables = transformer.transform(yaml_data)
   except TransformationError as e:
       print(f"Transformation failed: {e}")
   ```

## Related Topics

- [YamlQL Class](yamlql.md)
- [Database Class](database.md)
- [Schema Transformation](../concepts/schema-transformation.md)
- [Complex YAML Guide](../guides/complex-yaml.md) 