# YamlQL Documentation

YamlQL is a powerful command-line tool and Python library that allows you to query YAML files using SQL. It intelligently converts YAML structures into a relational schema, loads the data into a DuckDB database, and lets you run SQL queries against it.

## Key Features

- **SQL Querying**: Query YAML files using standard SQL syntax
- **AI-Powered**: Ask questions in natural language and get SQL-powered answers
- **Schema Discovery**: Automatically discover and understand YAML structure
- **Metadata Tables**: Built-in tables to understand relationships and structure
- **Multiple Output Formats**: Table and list views for better readability
- **Multiple LLM Providers**: Support for OpenAI and Google's Gemini

## Use Cases

- Querying Kubernetes manifests
- Analyzing Docker Compose files
- Exploring configuration files
- Understanding data dumps
- Building RAG systems
- CI/CD pipeline data extraction

## Quick Example

```bash
# Install YamlQL
pip install yamlql

# Discover the schema of a YAML file
yamlql discover -f docker-compose.yml

# Run a SQL query
yamlql sql -f docker-compose.yml "SELECT name, image FROM services"

# Ask a question in natural language
yamlql ai -f docker-compose.yml "What services use the postgres image?"
```

## Why YamlQL?

YamlQL offers several advantages over traditional YAML/JSON processing tools:

1. **SQL Power**: Leverage the full power of SQL for complex queries
2. **Relational Model**: Automatic conversion of nested structures into relational tables
3. **Intelligent Schema**: Smart handling of arrays, nested objects, and relationships
4. **AI Integration**: Natural language querying with multiple LLM providers
5. **Developer Friendly**: Both CLI and Python library interfaces

## Getting Started

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quick-start.md)
- [Configuration Guide](getting-started/configuration.md)

## Contributing

Contributions are welcome! Please feel free to submit a pull request on our [GitHub repository](https://github.com/AKSarav/YamlQL).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/AKSarav/YamlQL/blob/main/LICENSE) file for details. 