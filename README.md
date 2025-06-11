# YamlQL

Query YAML files with SQL.

## Overview

YamlQL is a command-line tool and Python library that allows you to query YAML files using SQL, powered by DuckDB. It intelligently converts YAML structures into a relational schema, loads the data into an in-memory DuckDB database, and lets you run SQL queries against it.

This is particularly useful for querying complex configuration files, data dumps, or for use in RAG (Retrieval Augmented Generation) systems where you need to precisely extract information from structured YAML content.

## Installation

```bash
pip install yamlql
```

## Usage

### CLI

#### Querying Data

To run a SQL query against a YAML file:
```bash
yamlql query --file path/to/your.yml "SELECT column_a, column_b FROM my_table"
```

#### Querying with List Output

For wide tables or complex data, the `list` output format is often more readable.
```bash
yamlql query --file path/to/your.yml "SELECT * FROM my_table" --output list
```

#### Discovering the Schema

Since the table and column names are generated automatically, you can use the `discover` command to see the schema YamlQL has created from your file. This is highly recommended before writing complex queries.
```bash
yamlql discover --file path/to/your.yml
```

### Library

```python
from yamlql_library import YamlQL

# Load a YAML file
yql = YamlQL(file_path='config.yaml')

# Run a query
results = yql.query("SELECT * FROM root")
print(results)
```

## How YamlQL Works

YamlQL transforms YAML files into a queryable, relational database on the fly. It follows a set of rules to create an intuitive schema from your YAML structure.

1.  **Table Discovery**:
    *   If your YAML file has a single root key (e.g., a `system:` key that contains everything else), YamlQL intelligently uses the keys *inside* that root object as your main tables (`application`, `services`, etc.).
    *   Otherwise, it treats each top-level key in the YAML file as a potential table.

2.  **Transformation Rules**:
    *   **Dictionaries / Objects**: A YAML object will be flattened into a single-row table. Nested keys are combined with an underscore (`_`). For example, `owner.contact.email` becomes a column named `owner_contact_email`.
    *   **Lists of Objects**: A list of objects (e.g., a list of `users`) becomes a standard, multi-row table.
    *   **Deeply Nested Lists of Objects**: When a list of objects is found nested inside another object (e.g., a list of `containers` inside a `spec`), YamlQL automatically extracts it into its own separate table (e.g., `spec_template_spec_containers`). It also copies parent fields into this new table to allow for `JOIN` operations.
    *   **Lists of Simple Values**: A list of simple values (e.g., strings or numbers) is converted into a single-column table.

3.  **Sanitization**: All generated column names are sanitized to be SQL-friendly. Special characters like spaces or periods in YAML keys are replaced with underscores.

4.  **Discovery**: Because the transformation is complex, the `discover` command is provided to inspect the final schema. It lists all the tables YamlQL has created from your file, along with all of their columns and data types, removing any guesswork.

## Development Journey & Challenges

Building YamlQL was an iterative process that involved solving several real-world challenges. This journey significantly hardened the tool and improved its usability.

*   **Initial Scaffolding**: We began with a clear project structure using modern Python tooling (`uv` and `pyproject.toml`). However, we immediately faced challenges with packaging and making the CLI script runnable, which required moving the `cli.py` file into the library and refining the `pyproject.toml` configuration multiple times.

*   **Evolving the CLI**: The command-line interface, built with `Typer`, went through several refactors. Initial designs using a default command with callbacks proved confusing for the argument parser, leading to a much simpler and more robust final design with two distinct commands: `query` and `discover`.

*   **The Data Transformer's Evolution**: The core of the project, the `DataTransformer`, became progressively smarter with each challenge:
    1.  **Initial Logic**: Could only handle simple, top-level lists of objects.
    2.  **Handling Nested Data**: The first major improvement was to flatten nested objects, but this led to the `address.city` vs. `address_city` problem, which we solved by standardizing on underscore separators.
    3.  **True Relational Tables**: The most significant challenge was handling deeply nested lists (like in the `complex_sample.yml`). Our first attempt failed, as it simply embedded the list into a single cell. The solution was to completely re-architect the transformer to automatically extract these nested lists into their own relational tables with foreign keys, enabling powerful `JOIN` queries. This required several bug fixes, including handling conflicting metadata names.
    4.  **Intuitive Table Creation**: When presented with YAML files having a single root object (like Kubernetes files or `deep_nested.yml`), the tool initially created one giant, unusable table. We improved the logic to "step inside" this single root object and treat its children as the primary tables, which is far more intuitive.
    5.  **Robustness and Edge Cases**: The final stage of development focused on hardening. We tested against various `null` formats, YAML anchors, lists of simple values, and keys with special characters. This forced us to improve the transformer logic one last time to sanitize column names and correctly handle these varied inputs, making the tool much more resilient for real-world use.

*   **Improving Usability**: Key features were added as a direct result of encountering problems. The `discover` command was created specifically because the powerful transformation logic could lead to non-obvious table and column names. Similarly, the `--output list` format was added to make viewing wide or complex query results much easier. 