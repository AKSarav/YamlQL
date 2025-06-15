# YamlQL

Query YAML files with SQL.

## Overview

YamlQL is a command-line tool and Python library that allows you to query YAML files using SQL, powered by DuckDB. It intelligently converts YAML structures into a relational schema, loads the data into an in-memory DuckDB database, and lets you run SQL queries against it.

This is particularly useful for querying complex configuration files, data dumps, or for use in RAG (Retrieval Augmented Generation) systems where you need to precisely extract information from structured YAML content.


## Use Cases

- Querying YAML files
- Querying Kubernetes manifests
- Querying Helm charts
- Querying Docker Compose files
- Querying configuration files
- Querying data dumps
- Querying YAML files in a CI/CD pipeline
- Understanding the schema of a YAML file
- Understanding the data in a YAML file
- Understanding the relationships between data in a YAML file
- While buiding RAG systems, you can use YamlQL to query the YAML files and get the data you need to build the RAG system.


## Installation

```bash
pip install yamlql
```

## Usage

### CLI

#### Querying Data

To run a SQL query against a YAML file:
```bash
yamlql sql --file path/to/your.yml "SELECT column_a, column_b FROM my_table"
```

#### Querying with List Output

For wide tables or complex data, the `list` output format is often more readable.
```bash
yamlql sql --file path/to/your.yml "SELECT * FROM my_table" --output list
```

#### Discovering the Schema

Since the table and column names are generated automatically, you can use the `discover` command to see the schema YamlQL has created from your file. This is highly recommended before writing complex queries.
```bash
yamlql discover --file path/to/your.yml
```

#### Answering Questions with Natural Language (AI)

You can ask questions about your YAML file in plain English. YamlQL will generate and execute a SQL query to get the answer.

> **Note:** We do not send your content to the LLM. Only the schema of the document is sent to generate the SQL query, which is then executed locally. This ensures your data remains private.

**Setup:**
This feature requires setting environment variables for your chosen LLM provider. You can set them in your shell or place them in a `.env` file in your project directory.

**1. Choose a Provider:**
Set `YAMLQL_LLM_PROVIDER` to `OpenAI`, `Gemini`, or `Ollama`.
```bash
export YAMLQL_LLM_PROVIDER="OpenAI"
```

**2. Set Provider-Specific Variables:**
Based on your choice above, set the corresponding API key or host.

*   **For OpenAI:**
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```
*   **For Gemini:**
    ```bash
    export GEMINI_API_KEY="..."
    ```
*   **For Ollama (Coming Soon):**
    The Ollama provider is not yet implemented. When it is, it will likely use an environment variable like `OLLAMA_HOST`.

**Usage:**
```bash
yamlql ai --file path/to/your.yml "What is the CPU limit for the nginx container?"
```

#### Session-Based Queries

You can also run queries directly using environment variables to set the file and mode. This is useful for repeated queries against the same file.

**Setup:**
Set the environment variables `YAMLQL_FILE` and `YAMLQL_MODE`.
```bash
export YAMLQL_FILE="path/to/your.yml"
export YAMLQL_MODE="SQL"  # or "AI"
```

**Usage:**
```bash
yamlql -e "SELECT column_a, column_b FROM my_table"
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
    *   If your YAML file has multiple root keys, each key is treated as a potential table.
    *   If a key has multiple children, a separate table is created for each child.
    *   This approach ensures that deeply nested structures are appropriately flattened into relational tables.

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

*   **Evolving the CLI**: The command-line interface, built with `Typer`, went through several refactors. Initial designs using a default command with callbacks proved confusing for the argument parser, leading to a much simpler and more robust final design with two distinct commands: `sql` and `discover`.

*   **The Data Transformer's Evolution**: The core of the project, the `DataTransformer`, became progressively smarter with each challenge:
    1.  **Initial Logic**: Could only handle simple, top-level lists of objects.
    2.  **Handling Nested Data**: The first major improvement was to flatten nested objects, but this led to the `address.city` vs. `address_city` problem, which we solved by standardizing on underscore separators.
    3.  **True Relational Tables**: The most significant challenge was handling deeply nested lists (like in the `complex_sample.yml`). Our first attempt failed, as it simply embedded the list into a single cell. The solution was to completely re-architect the transformer to automatically extract these nested lists into their own relational tables with foreign keys, enabling powerful `JOIN` queries. This required several bug fixes, including handling conflicting metadata names.
    4.  **Intuitive Table Creation**: When presented with YAML files having a single root object (like Kubernetes files or `deep_nested.yml`), the tool initially created one giant, unusable table. We improved the logic to "step inside" this single root object and treat its children as the primary tables, which is far more intuitive.
    5.  **Robustness and Edge Cases**: The final stage of development focused on hardening. We tested against various `null` formats, YAML anchors, lists of simple values, and keys with special characters. This forced us to improve the transformer logic one last time to sanitize column names and correctly handle these varied inputs, making the tool much more resilient for real-world use.

*   **Improving Usability**: Key features were added as a direct result of encountering problems. The `discover` command was created specifically because the powerful transformation logic could lead to non-obvious table and column names. Similarly, the `--output list` format was added to make viewing wide or complex query results much easier.

## Walkthrough: Examples

Here are a few examples to show how YamlQL can be used in different scenarios.

### Example 1: Basic Joins

Given a simple `data.yml` with users and posts:

```yaml
# data.yml
users:
  - id: 1
    name: John Doe
    email: john.doe@example.com
posts:
  - id: 101
    title: "First Post"
    author_id: 1
  - id: 102
    title: "Second Post"
    author_id: 1
```

YamlQL creates two tables: `users` and `posts`. You can easily run a `JOIN` query to find all posts by a specific user:

```bash
yamlql sql --file data.yml "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.author_id"
```
*This query will return the name "John Doe" with "First Post" and "Second Post".*

### Example 2: Querying a Kubernetes Manifest

Kubernetes manifests are deeply nested and a perfect use case. Given a `deployment.yml`:

```yaml
# deployment.yml (simplified)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        resources:
          limits:
            cpu: "200m"
```

The transformation logic is powerful, but can create non-obvious table names. **First, always use `discover`:**

```bash
yamlql discover --file deployment.yml
```

The output will show that YamlQL has intelligently created multiple tables, including `spec` and `spec_template_spec_containers`. Now that you know the schema, you can write a precise query:

```bash
yamlql sql -f deployment.yml "SELECT name, image, resources_limits_cpu FROM spec_template_spec_containers" --output list
```
The `--output list` format is ideal here for clear, readable results.

### Example 3: Natural Language to SQL

Using the same `deployment.yml`, you can get answers without writing any SQL.

First, ensure your environment is configured for your LLM provider:
```bash
export YAMLQL_LLM_PROVIDER="OpenAI"
export OPENAI_API_KEY="sk-your-key-here"
```

Now, ask a question in plain English:
```bash
yamlql ai -f deployment.yml "what is the name of the container and what is its cpu limit?"
```
Same can be done with Gemini - just change the provider and set the API key:

```bash
export YAMLQL_LLM_PROVIDER="Gemini"
export GEMINI_API_KEY="sk-your-key-here"
```

YamlQL will show you the SQL it generated and then print the final answer, abstracting away all the complexity of the YAML structure and SQL syntax.

As stated above, we do not send your content to the LLM. Only the schema of the document is sent to generate the SQL query, which is then executed locally. This ensures your data remains private.

### Example files 

We have a few example files in the [tests/test_data](./tests/test_data) directory. You can use them to test the tool.


### YamlQL as a Library

If you want to use YamlQL in your own project, you can do so by importing the `YamlQL` class and using the `query` method.

```python
from yamlql_library import YamlQL

yql = YamlQL(file_path='config.yaml')

results = yql.query("SELECT * FROM root")
```
> Note: YamlQL as a Library needs to be tested more. We will be adding more tests and examples in the future. Feel free to contribute!

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was inspired by the need to query YAML files in a more structured way. It is built on top of the excellent [DuckDB](https://duckdb.org/) project.

## Contact

If you have any questions or feedback, please feel free to contact me in LinkedIn [@joshuajohnson](https://www.linkedin.com/in/aksarav/).

## TODO

- [ ] Add support for Ollama
- [ ] Add support for other LLM providers
- [ ] Finishing the YamlQL-Web project which is in progress - Stay tuned!


## If you like this project, Please ⭐⭐⭐⭐⭐ it on GitHub!

https://github.com/AKSarav/YamlQL



