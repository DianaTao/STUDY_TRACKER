
import sys
from pathlib import Path

# Add project root to sys.path to ensure local code is prioritized
# This allows testing local changes without installing the package
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pytest
from pathlib import Path
from typing import TypedDict, List

# Assuming the module is named 'quest_engine' and is importable
from quest_engine import generate_daily_quests, Quest

# Helper function to create a session for testing
def create_session(topic: str, minutes: int) -> dict:
    return {"id": "some_id", "topic": topic, "minutes": minutes, "created_at": "2023-01-01T10:00:00"}

def test_generate_daily_quests_empty_sessions():
    """
    Test quest generation with an empty list of sessions.
    Ensures default behavior for no study history.
    """
    sessions: List[dict] = []
    quests = generate_daily_quests(sessions)

    assert len(quests) == 3

    # Quest 1: Daily Goal Progress
    quest1 = quests[0]
    assert quest1["id"] == "daily_volume"
    assert quest1["title"] == "Consistency King"
    assert "0/120" in quest1["description"]
    assert not quest1["completed"]
    assert quest1["xp"] == 0

    # Quest 2: Topic Diversification (Least studied topic)
    quest2 = quests[1]
    assert quest2["id"] == "topic_focus"
    assert quest2["title"] == "Deep Diver"
    assert "a new topic" in quest2["description"]
    assert not quest2["completed"]
    assert quest2["xp"] == 30

    # Quest 3: Metadata/Reflection
    quest3 = quests[2]
    assert quest3["id"] == "reflection_check"
    assert quest3["title"] == "Philosopher's Stone"
    assert "Add a detailed note" in quest3["description"]
    assert not quest3["completed"]
    assert quest3["xp"] == 20

def test_generate_daily_quests_single_session_below_goal():
    """
    Test quest generation with a single session, total minutes below daily goal.
    """
    sessions = [create_session("Python", 60)]
    quests = generate_daily_quests(sessions, daily_goal=100)

    assert len(quests) == 3

    # Quest 1
    quest1 = quests[0]
    assert quest1["id"] == "daily_volume"
    assert "60/100" in quest1["description"]
    assert not quest1["completed"]
    assert quest1["xp"] == 0

    # Quest 2
    quest2 = quests[1]
    assert quest2["id"] == "topic_focus"
    assert "'Python'" in quest2["description"]
    assert not quest2["completed"]
    assert quest2["xp"] == 30

def test_generate_daily_quests_single_session_at_goal():
    """
    Test quest generation with a single session, total minutes exactly at daily goal.
    """
    sessions = [create_session("Python", 100)]
    quests = generate_daily_quests(sessions, daily_goal=100)

    assert len(quests) == 3

    # Quest 1
    quest1 = quests[0]
    assert quest1["id"] == "daily_volume"
    assert "100/100" in quest1["description"]
    assert quest1["completed"]
    assert quest1["xp"] == 50

def test_generate_daily_quests_multiple_sessions_above_goal():
    """
    Test quest generation with multiple sessions, total minutes above daily goal.
    """
    sessions = [
        create_session("Python", 60),
        create_session("System Design", 70),
        create_session("Python", 30),
    ]
    quests = generate_daily_quests(sessions, daily_goal=150)

    assert len(quests) == 3

    # Quest 1
    quest1 = quests[0]
    assert quest1["id"] == "daily_volume"
    assert "160/150" in quest1["description"]
    assert quest1["completed"]
    assert quest1["xp"] == 50

    # Quest 2: Python (90 min), System Design (70 min) -> System Design is least
    quest2 = quests[1]
    assert quest2["id"] == "topic_focus"
    assert "'System Design'" in quest2["description"]
    assert not quest2["completed"]
    assert quest2["xp"] == 30

def test_generate_daily_quests_topic_diversification_least_studied():
    """
    Test Quest 2 logic for identifying the least studied topic.
    """
    sessions = [
        create_session("Topic A", 30),
        create_session("Topic B", 60),
        create_session("Topic A", 15),
        create_session("Topic C", 20),
    ]
    # Topic A: 45 min, Topic B: 60 min, Topic C: 20 min
    # Least studied: Topic C
    quests = generate_daily_quests(sessions)
    quest2 = quests[1]
    assert quest2["id"] == "topic_focus"
    assert "'Topic C'" in quest2["description"]

def test_generate_daily_quests_topic_diversification_tie_breaking():
    """
    Test Quest 2 logic for tie-breaking when multiple topics have the same minimum minutes.
    Should sort alphabetically.
    """
    sessions = [
        create_session("Topic B", 30),
        create_session("Topic A", 30),
        create_session("Topic C", 40),
    ]
    # Topic A: 30 min, Topic B: 30 min, Topic C: 40 min
    # Least studied (tie): Topic A (alphabetically first)
    quests = generate_daily_quests(sessions)
    quest2 = quests[1]
    assert quest2["id"] == "topic_focus"
    assert "'Topic A'" in quest2["description"]

def test_generate_daily_quests_custom_daily_goal_zero():
    """
    Test with a daily goal of 0.
    """
    sessions = [create_session("Math", 10)]
    quests = generate_daily_quests(sessions, daily_goal=0)
    quest1 = quests[0]
    assert "10/0" in quest1["description"]
    assert quest1["completed"] # 10 >= 0 is True
    assert quest1["xp"] == 50

def test_generate_daily_quests_custom_daily_goal_large():
    """
    Test with a very large daily goal.
    """
    sessions = [create_session("Science", 5)]
    quests = generate_daily_quests(sessions, daily_goal=1000)
    quest1 = quests[0]
    assert "5/1000" in quest1["description"]
    assert not quest1["completed"]
    assert quest1["xp"] == 0

def test_generate_daily_quests_deterministic_output():
    """
    Ensures that the function is deterministic, returning the same output for the same input.
    """
    sessions = [
        create_session("Python", 45),
        create_session("System Design", 60),
        create_session("Python", 30),
        create_session("Algorithms", 10),
    ]
    daily_goal = 120

    quests1 = generate_daily_quests(sessions, daily_goal)
    quests2 = generate_daily_quests(sessions, daily_goal)

    assert quests1 == quests2

def test_generate_daily_quests_all_quest_fields_present_and_correct_type():
    """
    Verify that all generated quests have the required fields and correct types.
    """
    sessions = [create_session("Test Topic", 10)]
    quests = generate_daily_quests(sessions)

    for quest in quests:
        assert isinstance(quest, dict)
        assert "id" in quest and isinstance(quest["id"], str)
        assert "title" in quest and isinstance(quest["title"], str)
        assert "description" in quest and isinstance(quest["description"], str)
        assert "completed" in quest and isinstance(quest["completed"], bool)
        assert "xp" in quest and isinstance(quest["xp"], int)

    # Specific check for XP values
    assert quests[0]["xp"] in [0, 50]
    assert quests[1]["xp"] == 30
    assert quests[2]["xp"] == 20

def test_generate_daily_quests_no_sessions_with_custom_goal():
    """
    Test with empty sessions and a custom daily goal.
    """
    sessions: List[dict] = []
    quests = generate_daily_quests(sessions, daily_goal=50)

    assert len(quests) == 3

    # Quest 1
    quest1 = quests[0]
    assert "0/50" in quest1["description"]
    assert not quest1["completed"]
    assert quest1["xp"] == 0

    # Quest 2
    quest2 = quests[1]
    assert "a new topic" in quest2["description"]

    # Quest 3
    quest3 = quests[2]
    assert quest3["id"] == "reflection_check"