"""
Study Quest Store: A JSON-backed persistence layer for gamified study tracking.
"""

import json
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import TypedDict, Optional


VALID_MOODS = {"focused", "tired", "distracted", "confident", "neutral"}


class Session(TypedDict):
    id: int
    topic: str
    minutes: int
    mood: str
    notes: str
    created_at: str


class StudySummary(TypedDict):
    total_sessions: int
    total_minutes: int
    by_topic: dict[str, int]
    today_minutes: int
    daily_goal: int
    daily_goal_percent: int
    streak_days: int
    favorite_topic: Optional[str]
    average_session_minutes: float
    achievements: list[str]
    suggestion: str


def _load_data(store_path: Path) -> list[Session]:
    if not store_path.exists():
        return []
    try:
        with open(store_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_data(store_path: Path, data: list[Session]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write using a temporary file
    fd, temp_path_str = tempfile.mkstemp(dir=store_path.parent, text=True)
    temp_path = Path(temp_path_str)
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_path.replace(store_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def add_session(
    store_path: Path,
    topic: str,
    minutes: int,
    mood: str = "neutral",
    notes: str = "",
    created_at: str | None = None,
) -> Session:
    if minutes <= 0:
        raise ValueError("Minutes must be a positive integer.")
    if not topic.strip():
        raise ValueError("Topic cannot be empty.")
    if mood not in VALID_MOODS:
        raise ValueError(f"Invalid mood. Must be one of: {', '.join(VALID_MOODS)}")

    data = _load_data(store_path)
    new_id = max([s["id"] for s in data], default=0) + 1
    
    timestamp = created_at or datetime.now().isoformat()
    
    new_session: Session = {
        "id": new_id,
        "topic": topic.strip(),
        "minutes": minutes,
        "mood": mood,
        "notes": notes,
        "created_at": timestamp,
    }
    
    data.append(new_session)
    _save_data(store_path, data)
    return new_session


def list_sessions(
    store_path: Path, topic: str | None = None, limit: int | None = None
) -> list[Session]:
    sessions = _load_data(store_path)
    sessions.sort(key=lambda x: x["created_at"])

    if topic:
        sessions = [s for s in sessions if s["topic"] == topic]

    if limit is not None:
        sessions = sessions[-limit:]

    return sessions


def delete_session(store_path: Path, session_id: int) -> bool:
    data = _load_data(store_path)
    initial_len = len(data)
    data = [s for s in data if s["id"] != session_id]
    
    if len(data) < initial_len:
        _save_data(store_path, data)
        return True
    return False


def summarize(store_path: Path, daily_goal: int = 120) -> StudySummary:
    sessions = _load_data(store_path)
    today_str = date.today().isoformat()
    
    total_minutes = sum(s["minutes"] for s in sessions)
    by_topic: dict[str, int] = {}
    today_minutes = 0
    active_dates: set[date] = set()

    for s in sessions:
        dt = datetime.fromisoformat(s["created_at"])
        session_date = dt.date()
        active_dates.add(session_date)
        
        by_topic[s["topic"]] = by_topic.get(s["topic"], 0) + s["minutes"]
        
        if session_date.isoformat() == today_str:
            today_minutes += s["minutes"]

    # Calculate Streak
    streak = 0
    check_date = date.today()
    while check_date in active_dates:
        streak += 1
        check_date -= timedelta(days=1)

    # Achievements
    achievements = []
    if len(sessions) >= 1:
        achievements.append("First Focus")
    if any(s["minutes"] >= 90 for s in sessions):
        achievements.append("Deep Work")
    if streak >= 2:
        achievements.append("Consistency Starter")
    if today_minutes >= 100:
        achievements.append("100 Minute Day")
    if len(by_topic) >= 3:
        achievements.append("Topic Explorer")

    # Suggestion logic
    if not sessions:
        suggestion = "Ready to start? Add your first study session!"
    elif today_minutes >= daily_goal:
        suggestion = "Goal reached! Excellent work today."
    else:
        remaining = daily_goal - today_minutes
        suggestion = f"Keep going! {remaining} more minutes to reach your daily goal."

    favorite_topic = max(by_topic, key=by_topic.get) if by_topic else None
    avg_minutes = total_minutes / len(sessions) if sessions else 0.0

    return {
        "total_sessions": len(sessions),
        "total_minutes": total_minutes,
        "by_topic": by_topic,
        "today_minutes": today_minutes,
        "daily_goal": daily_goal,
        "daily_goal_percent": min(100, int((today_minutes / daily_goal) * 100)) if daily_goal > 0 else 100,
        "streak_days": streak,
        "favorite_topic": favorite_topic,
        "average_session_minutes": float(avg_minutes),
        "achievements": achievements,
        "suggestion": suggestion,
    }


def seed_demo_data(store_path: Path) -> list[Session]:
    """Overwrites store with realistic data from the last week."""
    if store_path.exists():
        store_path.unlink()
    
    demo_sessions = []
    now = datetime.now()
    
    # 7 days of data
    seeds = [
        ("Python", 45, "focused", "Day 7 ago"),
        ("Algorithms", 90, "confident", "Day 6 ago"),
        ("System Design", 30, "tired", "Day 5 ago"),
        ("Python", 60, "focused", "Day 4 ago"),
        ("Web Dev", 120, "neutral", "Day 3 ago"),
        ("Algorithms", 45, "distracted", "Day 2 ago"),
        ("Python", 15, "tired", "Day 1 ago"),
        ("Web Dev", 10, "focused", "Today starter"),
    ]
    
    for i, (topic, mins, mood, note) in enumerate(seeds):
        days_ago = 7 - i
        ts = (now - timedelta(days=days_ago)).isoformat()
        demo_sessions.append(
            add_session(store_path, topic, mins, mood, note, created_at=ts)
        )
        
    return demo_sessions