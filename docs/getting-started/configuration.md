# Configuration Guide

YamlQL can be configured using environment variables and command-line options. This guide covers all available configuration options.

## Environment Variables

### Core Variables

| Variable | Description | Example |
|---|---|---|
| `YAMLQL_FILE` | Default YAML file to query | `export YAMLQL_FILE="config.yml"` |
| `YAMLQL_STRATEGY`| The transformation strategy (`depth` or `adaptive`). | `export YAMLQL_STRATEGY="adaptive"` |
| `YAMLQL_MAX_DEPTH`| Maximum recursion depth for the `depth` strategy. | `export YAMLQL_MAX_DEPTH=2` |
| `YAMLQL_OUTPUT`| The output format (`auto`, `table`, `list`). | `export YAMLQL_OUTPUT="list"` |
| `YAMLQL_MODE` | Default query mode (`SQL` or `AI`) | `export YAMLQL_MODE="SQL"` |

### AI Provider Configuration

| Variable | Description | Required For |
|----------|-------------|--------------|
| `YAMLQL_LLM_PROVIDER` | LLM provider to use (`OpenAI`, `Gemini`) | AI queries |
| `OPENAI_API_KEY` | OpenAI API key | OpenAI provider |
| `GEMINI_API_KEY` | Google Gemini API key | Gemini provider |

## Using .env Files

You can store configuration in a `.env` file in your project directory:

```ini
# Core settings
YAMLQL_FILE=config.yml
YAMLQL_MODE=SQL

# AI provider settings
YAMLQL_LLM_PROVIDER=OpenAI
OPENAI_API_KEY=sk-...
```

## Command-Line Options

### Global Options

| Option | Description | Example |
|--------|-------------|---------|
| `--version`, `-v` | Show version number | `yamlql --version` |
| `--execute`, `-e` | Execute query using environment variables | `yamlql -e "SELECT * FROM services"` |

### Command-Specific Options

#### SQL Command
```bash
yamlql sql [OPTIONS] QUERY
```

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | YAML file to query | Required |
| `--output`, `-o` | Output format (`auto`, `table`, `list`) | `auto` |

#### AI Command
```bash
yamlql ai [OPTIONS] QUESTION
```

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | YAML file to query | Required |
| `--output`, `-o` | Output format (`auto`, `table`, `list`) | `auto` |

#### Discover Command
```bash
yamlql discover [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | YAML file to analyze | Required |

## Output Formats

YamlQL supports three output formats:

1. **Table** (`table`): Default format for narrow results
   ```
   ┌────────┬───────────┐
   │ name   │ value     │
   ├────────┼───────────┤
   │ field1 │ value1    │
   │ field2 │ value2    │
   └────────┴───────────┘
   ```

2. **List** (`list`): Better for wide tables
   ```
   -- Record 1 --
   name: field1
   value: value1
   
   -- Record 2 --
   name: field2
   value: value2
   ```

3. **Auto** (`auto`): Automatically switches between table and list based on terminal width

## Configuration Examples

### Session-Based SQL Queries

You can create a session-like experience by setting your file and query mode in environment variables. This allows you to run multiple queries without repeating the arguments.

```bash
# Set your file and default to SQL mode
export YAMLQL_FILE="tests/test_data/kubernetes_deployment.yaml"
export YAMLQL_MODE="SQL"

# Now you can execute queries directly with the -e flag
yamlql -e "SELECT name, image FROM spec_template_spec_containers"
# ... (run more queries)
yamlql -e "SELECT replicas FROM spec"
```

### Session-Based AI Queries

The same session-based workflow can be used for AI queries.

```bash
# Set up your file, AI provider, and API key
export YAMLQL_FILE="tests/test_data/kubernetes_deployment.yaml"
export YAMLQL_LLM_PROVIDER="OpenAI"
export OPENAI_API_KEY="your-key"
export YAMLQL_MODE="AI"

# Now you can ask questions directly with the -e flag
yamlql -e "What is the CPU limit for the nginx container?"
# ... (ask more questions)
yamlql -e "How many containers are there?"
```

## Best Practices

1. **Environment Variables**
   - Use `.env` files for project-specific settings
   - Use shell environment variables for user-specific settings

2. **Output Format**
   - Use `list` format for tables with many columns
   - Use `table` format for compact data
   - Default to `auto` when unsure

3. **AI Configuration**
   - Keep API keys secure in environment variables
   - Consider using different providers for different use cases

4. **File Handling**
   - Use `YAMLQL_FILE` for frequently accessed files
   - Use `