# YamlQL

YamlQL is a powerful command-line tool and Python library that allows you to query YAML files using SQL. It intelligently converts YAML structures into a relational schema, loads it into an in-memory database, and lets you run SQL queries against it.

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

# Run a SQL query (new default, recommended)
yamlql -f docker-compose.yml "SELECT name, image FROM services"

# (Alternatively, you can use the explicit subcommand)
yamlql sql -f docker-compose.yml "SELECT name, image FROM services"

# Ask a question in natural language
yamlql ai -f docker-compose.yml "What services use the postgres image?"
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