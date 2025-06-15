import pandas as pd
from rich.table import Table
from rich.console import Console
import rich
from enum import Enum

class OutputFormat(str, Enum):
    AUTO = "auto"
    TABLE = "table"
    LIST = "list"

def _get_required_table_width(df: pd.DataFrame) -> int:
    """Calculates the minimum terminal width required to display a dataframe as a table."""
    # Add 4 characters for padding/borders per column
    return sum(df.columns.map(len)) + (len(df.columns) * 4)

def _render_table(df: pd.DataFrame):
    """Renders a pandas DataFrame as a rich Table."""
    table = Table(show_header=True, header_style="bold magenta")
    for col in df.columns:
        table.add_column(col)
    for _, row in df.iterrows():
        table.add_row(*[str(item) for item in row])
    rich.print(table)

def _render_list(df: pd.DataFrame):
    """Renders a pandas DataFrame as a rich List of dictionaries."""
    console = Console()
    for i, row in df.iterrows():
        console.print(f"[bold yellow]-- Record {i+1} --[/bold yellow]")
        for col, val in row.items():
            console.print(f"  [bold cyan]{col}:[/bold cyan] {val}") 