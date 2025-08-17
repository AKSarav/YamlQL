# YamlQL

**Query YAML files with SQL.** Transform any YAML structure into a queryable database instantly.

[![Watch the video](./assets/YamlQL-Short.gif)](https://www.youtube.com/watch?v=6MRYTz027Fc)

## The Problem

YAML files are everywhere in modern infrastructure - Kubernetes manifests, Docker Compose files, configuration files, data dumps. But analyzing this data has always been painful:

- ❌ Each tool requires learning specific query syntax
- ❌ Complex nested structures are hard to navigate  
- ❌ No way to perform aggregations or joins across structures
- ❌ Manual scripting for every analysis task

## The Solution

YamlQL automatically transforms any YAML file into a relational database and lets you query it with SQL. No custom parsers, no complex scripts - just familiar SQL syntax that works on any YAML structure.

```bash
# Instead of complex parsing scripts...
yamlql sql -f deployment.yaml "SELECT name, image FROM containers WHERE image LIKE '%nginx%'"

# Or ask questions in plain English
yamlql ai -f config.yaml "What containers are using more than 1GB of memory?"
```

## Why YamlQL?

### ✅ **Universal Compatibility**
Works with ANY YAML structure - Kubernetes, Docker Compose, custom configs, data dumps. Our intelligent transformer uses universal heuristics, not hardcoded rules.

### ✅ **Zero Learning Curve** 
If you know SQL, you're ready. No domain-specific query languages to learn.

### ✅ **Instant Insights**
```sql
-- Find resource bottlenecks across all deployments
SELECT name, resources_limits_cpu, resources_requests_memory
FROM containers 
WHERE resources_limits_cpu > '1000m'
ORDER BY resources_limits_cpu DESC

-- Analyze service dependencies
SELECT service_name, COUNT(*) as container_count
FROM services 
GROUP BY service_name
```

### ✅ **Enterprise Ready**
Direct integration with BI tools, data pipelines, and existing SQL infrastructure. No export/import gymnastics.

## Quick Start

```bash
# Install
pip install yamlql

# Discover what's in your YAML
yamlql discover -f your-file.yaml

# Query anything
yamlql sql -f your-file.yaml "SELECT * FROM your_table"
```

## Real-World Examples

### Kubernetes Resource Audit
```sql
-- Find all containers missing resource limits
SELECT name, image 
FROM spec_template_spec_containers 
WHERE resources_limits_cpu IS NULL 
   OR resources_limits_memory IS NULL
```

### Docker Compose Analysis  
```sql
-- Identify services using outdated images
SELECT service_name, image 
FROM services 
WHERE image LIKE '%:latest' OR image NOT LIKE '%:%'
```

### Configuration Compliance
```sql
-- Check security policies across environments
SELECT environment, security_policy, COUNT(*) as violations
FROM configurations 
WHERE security_policy != 'enforced'
GROUP BY environment, security_policy
```

## AI-Powered Queries

Ask questions in plain English - YamlQL generates and executes SQL for you: 

We do not send your content to the LLM. Only the schema of the document is sent to generate the SQL query, which is then executed locally. This ensures your data remains private.

```bash
# Setup (your data stays private - only schema is sent to AI)
export YAMLQL_LLM_PROVIDER="OpenAI"  # or "Gemini"
export OPENAI_API_KEY="your-key"

# Query naturally
yamlql ai -f k8s-manifest.yaml "Which containers are using the most CPU?"
yamlql ai -f docker-compose.yml "Show me all database services and their ports"
```

## How It Works

Please refer to the [docs](https://docs.yamlql.com) for more details.

## Use Cases That Transform Teams

### **Platform Engineers**
```sql
-- Audit resource allocation across all services
SELECT namespace, AVG(CAST(cpu_limit AS FLOAT)) as avg_cpu
FROM containers GROUP BY namespace
```

### **DevOps Teams**  
```sql
-- Find deployment patterns and optimize
SELECT image, COUNT(*) as usage_count
FROM containers GROUP BY image ORDER BY usage_count DESC
```

### **Security Teams**
```sql
-- Compliance auditing at scale
SELECT service, security_context 
FROM pods WHERE security_context NOT LIKE '%nonroot%'
```

### **Data Teams**
```sql
-- Process configuration data for ML pipelines
SELECT environment, feature_flags, model_config
FROM app_configs WHERE environment = 'production'
```

## Library Usage

```python
from yamlql_library import YamlQL

# Load and query any YAML structure
yql = YamlQL(file_path='config.yaml')
results = yql.query("SELECT * FROM services WHERE port = 8080")
print(results)
```

## YamlQL vs Alternatives

| Tool | Learning Curve | Cross-Format Support | Complex Queries | BI Integration |
|------|----------------|---------------------|-----------------|----------------|
| **YamlQL** | ✅ SQL (universal) | ✅ Any YAML | ✅ Full SQL | ✅ Direct |
| **yq/jq** | ❌ Domain-specific | ❌ Path-based only | ❌ Limited | ❌ Manual export |
| **PyYAML** | ❌ Custom parsing | ❌ Schema-specific | ❌ Programmatic only | ❌ Custom integration |
| **kubectl** | ❌ K8s-specific | ❌ Kubernetes only | ❌ Basic filtering | ❌ Not designed for BI |

## Installation & Setup

```bash
# Install YamlQL
pip install yamlql

# For AI features, set your provider
export YAMLQL_LLM_PROVIDER="OpenAI"  # or "Gemini" 
export OPENAI_API_KEY="your-key"

# Quick test
yamlql discover -f tests/test_data/sample.yaml
```

## Advanced Features

### Session-Based Queries

For a more streamlined workflow, you can set your configuration once using environment variables and then run multiple queries without repeating the arguments.

```bash
# Set your file and query mode once
export YAMLQL_FILE="tests/test_data/kubernetes_deployment.yaml"
export YAMLQL_MODE="SQL"

# Now you can execute queries directly with the -e flag
yamlql -e "SELECT name, image FROM spec_template_spec_containers"
yamlql -e "SELECT replicas FROM spec"

# Switch to AI mode
export YAMLQL_MODE="AI"
yamlql -e "How many containers are there?"
```

### Transformation Strategies

YamlQL offers two powerful strategies to control how your YAML file is transformed into database tables. You can select a strategy using the `--strategy` flag with the `discover` and `sql` commands.

*   **`--strategy depth` (Default):** This strategy creates tables based on the nesting depth of your YAML. It's predictable and useful for consistently structured files. You can control the recursion level with the `--max-depth` flag (e.g., `--max-depth 2` for a flatter structure).

*   **`--strategy adaptive`:** This intelligent strategy analyzes the content and shape of your YAML to create the most intuitive schema. It automatically separates complex objects into their own tables while flattening simpler ones. This is the recommended strategy for complex or varied YAML files. Recommended for Kubernetes Configuration files.

```bash
# Use the adaptive strategy for a Kubernetes file
yamlql discover -f k8s.yaml --strategy adaptive

# Use the depth strategy for a simple config file
yamlql sql -f config.yaml --strategy depth --max-depth 2 "SELECT * FROM services"
```

### Output Formats
```bash
# Table format (default)
yamlql sql -f file.yaml "SELECT * FROM table"

# List format for wide tables
yamlql sql -f file.yaml "SELECT * FROM table" --output list
```

### Complex Joins
```sql
-- Join across related structures  
SELECT s.name, c.image, c.resources_limits_cpu
FROM services s
JOIN containers c ON s.name = c.service_name
WHERE c.resources_limits_cpu > '500m'
```

## Example Files

Try YamlQL with our test data:
```bash
# Kubernetes deployment
yamlql discover -f tests/test_data/kubernetes-deployment.yaml

# Docker Compose
yamlql discover -f tests/test_data/docker-compose.yaml

# Custom configuration
yamlql discover -f tests/test_data/complex-config.yaml
```

## Contributing

We welcome contributions! Whether it's:
- 🐛 Bug reports and fixes
- 📖 Documentation improvements  
- ✨ New features and enhancements
- 🧪 Test cases and examples

See our [contribution guidelines](CONTRIBUTING.md) to get started.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Get Started Now

```bash
pip install yamlql
yamlql discover -f your-file.yaml
# Start querying your YAML files with SQL!
```

**Transform your YAML analysis workflow today.** Stop writing custom parsers, stop learning new query languages - just use SQL on any YAML structure.

---


## Contributors

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/aksarav">
          <img src="https://github.com/aksarav.png" width="100px;" alt="@aksarav" style="border-radius:50%"/>
          <br />
          <sub><b>@aksarav</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/jithish-sekar">
          <img src="https://github.com/jithish-sekar.png" width="100px;" alt="@Jithish" style="border-radius:50%"/>
          <br />
          <sub><b>@Jithish</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/KumarSanthosh16">
          <img src="https://github.com/KumarSanthosh16.png" width="100px;" alt="@Santhosh" style="border-radius:50%"/>
          <br />
          <sub><b>@Santhosh</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/aakj2010">
          <img src="https://github.com/aakj2010.png" width="100px;" alt="@AK" style="border-radius:50%"/>
          <br />
          <sub><b>@AK</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/Prabha-46">
          <img src="https://github.com/Prabha-46.png" width="100px;" alt="@Prabha" style="border-radius:50%"/>
          <br />
          <sub><b>@Prabha</b></sub>
        </a>
      </td>
    </tr>
  </table>
</div>

---

**⭐ Star us on GitHub if YamlQL helps transform your YAML workflow!**  
[https://github.com/AKSarav/YamlQL](https://github.com/AKSarav/YamlQL)
