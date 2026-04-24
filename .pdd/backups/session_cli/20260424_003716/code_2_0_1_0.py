"""
CLI application for tracking study sessions using Click.
This module provides the user interface for the session_store backend.
"""

from pathlib import Path
from typing import NoReturn
import click

# Assuming session_store is available in the environment as per the prompt instructions
try:
    from session_store import add_session, list_sessions, summarize
except ImportError:
    # Placeholder for environment where session_store isn't present
    pass


def get_default_store_path() -> Path:
    """Returns the default path for the session storage file."""
    base_dir = Path.home() / ".study_tracker"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "sessions.json"


def abort_on_error(message: str) -> NoReturn:
    """Prints a friendly error message and exits with status 1."""
    click.secho(f"Error: {message}", fg="red", err=True)
    raise click.Abort()


@click.group()
@click.option(
    "--store",
    type=click.Path(path_type=Path),
    default=get_default_store_path(),
    help="Path to the JSON storage file.",
)
@click.pass_context
def cli(ctx: click.Context, store: Path) -> None:
    """Study Tracker CLI - Record and analyze your learning progress."""
    ctx.ensure_object(dict)
    ctx.obj["STORE_PATH"] = store


@cli.command()
@click.option("--topic", required=True, help="The subject studied.")
@click.option("--minutes", required=True, type=int, help="Duration in minutes.")
@click.pass_context
def add(ctx: click.Context, topic: str, minutes: int) -> None:
    """Record a new study session."""
    store_path: Path = ctx.obj["STORE_PATH"]
    try:
        session = add_session(store_path, topic, minutes)
        click.echo(f"Session recorded successfully (ID: {session['id']}).")
    except ValueError as e:
        abort_on_error(str(e))


@cli.command(name="list")
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    """Show all recorded study sessions."""
    store_path: Path = ctx.obj["STORE_PATH"]
    try:
        sessions = list_sessions(store_path)
        if not sessions:
            click.echo("No sessions recorded yet.")
            return

        for s in sessions:
            # Format: "{id} | {created_at} | {minutes}m | {topic}"
            line = f"{s['id']} | {s['created_at']} | {s['minutes']}m | {s['topic']}"
            click.echo(line)
    except ValueError as e:
        abort_on_error(str(e))


@cli.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show total progress and per-topic breakdown."""
    store_path: Path = ctx.obj["STORE_PATH"]
    try:
        data = summarize(store_path)
        
        click.echo("=== Study Statistics ===")
        click.echo(f"Total Sessions: {data['total_sessions']}")
        click.echo(f"Total Time:     {data['total_minutes']} minutes")
        click.echo("\nBreakdown by Topic (Descending):")
        
        # Sort breakdown by minutes descending
        sorted_topics = sorted(
            data["by_topic"].items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        
        for topic, mins in sorted_topics:
            click.echo(f" - {topic}: {mins} min")
            
    except ValueError as e:
        abort_on_error(str(e))


# Testing logic below (usually in a separate test file)
# import pytest
# from click.testing import CliRunner
# from study_cli import cli

# @pytest.fixture
# def temp_store(tmp_path: Path) -> Path:
#     return tmp_path / "test_sessions.json"

# def test_add_session_creates_entry(temp_store: Path):
#     runner = CliRunner()
#     result = runner.invoke(cli, ["--store", str(temp_store), "add", "--topic", "Python", "--minutes", "30"])
#     assert result.exit_code == 0
#     assert "Session recorded" in result.output

# def test_list_sessions_displays_data(temp_store: Path):
#     runner = CliRunner()
#     runner.invoke(cli, ["--store", str(temp_store), "add", "--topic", "Python", "--minutes", "30"])
#     result = runner.invoke(cli, ["--store", str(temp_store), "list"])
#     assert "30m | Python" in result.output

# def test_stats_sorting(temp_store: Path):
#     runner = CliRunner()
#     runner.invoke(cli, ["--store", str(temp_store), "add", "--topic", "A", "--minutes", "10"])
#     runner.invoke(cli, ["--store", str(temp_store), "add", "--topic", "B", "--minutes", "50"])
#     result = runner.invoke(cli, ["--store", str(temp_store), "stats"])
#     assert result.output.find("B: 50 min") < result.output.find("A: 10 min")

if __name__ == "__main__":
    cli()