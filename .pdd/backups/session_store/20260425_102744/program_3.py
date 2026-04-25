import os
from pathlib import Path
from session_store import add_session, list_sessions, summarize

def run_example():
    """
    Demonstrates how to use the session_store module to track study habits.
    
    This script will:
    1. Initialize a path for a JSON storage file.
    2. Add new study sessions (input: Path, topic string, minutes integer).
    3. List all recorded sessions (output: list of session dictionaries).
    4. Generate summary statistics (output: dictionary with totals and topic breakdown).
    """
    # Define the store path relative to this script
    current_dir = Path(os.path.dirname(__file__))
    store_path = current_dir / "study_data.json"

    # Ensure we start fresh for the example
    if store_path.exists():
        store_path.unlink()

    print(f"--- Initializing session store at: {store_path.name} ---\n")

    try:
        # 1. Add some study sessions
        # Parameters: (store_path: Path, topic: str, minutes: int)
        print("Adding sessions...")
        s1 = add_session(store_path, "Python 3.12 Features", 45)
        s2 = add_session(store_path, "System Design", 60)
        s3 = add_session(store_path, "Python 3.12 Features", 30)
        
        print(f"Created session: {s1['topic']} ({s1['minutes']} min)")
        print(f"Created session: {s2['topic']} ({s2['minutes']} min)")
        print(f"Created session: {s3['topic']} ({s3['minutes']} min)\n")

        # 2. List all sessions
        # Returns: list[Session] (TypedDict with id, topic, minutes, created_at)
        print("History of sessions (Sorted by date):")
        history = list_sessions(store_path)
        for entry in history:
            print(f"[{entry['created_at']}] ID: {entry['id']} | {entry['topic']} | {entry['minutes']} min")

        # 3. Get summary statistics
        # Returns: Summary (TypedDict with total_sessions, total_minutes, by_topic)
        print("\n--- Study Summary ---")
        stats = summarize(store_path)
        print(f"Total Sessions: {stats['total_sessions']}")
        print(f"Total Time:     {stats['total_minutes']} minutes")
        print("Breakdown by Topic:")
        for topic, mins in stats['by_topic'].items():
            print(f" - {topic}: {mins} min")

        # 4. Error Handling Example
        print("\nTesting validation...")
        try:
            add_session(store_path, "", -10)  # This will trigger a ValueError
        except ValueError as e:
            print(f"Caught expected error: {e}")

    finally:
        # Cleanup example file
        if store_path.exists():
            store_path.unlink()
            print(f"\nCleaned up {store_path.name}")

if __name__ == "__main__":
    run_example()