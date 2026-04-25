import sys
from pathlib import Path

# Ensure the source directory is in the path for module discovery
# This allows importing 'quest_engine' from the parent directory structure
sys.path.append(str(Path(__file__).parent.parent / "src"))

from quest_engine import generate_daily_quests, Quest

def run_quest_example():
    """
    Demonstrates how to generate daily gamified quests from study session data.

    The generate_daily_quests function takes:
    - sessions (list[dict]): A list of dictionaries, where each dict contains 
      at least 'topic' (str) and 'minutes' (int).
    - daily_goal (int): Optional. The target study minutes for the day (default: 120).

    It returns:
    - list[Quest]: Exactly three Quest objects (TypedDict) containing progress,
      diversification goals, and reflection prompts.
    """

    # 1. Prepare sample session data (usually retrieved from a session store)
    # Note: We have studied Python heavily but neglected SQL.
    sessions = [
        {"id": "1", "topic": "Python 3.12", "minutes": 45},
        {"id": "2", "topic": "Python 3.12", "minutes": 30},
        {"id": "3", "topic": "SQL Optimization", "minutes": 15}
    ]

    # 2. Generate quests based on a 100-minute daily goal
    daily_goal = 100
    quests: list[Quest] = generate_daily_quests(sessions, daily_goal=daily_goal)

    print(f"--- Daily Quests (Goal: {daily_goal} min) ---\n")

    for i, quest in enumerate(quests, 1):
        status = "[COMPLETED]" if quest["completed"] else "[IN PROGRESS]"
        print(f"Quest {i}: {quest['title']}")
        print(f"Status:  {status}")
        print(f"Task:    {quest['description']}")
        print(f"Reward:  {quest['xp']} XP")
        print("-" * 30)

    # 3. Demonstration of Determinism
    # Quest 1 tracks progress: (45+30+15) = 90/100 minutes. Not completed.
    # Quest 2 targets 'SQL Optimization' as it has the least minutes (15).
    # Quest 3 is a static engagement prompt.

    total_xp = sum(q["xp"] for q in quests if q["completed"])
    print(f"\nTotal XP Earned so far: {total_xp}")

if __name__ == "__main__":
    run_quest_example()