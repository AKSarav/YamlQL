from pathlib import Path
import pandas as pd
from .loader import YamlLoader
from .transformer import DataTransformer
from .database import Database

class YamlQL:
    """Main entry-point for turning one or *many* YAML files into a DuckDB session.

    """

    def __init__(
        self,
        file_paths: str | list[str] | None = None,
        *,
        file_path: str | None = None,
        add_source_column: bool = True,
        prefix_tables: bool = True,
    ):
        """Load one or more YAML files and register their tables.

        Args
        ----
        file_paths
            A single path or a list of paths.
        add_source_column
            If *True* (default) a column named ``__source_file`` is added to all
            tables containing the *basename* of the YAML file that produced the
            row.
        prefix_tables
            If *True* (default) each table name is prefixed with the file stem
            (e.g. ``sample_users``).  Disabling keeps old single-file behaviour
            but risks name collisions.
        """

        # Back-compat: allow old single 'file_path'
        if file_paths is None and file_path is not None:
            file_paths = file_path

        if file_paths is None:
            raise ValueError("YamlQL requires at least one file path")

        # Normalise to list of Path objects
        if isinstance(file_paths, (str, Path)):
            path_list: list[Path] = [Path(file_paths)]
        else:
            path_list = [Path(p) for p in file_paths]

        all_tables: list[tuple[str, pd.DataFrame]] = []

        for path in path_list:
            # 1. Load YAML
            loader = YamlLoader(path)
            data = loader.load()

            # 2. Transform to relational tables
            transformer = DataTransformer(data)
            file_tables = transformer.transform()

            # 3. Optionally prefix table names & add provenance column
            prefix = path.stem.replace("-", "_").replace(" ", "_") if prefix_tables else ""

            for original_name, df in file_tables:
                new_name = f"{prefix}_{original_name}" if prefix else original_name

                if add_source_column:
                    df = df.copy()
                    df["__source_file"] = path.name

                all_tables.append((new_name, df))

        # Keep a reference for backwards-compatibility
        self.tables = all_tables

        # 4. Setup DuckDB and register everything
        self.db = Database()
        self.db.create_tables(all_tables)

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
        """Return list of registered table names."""
        return [row[0] for row in self.db.con.execute("SHOW ALL TABLES").fetchall()] 