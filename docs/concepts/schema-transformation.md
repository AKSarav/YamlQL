# Schema Transformation

YamlQL transforms YAML files into a relational database schema that you can query with SQL. This guide explains how you can control this transformation process using two powerful strategies: `depth` and `adaptive`.

## Choosing a Strategy

You can select a transformation strategy using the `--strategy` flag in the `discover` and `sql` commands.

*   **`--strategy depth` (Default):** Best for predictable, consistently structured files.
*   **`--strategy adaptive`:** Best for complex, nested, or inconsistently structured files.

---

## `depth` Strategy (Default)

This is the default strategy. It creates tables by recursing through your YAML file up to a specified depth, giving you direct control over the level of normalization.

### How It Works
The `depth` strategy walks through your nested objects and creates a new table for each one, until it reaches the limit specified by the `--max-depth` flag.

*   **`--max-depth <number>`:** This flag controls how many levels deep the transformer will go.
    *   A **lower number** (e.g., 2) will create fewer, wider tables with more flattened columns.
    *   A **higher number** (e.g., 5) will create more, smaller tables, resulting in a more normalized schema.

### Example

Given this YAML file:
```yaml
application:
  name: user-service
  database:
    host: db.example.com
    port: 5432
  features:
    - name: login
      enabled: true
    - name: signup
      enabled: false
```

**With `--max-depth 1`:**
The transformer will only process the top-level `application` object and flatten everything inside it.
```bash
yamlql discover -f config.yml --strategy depth --max-depth 1
```
Result: One table.
*   `application` (with columns `name`, `database_host`, `database_port`)
*   `application_features` (from the list of objects)

**With `--max-depth 2`:**
The transformer will go one level deeper, creating a separate table for the `database` object.
```bash
yamlql discover -f config.yml --strategy depth --max-depth 2
```
Result: Two tables.
*   `application` (with column `name`)
*   `application_database` (with columns `host` and `port`)
*   `application_features`

---

## `adaptive` Strategy

This strategy intelligently analyzes the content and shape of your YAML file to create the most intuitive and useful schema. The `--max-depth` flag is ignored in this mode.

### How It Works
The `adaptive` strategy follows a simple set of content-aware rules:

1.  **Isolate the Root:** It scans the top level of your YAML. Simple key-value pairs (like `apiVersion: apps/v1`) are collected into a single `root` table.

2.  **Top-Level Objects Become Tables:** Each top-level object (dictionary or list) becomes its own base table. For example, a `metadata` object at the root will become a `metadata` table.

3.  **Create Hierarchical Tables:** As it processes deeper nested objects, it creates new tables with hierarchical names. For example, a `template` object inside a `spec` object will become a `spec_template` table.

4.  **Normalize Lists of Objects:** A list of complex objects will be transformed into a single, multi-row table.

### Example

Given this Kubernetes-style YAML:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
```

```bash
yamlql discover -f k8s.yaml --strategy adaptive
```

**Resulting Tables:**
*   `root`: A table with `apiVersion` and `kind` columns.
*   `metadata`: A table with the `name` column.
*   `metadata_labels`: A table for the nested `labels` object.
*   `spec`: A table with the `replicas` column.
*   `spec_template_spec_containers`: A table with `name` and `image` columns, containing one row for each container in the list.

This creates a clean, normalized schema that accurately reflects the structure of your data, making it easy to write powerful and intuitive queries. 