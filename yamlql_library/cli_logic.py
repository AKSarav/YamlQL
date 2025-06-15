# This file contains the core implementation logic for the CLI commands
# to avoid circular dependencies and overly complex CLI files.

import rich
import os
import typer
from . import YamlQL
from .llm_providers import get_llm_provider
from .utils import OutputFormat, _render_list, _render_table, _get_required_table_width
from rich.console import Console

def run_query(sql_query: str, file: str, output: OutputFormat):
    """Core logic for the 'query' command."""
    yql = None
    try:
        yql = YamlQL(file_path=file)
        results = yql.query(sql_query)

        if results.empty:
            rich.print("[yellow]Query returned no results.[/yellow]")
            return
        
        console = Console()
        use_list_view = (
            output == OutputFormat.LIST or
            (output == OutputFormat.AUTO and _get_required_table_width(results) > console.width)
        )

        if use_list_view:
            _render_list(results)
        else:
            _render_table(results)

    except FileNotFoundError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
    finally:
        if yql:
            yql.close()

def run_nlp(question: str, file: str, output: OutputFormat):
    """Core logic for the 'nlp' command."""
    yql = None
    try:
        yql = YamlQL(file_path=file)
        
        schema_lines = []
        for row in yql.db.con.execute("SHOW ALL TABLES;").fetchall():
            table_name = row[2]
            schema_lines.append(f"\n-- Table: {table_name}")
            for col_info in yql.db.con.execute(f"PRAGMA table_info('{table_name}');").fetchall():
                schema_lines.append(f"  - {col_info[1]}: {col_info[2]}")
        schema = "\n".join(schema_lines)

        provider_name = os.getenv("YAMLQL_LLM_PROVIDER")
        llm_provider = get_llm_provider(provider_name)

        rich.print("[yellow]Generating SQL query from your question...[/yellow]")
        sql_query = llm_provider.get_sql_query(schema, question)
        rich.print(f"[bold green]Generated SQL:[/bold green] [cyan]{sql_query}[/cyan]")

        results = yql.query(sql_query)

        if results.empty:
            rich.print("[yellow]Query executed successfully and returned no results.[/yellow]")
            return

        rich.print("\n[bold magenta]Query Results:[/bold magenta]")
        console = Console()
        use_list_view = (
            output == OutputFormat.LIST or
            (output == OutputFormat.AUTO and _get_required_table_width(results) > console.width)
        )

        if use_list_view:
            _render_list(results)
        else:
            _render_table(results)

    except (ValueError, NotImplementedError) as e:
        rich.print(f"[bold red]Configuration Error:[/bold red] {e}")
    except FileNotFoundError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
    finally:
        if yql:
            yql.close() 