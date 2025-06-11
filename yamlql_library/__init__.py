from pathlib import Path
import pandas as pd
from .loader import YamlLoader
from .transformer import DataTransformer
from .database import Database

class YamlQL:
    """
    The main class for querying YAML files with SQL.
    """
    def __init__(self, file_path: str):
        """
        Initializes the YamlQL instance.

        This loads the YAML file, transforms the data, and sets up the
        in-memory database.

        Args:
            file_path: The path to the YAML file.
        """
        path = Path(file_path)
        
        # 1. Load the data
        loader = YamlLoader(path)
        data = loader.load()

        # 2. Transform the data
        transformer = DataTransformer(data)
        self.tables = transformer.transform()
        
        # 3. Setup the database
        self.db = Database()
        self.db.create_tables(self.tables)

    def query(self, sql_query: str) -> pd.DataFrame:
        """
        Executes a SQL query against the loaded YAML data.

        Args:
            sql_query: The SQL query to run.

        Returns:
            A pandas DataFrame with the results.
        """
        return self.db.query(sql_query)

    def close(self):
        """Closes the database connection."""
        self.db.close()

    def list_tables(self):
        """Lists the tables that were created from the YAML file."""
        return [name for name, _ in self.tables] 