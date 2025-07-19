# AI Query Command

The `ai` command allows you to query YAML files using natural language. It uses LLMs (Language Learning Models) to convert your questions into SQL queries.

## Basic Usage

```bash
yamlql ai -f your-file.yml "What services are using the postgres image?"
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | YAML file to query | Required |
| `--output`, `-o` | Output format (`auto`, `table`, `list`) | `auto` |

## Setting Up AI Providers

### OpenAI

1. Get API key from [OpenAI Platform](https://platform.openai.com)
2. Set environment variables:
   ```bash
   export YAMLQL_LLM_PROVIDER="OpenAI"
   export OPENAI_API_KEY="your-api-key"
   ```

### Google Gemini

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set environment variables:
   ```bash
   export YAMLQL_LLM_PROVIDER="Gemini"
   export GEMINI_API_KEY="your-api-key"
   ```

## Example Questions

### Docker Compose Files

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
    ports:
      - "5432:5432"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

Questions:
```bash
# List services
yamlql ai -f docker-compose.yml "What services are defined?"

# Find specific images
yamlql ai -f docker-compose.yml "Which services use postgres?"

# Port information
yamlql ai -f docker-compose.yml "What ports are exposed by each service?"
```

### Kubernetes Manifests

```yaml
# deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
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
            memory: "256Mi"
```

Questions:
```bash
# Resource limits
yamlql ai -f deployment.yml "What are the CPU and memory limits?"

# Container details
yamlql ai -f deployment.yml "What containers are defined and what images do they use?"

# Replica count
yamlql ai -f deployment.yml "How many replicas are configured?"
```

## How It Works

1. Schema Analysis
   - YamlQL analyzes your YAML file structure
   - Creates a relational schema
   - Identifies tables and relationships

2. Question Processing
   - Your question is sent to the LLM provider
   - Only the schema is shared, not your data
   - LLM generates appropriate SQL query

3. Query Execution
   - Generated SQL is executed locally
   - Results are formatted and displayed
   - Original data never leaves your system

## Best Practices

### 1. Ask Clear Questions

Good:
```bash
yamlql ai -f config.yml "What is the database host and port?"
```

Not so good:
```bash
yamlql ai -f config.yml "database config"  # Too vague
```

### 2. Be Specific

Good:
```bash
yamlql ai -f docker-compose.yml "Which services expose port 5432?"
```

Not so good:
```bash
yamlql ai -f docker-compose.yml "What about ports?"  # Too general
```

### 3. One Question at a Time

Good:
```bash
yamlql ai -f deployment.yml "What is the CPU limit for nginx?"
yamlql ai -f deployment.yml "What is the memory limit for nginx?"
```

Not so good:
```bash
yamlql ai -f deployment.yml "What are all the limits and ports and volumes?"  # Too many questions
```

### 4. Use Context

Good:
```bash
yamlql ai -f k8s.yml "What containers in the backend namespace use more than 1GB memory?"
```

Not so good:
```bash
yamlql ai -f k8s.yml "memory usage"  # Lacks context
```

## Privacy and Security

YamlQL prioritizes data privacy:

1. **Local Processing**
   - Your YAML data stays local
   - Only schema information is shared
   - Queries run on your machine

2. **API Key Security**
   - Store API keys securely
   - Use environment variables
   - Consider using `.env` files

3. **Provider Selection**
   - Choose trusted providers
   - Control data sharing
   - Monitor API usage

## Common Questions

### 1. Resource Usage
```bash
# CPU limits
yamlql ai -f deployment.yml "Show containers using more than 500m CPU"

# Memory allocation
yamlql ai -f deployment.yml "List containers with memory limits above 1Gi"
```

### 2. Service Discovery
```bash
# Find services
yamlql ai -f docker-compose.yml "What databases are running?"

# Port mapping
yamlql ai -f docker-compose.yml "Which services expose public ports?"
```

### 3. Configuration Analysis
```bash
# Environment variables
yamlql ai -f config.yml "What environment variables are set for production?"

# Dependencies
yamlql ai -f docker-compose.yml "Show services that depend on postgres"
```

## Troubleshooting

### 1. Provider Issues
```
Error: YAMLQL_LLM_PROVIDER not set
```
Solution: Set provider environment variable

### 2. API Key Problems
```
Error: Authentication failed
```
Solution: Check API key and provider settings

### 3. Query Generation
```
Error: Could not generate SQL query
```
Solution: Rephrase question more clearly

## Related Topics

- [Configuration Guide](../getting-started/configuration.md)
- [SQL Query Command](sql.md)
- [Schema Transformation](../concepts/schema-transformation.md)
- [Metadata Tables](../concepts/metadata-tables.md) 