# cli.py
from pathlib import Path
import click
import sys
from typing import Final

from session_store import add_session, list_sessions, summarize

DEFAULT_STORE_PATH: Final[Path] = Path.home() / ".study_tracker" / "sessions.json"

@click.group()
@click.option(
    "--store",
    type=click.Path(path_type=Path),
    default=DEFAULT_STORE_PATH,
    help="Path to the JSON storage file."
)
@click.pass_context
def cli(ctx: click.Context, store: Path) -> None:
    """Study session tracker CLI."""
    ctx.ensure_object(dict)
    ctx.obj["store_path"] = store

@cli.command()
@click.option("--topic", required=True, help="Topic of the study session.")
@click.option("--minutes", required=True, type=int, help="Duration in minutes.")
@click.pass_context
def add(ctx: click.Context, topic: str, minutes: int) -> None:
    """Record a new study session."""
    store_path: Path = ctx.obj["store_path"]
    try:
        session = add_session(store_path, topic, minutes)
        click.echo(f"Session recorded. ID: {session['id']}")
    except ValueError as e:
        click.secho(f"Error: {e}", err=True, fg="red")
        sys.exit(1)

@cli.command(name="list")
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    """Show all recorded study sessions."""
    store_path: Path = ctx.obj["store_path"]
    sessions = list_sessions(store_path)
    
    if not sessions:
        click.echo("No sessions recorded yet.")
        return

    for s in sessions:
        # Format: {id} | {created_at} | {minutes}m | {topic}
        click.echo(f"{s['id']} | {s['created_at']} | {s['minutes']}m | {s['topic']}")

@cli.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show totals and per-topic breakdown."""
    store_path: Path = ctx.obj["store_path"]
    try:
        data = summarize(store_path)
    except Exception as e:
        click.secho(f"Error retrieving stats: {e}", err=True, fg="red")
        sys.exit(1)

    click.echo(f"Total Sessions: {data['total_sessions']}")
    click.echo(f"Total Minutes:  {data['total_minutes']}")
    click.echo("\nBreakdown by Topic:")
    
    # Sorted by minutes descending as per requirements
    sorted_topics = sorted(
        data["by_topic"].items(), 
        key=lambda item: item[1], 
        reverse=True
    )
    
    for topic, mins in sorted_topics:
        click.echo(f" - {topic}: {mins}m")

if __name__ == "__main__":
    cli()