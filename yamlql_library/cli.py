import typer
import rich
import rich.panel
from enum import Enum
from . import YamlQL

class OutputFormat(str, Enum):
    TABLE = "table"
    LIST = "list"

app = typer.Typer()

@app.command()
def query(
    sql_query: str = typer.Argument(..., help="The SQL query to execute."),
    file: str = typer.Option(..., "--file", "-f", help="Path to the YAML file to query."),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE, 
        "--output", 
        "-o", 
        help="The output format for the results."
    )
):
    """
    Run a SQL query against a YAML file and print the results.
    """
    try:
        yql = YamlQL(file_path=file)
        results = yql.query(sql_query)

        if results.empty:
            rich.print("[yellow]Query returned no results.[/yellow]")
            return
        
        if output == OutputFormat.LIST:
            for i, row in results.iterrows():
                rich.print(f"─[ Row {i+1} ]──────────────────")
                for col_name, value in row.items():
                    rich.print(f"  [bold cyan]{col_name}[/bold cyan]: {value}")
        else: # Default to table
            table = rich.table.Table(show_header=True, header_style="bold magenta")
            for col in results.columns:
                table.add_column(col)
            
            for _, row in results.iterrows():
                table.add_row(*[str(item) for item in row])
                
            rich.print(table)

    except FileNotFoundError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
    finally:
        if 'yql' in locals() and yql:
            yql.close()


@app.command()
def discover(
    file: str = typer.Option(..., "--file", "-f", help="Path to the YAML file to discover.")
):
    """
    Discovers and lists all tables and their columns from a YAML file.
    """
    try:
        yql = YamlQL(file_path=file)
        rich.print(f"Discovered tables in [bold cyan]{file}[/bold cyan]:")
        
        # Use SHOW ALL TABLES to get all created tables from DuckDB
        for row in yql.db.con.execute("SHOW ALL TABLES;").fetchall():
            table_name = row[2] # 'table_name' is the 3rd column
            panel_content = ""
            # Use PRAGMA to get column info
            for col_info in yql.db.con.execute(f"PRAGMA table_info('{table_name}');").fetchall():
                col_name = col_info[1]
                col_type = col_info[2]
                panel_content += f"  [bold]{col_name}[/bold]: {col_type}\n"
            
            panel = rich.panel.Panel(panel_content.strip(), title=f"[bold green]{table_name}[/bold green]", expand=False)
            rich.print(panel)

    except FileNotFoundError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
    finally:
        if 'yql' in locals() and yql:
            yql.close()

if __name__ == "__main__":
    app() 