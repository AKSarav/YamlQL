# This file contains the core implementation logic for the CLI commands
# to avoid circular dependencies and overly complex CLI files.

import rich
import os
import typer
from . import YamlQL
from .llm_providers import get_llm_provider
from .utils import OutputFormat, _render_list, _render_table, _get_required_table_width
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

def run_query(sql_query: str, file: str, output: OutputFormat, max_depth: int = 5, strategy: str = "depth"):
    """Core logic for the 'query' command."""
    yql = None
    try:
        yql = YamlQL(file_path=file, max_depth=max_depth, strategy=strategy)
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

def run_interactive_sql(file: str, output: OutputFormat, max_depth: int = 5, strategy: str = "depth"):
    """Starts an interactive SQL prompt."""
    yql = None
    try:
        yql = YamlQL(file_path=file, max_depth=max_depth, strategy=strategy)
        rich.print(f"[bold green]Connected to {file}.[/bold green]")
        rich.print("Enter SQL commands (end with a semicolon) or interactive commands.")
        rich.print("Interactive commands: [bold cyan]listtables[/bold cyan], [bold cyan]listfields <table_name>[/bold cyan], [bold cyan]exit[/bold cyan]")
        
        session = PromptSession(
            history=FileHistory(os.path.expanduser("~/.yamlql_history")),
            auto_suggest=AutoSuggestFromHistory()
        )
        
        multiline_buffer = []

        while True:
            prompt_text = "yamlql> " if not multiline_buffer else "     ...> "
            line = session.prompt(prompt_text)
            command = line.strip().lower()

            if command in ('exit', 'quit'):
                break

            if command == 'listtables':
                tables = yql.db.con.execute("SHOW ALL TABLES;").fetchall()
                if tables:
                    rich.print("[bold green]Available tables:[/bold green]")
                    for table in tables:
                        rich.print(f"- {table[2]}")
                else:
                    rich.print("[yellow]No tables found.[/yellow]")
                continue

            if command.startswith('listfields'):
                parts = line.strip().split()
                if len(parts) < 2:
                    rich.print("[bold red]Error:[/bold red] Please provide a table name. Usage: listfields <table_name>")
                    continue
                
                table_name = parts[1]
                try:
                    columns = yql.db.con.execute(f"PRAGMA table_info('{table_name}');").fetchall()
                    if columns:
                        rich.print(f"[bold green]Fields for table '{table_name}':[/bold green]")
                        for col in columns:
                            rich.print(f"- [bold]{col[1]}[/bold]: {col[2]}")
                    else:
                        rich.print(f"[bold red]Error:[/bold red] Table '{table_name}' not found or has no columns.")
                except Exception as e:
                    rich.print(f"[bold red]Error:[/bold red] {e}")
                continue

            multiline_buffer.append(line)
            
            # If the line ends with a semicolon, it's time to execute
            if line.strip().endswith(';'):
                full_query = " ".join(multiline_buffer).strip()
                # Remove the trailing semicolon for DuckDB
                full_query = full_query[:-1]
                
                try:
                    results = yql.query(full_query)
                    if results.empty:
                        rich.print("[yellow]Query returned no results.[/yellow]")
                    else:
                        console = Console()
                        use_list_view = (
                            output == OutputFormat.LIST or
                            (output == OutputFormat.AUTO and _get_required_table_width(results) > console.width)
                        )
                        if use_list_view:
                            _render_list(results)
                        else:
                            _render_table(results)
                except Exception as e:
                    rich.print(f"[bold red]Query Error:[/bold red] {e}")

                multiline_buffer = [] # Reset for the next query

    except FileNotFoundError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
    finally:
        if yql:
            yql.close()
        rich.print("[bold]Exiting YamlQL.[/bold]")

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