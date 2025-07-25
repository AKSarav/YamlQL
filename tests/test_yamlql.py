import pytest
import pandas as pd
from typer.testing import CliRunner
import os

from yamlql_library import YamlQL
from yamlql_library.cli import app

# --- Fixtures ---

runner = CliRunner()

@pytest.fixture
def create_test_file():
    """A factory fixture to create temporary test files."""
    files_to_clean_up = []
    def _create_test_file(filename, content):
        with open(filename, "w") as f:
            f.write(content)
        files_to_clean_up.append(filename)
        return filename
    
    yield _create_test_file
    
    for f in files_to_clean_up:
        os.remove(f)

# --- Library-Level Tests (Directly testing the YamlQL class) ---

def test_root_level_list_creates_root_table(create_test_file):
    """Tests that a YAML file whose root is a list of objects creates a 'root' table."""
    content = """
- name: service-a
  image: nginx:latest
- name: service-b
  image: apache:latest
"""
    test_file = create_test_file("root_list.yml", content)
    yql = YamlQL(file_path=test_file)
    assert "root" in yql.list_tables()
    results = yql.query("SELECT name FROM root WHERE image = 'nginx:latest'")
    assert len(results) == 1
    assert results['name'][0] == 'service-a'
    yql.close()

def test_hyphenated_keys_and_nested_lists_of_objects(create_test_file):
    """Tests that hyphenated keys are sanitized and nested lists of objects create new tables."""
    content = """
service-catalog:
  name: "Cloud Services"
  providers:
    - name: "aws"
      services:
        - service-name: "amazon-rds"
          type: "database"
        - service-name: "aws-lambda"
          type: "compute"
"""
    test_file = create_test_file("hyphens.yml", content)
    yql = YamlQL(file_path=test_file)
    tables = yql.list_tables()
    
    assert "service_catalog" in tables
    assert "service_catalog_providers" in tables
    assert "service_catalog_providers_services" in tables
    
    results = yql.query("SELECT type FROM service_catalog_providers_services WHERE service_name = 'amazon_rds'")
    assert len(results) == 1
    assert results['type'][0] == 'database'
    yql.close()

def test_mixed_type_list_becomes_string_list_column(create_test_file):
    """Tests that lists with mixed scalar types become a single LIST<VARCHAR> column."""
    content = """
settings:
  - name: feature_flags
    options: [True, 123, "hello", null]
"""
    test_file = create_test_file("mixed_list.yml", content)
    yql = YamlQL(file_path=test_file)
    
    assert 'settings' in yql.list_tables()
    
    # DuckDB returns list elements as a tuple from a query
    results = yql.query("SELECT options FROM settings").iloc[0,0]
    assert results == ('True', '123', 'hello', 'None')
    
    # Also test with UNNEST
    unnest_results = yql.query("SELECT UNNEST(options) as opt FROM settings")
    expected = ['True', '123', 'hello', 'None']
    assert len(unnest_results) == 4
    assert sorted(unnest_results['opt'].tolist()) == sorted(expected)

    yql.close()

# --- CLI-Level Tests (Using Typer's CliRunner to test the app) ---

def test_cli_discover_command(create_test_file):
    """Test the 'discover' command successfully finds tables."""
    content = "users:\n  - name: test"
    test_file = create_test_file("discover.yml", content)
    
    result = runner.invoke(app, ["discover", "-f", test_file])
    
    assert result.exit_code == 0
    assert "Discovered tables" in result.stdout
    assert "users" in result.stdout

def test_cli_sql_from_file_option(create_test_file):
    """Test running a query using the --sql-file option."""
    yaml_content = "users:\n  - id: 1\n    name: cli_user"
    yaml_file = create_test_file("cli_test.yml", yaml_content)
    
    sql_content = "SELECT name FROM users WHERE id = 1"
    sql_file = create_test_file("query.sql", sql_content)
    
    result = runner.invoke(app, ["sql", "-f", yaml_file, "--sql-file", sql_file])
    
    assert result.exit_code == 0
    assert "cli_user" in result.stdout

def test_cli_sql_without_quotes(create_test_file):
    """Test that a simple SQL query can be run without quotes."""
    yaml_content = "users:\n  - name: no_quotes_user"
    yaml_file = create_test_file("no_quotes.yml", yaml_content)

    result = runner.invoke(app, ["sql", "-f", yaml_file, "SELECT", "name", "FROM", "users"])

    assert result.exit_code == 0
    assert "no_quotes_user" in result.stdout

def test_cli_interactive_mode_is_triggered(create_test_file):
    """Test that interactive mode starts when no query is provided."""
    yaml_content = "data:\n  - value: 1"
    yaml_file = create_test_file("interactive.yml", yaml_content)

    # Use the 'input' argument to pass 'exit' to the prompt, closing it immediately.
    result = runner.invoke(app, ["sql", "-f", yaml_file], input="exit\n")

    assert result.exit_code == 0
    assert "Connected to" in result.stdout
    assert "Enter SQL commands" in result.stdout
    assert "Exiting YamlQL" in result.stdout

def test_dictionary_of_objects_creates_separate_tables(create_test_file):
    """
    Tests the core principle that a dictionary whose values are all dictionaries
    (a common pattern for a collection of named objects) creates a separate table
    for each entry, not one combined table.
    """
    content = """
services:
  postgres:
    image: postgres:14
    ports: ["5432:5432"]
  redis:
    image: redis:7
"""
    test_file = create_test_file("docker_compose_style.yml", content)
    yql = YamlQL(file_path=test_file)
    tables = yql.list_tables()

    # Assert that a separate table was created for each service
    assert "services_postgres" in tables
    assert "services_redis" in tables
    # Assert that a single "services" table was NOT created
    assert "services" not in tables

    # Verify content of one of the tables
    postgres_results = yql.query("SELECT image FROM services_postgres")
    assert postgres_results['image'][0] == 'postgres:14'
    yql.close() 