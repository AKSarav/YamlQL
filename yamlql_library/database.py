import duckdb
import pandas as pd
from typing import List, Tuple

class Database:
    """Manages an in-memory DuckDB database."""

    def __init__(self):
        """Initializes a new in-memory DuckDB connection."""
        self.con = duckdb.connect(database=':memory:')

    def create_tables(self, tables: List[Tuple[str, pd.DataFrame]]):
        """
        Registers a list of pandas DataFrames as tables in DuckDB.

        Args:
            tables: A list of tuples, where each tuple contains a table name
                    and the corresponding DataFrame.
        """
        existing = set()
        for name, df in tables:
            candidate = name
            i = 1
            # Ensure unique table names inside this DuckDB connection
            while candidate in existing:
                candidate = f"{name}_{i}"
                i += 1
            self.con.register(candidate, df)
            existing.add(candidate)

    def query(self, sql_query: str) -> pd.DataFrame:
        """
        Executes a SQL query against the database.

        Args:
            sql_query: The SQL query to execute.

        Returns:
            A pandas DataFrame containing the query results.
        """
        return self.con.execute(sql_query).fetchdf()

    def close(self):
        """Closes the database connection."""
        self.con.close() 