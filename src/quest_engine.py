# quest_engine.py
from typing import TypedDict
from pathlib import Path

class Quest(TypedDict):
    """Represents a gamified daily quest."""
    id: str
    title: str
    description: str
    completed: bool
    xp: int

def generate_daily_quests(sessions: list[dict], daily_goal: int = 120) -> list[Quest]:
    """
    Generates exactly three deterministic quests based on session history.
    
    Requirements:
    1. Quest 1: Progress toward the daily goal.
    2. Quest 2: Focus on the least-studied topic from the history.
    3. Quest 3: Encouragement for metadata/reflection.
    """
    quests: list[Quest] = []

    # Quest 1: Daily Goal Progress
    total_minutes = sum(s["minutes"] for s in sessions)
    is_goal_met = total_minutes >= daily_goal
    quests.append({
        "id": "daily_volume",
        "title": "Consistency King",
        "description": f"Reach {daily_goal} minutes of study today. ({total_minutes}/{daily_goal})",
        "completed": is_goal_met,
        "xp": 50 if is_goal_met else 0
    })

    # Quest 2: Topic Diversification (Least studied topic)
    # If no sessions, provide a default prompt.
    topic_map: dict[str, int] = {}
    for s in sessions:
        topic = s["topic"]
        topic_map[topic] = topic_map.get(topic, 0) + s["minutes"]
    
    # Deterministic selection: sort by minutes ascending, then alphabetically by topic
    sorted_topics = sorted(topic_map.items(), key=lambda x: (x[1], x[0]))
    
    target_topic = sorted_topics[0][0] if sorted_topics else "a new topic"
    quests.append({
        "id": "topic_focus",
        "title": "Deep Diver",
        "description": f"Spend more time on '{target_topic}' to balance your knowledge.",
        "completed": False,
        "xp": 30
    })

    # Quest 3: Metadata/Reflection (Static deterministic engagement quest)
    quests.append({
        "id": "reflection_check",
        "title": "Philosopher's Stone",
        "description": "Add a detailed note to your next session recording.",
        "completed": False,
        "xp": 20
    })

    return quests