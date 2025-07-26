# YamlQL

YamlQL is a powerful command-line tool and Python library that allows you to query YAML files using SQL. It intelligently converts YAML structures into a relational schema, loads it into an in-memory database, and lets you run SQL queries against it.

## Key Features

- **SQL Querying**: Query YAML files using standard SQL syntax
- **AI-Powered**: Ask questions in natural language and get SQL-powered answers
- **Schema Discovery**: Automatically discover and understand YAML structure
- **Multiple Output Formats**: Table and list views for better readability
- **Multiple LLM Providers**: Support for OpenAI and Google's Gemini
- **Native DuckDB List/Array Support**: YAML lists of scalars (e.g., [1, 2, 3] or ['a', 'b', 'c']) are stored as DuckDB arrays with all elements converted to strings for type safety. You can use DuckDB's array functions (like UNNEST, ARRAY_LENGTH, or direct indexing) in your SQL queries.
- **Run SQL from a File**: Use the `--sql-file` option to run SQL queries from a file, making it easy to work with complex queries or avoid shell quoting issues.

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

# Run a SQL query (new default, recommended)
yamlql sql -f docker-compose.yml "SELECT web_image, db_image FROM services"
# Or, for complex queries, use a SQL file
yamlql sql -f docker-compose.yml --sql-file myquery.sql

# (Alternatively, you can use the explicit subcommand)
yamlql sql -f docker-compose.yml "SELECT web_image, db_image FROM services"

# Ask a question in natural language
yamlql ai -f docker-compose.yml "What services use the postgres image?"
```

## Global Options

### Displaying the Version

You can check the installed version of YamlQL using the `--version` or `-v` flag. This is useful for verifying your installation and ensuring you are on the latest version.

```bash
yamlql --version
# or
yamlql -v
```

## Getting Started

Check out our [Quick Start Guide](getting-started/quick-start.md) to begin using YamlQL, or dive into specific topics:

- [Installation Guide](getting-started/installation.md)
- [SQL Query Command](commands/sql.md)
- [AI Query Command](commands/ai.md)
- [Schema Discovery](commands/discover.md)

## Documentation Structure

- **Getting Started**: Installation, quick start, and configuration guides
- **Commands**: Detailed documentation for each YamlQL command
- **Concepts**: Understanding YamlQL's core concepts
- **Guides**: Practical guides for common use cases
- **API Reference**: Complete Python API documentation
- **Troubleshooting**: Common issues and solutions 