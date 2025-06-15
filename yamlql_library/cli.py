import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Proactively check for old completion scripts to prevent a traceback.
if "_YAMLQL_COMPLETE" in os.environ:
    # This environment variable is set by the shell when it calls for completions.
    # We exit gracefully to prevent a crash from old, lingering completion scripts.
    print("\nNote: YamlQL autocompletion is disabled. Please remove the old completion script from your shell's configuration.")
    sys.exit(0)

import typer
import rich
import rich.panel
from . import YamlQL
from .llm_providers import get_llm_provider
from . import cli_logic
from .utils import OutputFormat

app = typer.Typer(
    add_completion=False,
    help="YamlQL: A command-line tool to query YAML files using SQL.",
    no_args_is_help=True, # Show help if no command is given
)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    execute: str = typer.Option(
        None,
        "--execute",
        "-e",
        help="A direct SQL or NLP query to run using session environment variables.",
    ),
):
    """
    Main callback to handle the --execute/-e flag for direct queries.
    """
    # If a subcommand is being invoked (e.g., query, discover), do nothing.
    if ctx.invoked_subcommand is not None:
        return

    # If --execute is used, run the query and exit.
    if execute:
        file = os.environ.get("YAMLQL_FILE")
        mode = (os.environ.get("YAMLQL_MODE") or "SQL").upper()

        if not file:
            rich.print("[bold red]Error:[/bold red] The --execute/-e flag requires the YAMLQL_FILE environment variable to be set.", file=sys.stderr)
            raise typer.Exit(code=1)

        if mode == "SQL":
            cli_logic.run_query(execute, file, OutputFormat.AUTO)
        elif mode == "AI":
            cli_logic.run_nlp(execute, file, OutputFormat.AUTO)
        else:
            rich.print("[bold red]Error:[/bold red] Invalid YAMLQL_MODE set. Use SQL or AI.", file=sys.stderr)
            raise typer.Exit(code=1)
        
        # Exit after execution to prevent Typer from looking for a subcommand.
        raise typer.Exit()

@app.command(name="sql")
def sql_command(
    sql_query: str = typer.Argument(..., help="The SQL query to execute."),
    file: str = typer.Option(..., "--file", "-f", help="Path to the YAML file to query."),
    output: OutputFormat = typer.Option(
        OutputFormat.AUTO, 
        "--output", 
        "-o", 
        help="Output format. 'auto' switches to list if table exceeds terminal width."
    )
):
    """
    Run a SQL query against a YAML file and print the results.
    """
    cli_logic.run_query(sql_query, file, output)


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

@app.command(name="ai")
def ai_command(
    question: str = typer.Argument(..., help="The natural language question to ask about the YAML file."),
    file: str = typer.Option(..., "--file", "-f", help="Path to the YAML file to query."),
    output: OutputFormat = typer.Option(
        OutputFormat.AUTO, 
        "--output", 
        "-o", 
        help="Output format. 'auto' switches to list if table exceeds terminal width."
    )
):
    """
    Answers a natural language question about a YAML file by generating and executing a SQL query.
    Requires environment variables for the chosen LLM provider (e.g., YAMLQL_LLM_PROVIDER and OPENAI_API_KEY).
    """
    cli_logic.run_nlp(question, file, output)

if __name__ == "__main__":
    app() 