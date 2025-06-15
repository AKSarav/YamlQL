import pytest
from yamlql_library import YamlQL
import pandas as pd

SAMPLE_YAML_PATH = "tests/test_data/sample.yaml"

@pytest.fixture
def yql_instance():
    """Fixture to provide a YamlQL instance for tests."""
    instance = YamlQL(file_path=SAMPLE_YAML_PATH)
    yield instance
    instance.close()

def test_initialization(yql_instance):
    """Test that the YamlQL class initializes correctly."""
    assert yql_instance is not None
    assert yql_instance.db is not None

def test_table_creation(yql_instance):
    """Test that tables are created correctly from the YAML file."""
    tables = yql_instance.list_tables()
    assert "users" in tables
    assert "posts" in tables
    assert "settings" in tables

def test_simple_select_query(yql_instance):
    """Test a simple SELECT query on the 'users' table."""
    results = yql_instance.query("SELECT id, name FROM users ORDER BY id")
    assert isinstance(results, pd.DataFrame)
    assert len(results) == 2
    assert results['name'][0] == "John Doe"
    assert results['id'][1] == 2

def test_join_query(yql_instance):
    """Test a JOIN query between 'users' and 'posts' tables."""
    query = """
    SELECT u.name, p.title
    FROM users u
    JOIN posts p ON u.id = p.author_id
    WHERE u.name = 'John Doe'
    ORDER BY p.title
    """
    results = yql_instance.query(query)
    assert isinstance(results, pd.DataFrame)
    assert len(results) == 2
    assert results['title'][0] == "First Post"
    assert results['title'][1] == "Second Post"

# --- Tests for complex YAML file ---

COMPLEX_YAML_PATH = "tests/test_data/complex_sample.yaml"

@pytest.fixture
def complex_yql_instance():
    """Fixture for the complex YAML file."""
    instance = YamlQL(file_path=COMPLEX_YAML_PATH)
    yield instance
    instance.close()

def test_complex_table_creation(complex_yql_instance):
    """Test that the 'environments' table is created from the complex file."""
    tables = complex_yql_instance.list_tables()
    assert "environments" in tables
    assert "project_name" not in tables # This is a top-level key, not a table

def test_deeply_nested_query(complex_yql_instance):
    """Test querying a deeply nested field."""
    query = "SELECT config_database_credentials_username FROM environments WHERE name = 'production'"
    results = complex_yql_instance.query(query)
    assert len(results) == 1
    assert results['config_database_credentials_username'][0] == 'prod_user'

def test_missing_field_is_null(complex_yql_instance):
    """Test that a field missing in one record but present in another is handled as null."""
    query = "SELECT name, config_database_credentials_password_secret_ref FROM environments ORDER BY name"
    results = complex_yql_instance.query(query)
    
    # The 'development' env should have a null/None value for this field
    dev_row = results[results['name'] == 'development']
    assert len(dev_row) == 1
    # Pandas uses different representations for nulls, so we check for common ones
    assert pd.isna(dev_row['config_database_credentials_password_secret_ref'].iloc[0])

    # The 'production' env should have the value
    prod_row = results[results['name'] == 'production']
    assert len(prod_row) == 1
    assert prod_row['config_database_credentials_password_secret_ref'].iloc[0] == 'prod-db-password'

def test_relational_join_on_nested_list(complex_yql_instance):
    """
    Tests that the nested 'services' list was correctly transformed into a
    separate table and can be JOINed back to its parent.
    """
    tables = complex_yql_instance.list_tables()
    assert "environments_services" in tables

    query = """
    SELECT
        e.name as env_name,
        s.name as service_name,
        s.port
    FROM environments e
    JOIN environments_services s ON e.name = s.environments_name
    WHERE e.name = 'development'
    ORDER BY s.name
    """
    results = complex_yql_instance.query(query)
    
    assert len(results) == 2
    assert results['service_name'][0] == 'api-gateway'
    assert results['port'][0] == 8080
    assert results['service_name'][1] == 'user-service'
    assert results['port'][1] == 9001

# --- Tests for single-object YAML file (Kubernetes style) ---

K8S_YAML_PATH = "tests/test_data/deployment.yml"

@pytest.fixture
def k8s_yql_instance():
    """Fixture for the Kubernetes deployment YAML file."""
    instance = YamlQL(file_path=K8S_YAML_PATH)
    yield instance
    instance.close()

def test_k8s_table_creation(k8s_yql_instance):
    """Test that tables are created from top-level dictionaries."""
    tables = k8s_yql_instance.list_tables()
    assert "metadata" in tables
    assert "spec" in tables
    assert "apiVersion" not in tables # This is a scalar, not a table

def test_k8s_nested_query(k8s_yql_instance):
    """Test querying a nested field in a single-row table."""
    query = "SELECT selector_matchLabels_app FROM spec"
    results = k8s_yql_instance.query(query)
    assert len(results) == 1
    assert results['selector_matchLabels_app'][0] == 'nginx'

def test_k8s_relational_join(k8s_yql_instance):
    """Test that the nested 'containers' list was extracted and can be joined."""
    tables = k8s_yql_instance.list_tables()
    assert 'spec_template_spec_containers' in tables
    
    query = """
    SELECT
        s.replicas,
        c.name as container_name,
        c.image
    FROM spec s
    JOIN spec_template_spec_containers c 
        ON s.replicas = c.spec_replicas -- 'replicas' is a stable parent field to join on
    """
    results = k8s_yql_instance.query(query)
    assert len(results) == 1
    assert results['replicas'][0] == 3
    assert results['container_name'][0] == 'nginx'
    assert results['image'][0] == 'nginx:latest'

# --- Tests for deeply nested single-root YAML file ---

DEEP_YAML_PATH = "tests/test_data/deep_nested.yml"

@pytest.fixture
def deep_yql_instance():
    """Fixture for the deeply nested YAML file."""
    instance = YamlQL(file_path=DEEP_YAML_PATH)
    yield instance
    instance.close()

def test_deep_table_creation(deep_yql_instance):
    """Test that tables are created from the children of the single root object."""
    tables = deep_yql_instance.list_tables()
    assert "system" not in tables # The root object itself should not be a table
    assert "application" in tables
    assert "services" in tables
    assert "features" in tables
    assert "monitoring" in tables
    # 'audit' table should not be created as it would be empty
    assert "audit" not in tables
    
    # Check that a deeply nested list was also extracted correctly
    assert "audit_pipelines" in tables

# --- Tests for Edge Cases YAML file ---

EDGE_CASES_PATH = "tests/test_data/edge_cases.yml"

@pytest.fixture
def edge_case_yql_instance():
    """Fixture for the edge cases YAML file."""
    instance = YamlQL(file_path=EDGE_CASES_PATH)
    yield instance
    instance.close()

def test_edge_case_table_creation(edge_case_yql_instance):
    """Test that tables are created correctly for various edge cases."""
    tables = edge_case_yql_instance.list_tables()
    
    # Cases that should create tables
    assert "database" in tables
    assert "development" in tables
    assert "production" in tables
    assert "supported_regions" in tables
    assert "user-settings" in tables
    assert "defaults" in tables  # The anchor is resolved and treated as a table
    
    # Cases that should be ignored and not create tables
    assert "mixed_content" not in tables
    assert "empty_list_of_objects" not in tables

def test_null_value_handling(edge_case_yql_instance):
    """Test that various null formats are all treated as None/NULL."""
    results = edge_case_yql_instance.query("SELECT password, backup_schedule, description FROM database")
    assert len(results) == 1
    assert pd.isna(results['password'][0])
    assert pd.isna(results['backup_schedule'][0])
    assert pd.isna(results['description'][0])

def test_yaml_anchors_and_aliases(edge_case_yql_instance):
    """Test that aliased values are correctly resolved and can be overridden."""
    dev_results = edge_case_yql_instance.query("SELECT host, adapter, database FROM development")
    assert dev_results['host'][0] == 'localhost'
    assert dev_results['adapter'][0] == 'postgres'

    prod_results = edge_case_yql_instance.query("SELECT host, adapter, database FROM production")
    assert prod_results['host'][0] == 'localhost'
    assert prod_results['adapter'][0] == 'postgres_prod' # Value was overridden

def test_list_of_scalars(edge_case_yql_instance):
    """Test that a list of simple values becomes a single-column table."""
    results = edge_case_yql_instance.query("SELECT * FROM supported_regions")
    assert len(results) == 3
    assert results.columns[0] == 'supported_regions'
    assert results['supported_regions'][0] == 'us-east-1'

def test_special_characters_in_keys(edge_case_yql_instance):
    """Test that keys with spaces and dots are flattened correctly."""
    # Note: the transformer sanitizes 'font size' to 'font_size' and 'background.color' to 'background_color'
    results = edge_case_yql_instance.query("SELECT font_size, background_color FROM \"user-settings\"")
    assert results['font_size'].item() == 14
    assert results['background_color'].item() == 'dark-grey'

# --- Tests for Multi-Document YAML file ---

MULTI_DOC_PATH = "tests/test_data/multiple-entries.yaml"

@pytest.fixture
def multi_doc_yql_instance():
    """Fixture for the multi-document YAML file."""
    instance = YamlQL(file_path=MULTI_DOC_PATH)
    yield instance
    instance.close()

def test_multi_doc_table_creation(multi_doc_yql_instance):
    """Test that tables are created from all documents in a multi-document file."""
    tables = multi_doc_yql_instance.list_tables()
    
    # Check that tables from all documents are present
    assert "application" in tables
    assert "database" in tables
    assert "logging" in tables
    assert "features" in tables
    assert "monitoring" in tables
    
    # Check that a nested list from one of the documents was also extracted
    assert "logging_destinations" in tables
    assert "monitoring_escalation_contacts" in tables 