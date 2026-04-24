import os
from pathlib import Path
from click.testing import CliRunner
from session_cli import cli

def run_cli_example():
    """
    Demonstrates how to use the session_cli module via Click's CliRunner.
    
    This example covers:
    1. Initializing a temporary storage path.
    2. Adding study sessions via the 'add' command.
    3. Listing sessions using the 'list' command.
    4. Viewing aggregated statistics via the 'stats' command.
    
    Input Parameters:
    - --store: (Path) The location of the JSON database (defaults to ~/.study_tracker/sessions.json).
    - --topic: (String) Used in 'add' to define the subject.
    - --minutes: (Integer) Used in 'add' to define the duration.

    Output:
    - Console output managed by Click (echo/secho).
    """
    runner = CliRunner()
    
    # Define a local path for the example storage file relative to this script
    base_dir = Path(__file__).parent
    example_store = base_dir / "example_sessions.json"
    
    # Ensure a clean state for the example
    if example_store.exists():
        example_store.unlink()

    print(f"--- Starting Study Tracker CLI Example ---")
    print(f"Storage: {example_store.name}\n")

    try:
        # 1. Add Sessions
        # Command: study add --topic <name> --minutes <int>
        print("Action: Adding sessions for 'Python' and 'Algorithms'...")
        runner.invoke(cli, ["--store", str(example_store), "add", "--topic", "Python", "--minutes", "45"])
        runner.invoke(cli, ["--store", str(example_store), "add", "--topic", "Algorithms", "--minutes", "90"])
        runner.invoke(cli, ["--store", str(example_store), "add", "--topic", "Python", "--minutes", "30"])

        # 2. List Sessions
        # Command: study list
        print("\nAction: Listing all recorded sessions:")
        list_result = runner.invoke(cli, ["--store", str(example_store), "list"])
        print(list_result.output)

        # 3. Show Stats
        # Command: study stats
        # Note: This displays totals and a breakdown sorted by minutes descending.
        print("Action: Displaying study statistics:")
        stats_result = runner.invoke(cli, ["--store", str(example_store), "stats"])
        print(stats_result.output)

        # 4. Error Handling
        # Demonstrate response to invalid input (e.g., negative minutes if handled by backend)
        print("Action: Testing error handling with invalid data:")
        error_result = runner.invoke(cli, ["--store", str(example_store), "add", "--topic", "", "--minutes", "-5"])
        if error_result.exit_code != 0:
            print("Caught expected CLI error for invalid input.")

    finally:
        # Cleanup the example file created
        if example_store.exists():
            example_store.unlink()
            print(f"\nCleaned up {example_store.name}")

if __name__ == "__main__":
    run_cli_example()