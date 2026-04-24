"""
A small library for tracking and summarizing study sessions using a JSON-backed store.
"""

import json
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class Session(TypedDict):
    id: int
    topic: str
    minutes: int
    created_at: str


class Summary(TypedDict):
    total_sessions: int
    total_minutes: int
    by_topic: dict[str, int]


@dataclass(frozen=True)
class _SessionRecord:
    id: int
    topic: str
    minutes: int
    created_at: str


def _read_data(store_path: Path) -> list[Session]:
    if not store_path.exists():
        return []
    try:
        with store_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def _write_data(store_path: Path, sessions: list[Session]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Atomic write pattern
    with tempfile.NamedTemporaryFile("w", dir=store_path.parent, delete=False, encoding="utf-8") as tf:
        json.dump(sessions, tf, ensure_ascii=False, indent=2)
        temp_name = Path(tf.name)
    
    try:
        temp_name.replace(store_path)
    except Exception:
        temp_name.unlink(missing_ok=True)
        raise


def add_session(store_path: Path, topic: str, minutes: int) -> Session:
    """
    Appends a new study session to the store.
    
    Raises:
        ValueError: If topic is empty or minutes are non-positive.
    """
    if not topic.strip():
        raise ValueError("Topic cannot be empty.")
    if minutes <= 0:
        raise ValueError("Minutes must be a positive integer.")

    sessions = _read_data(store_path)
    
    new_id = max((s["id"] for s in sessions), default=0) + 1
    new_session = _SessionRecord(
        id=new_id,
        topic=topic.strip(),
        minutes=minutes,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    record = asdict(new_session)
    sessions.append(record)
    _write_data(store_path, sessions)
    
    return record


def list_sessions(store_path: Path) -> list[Session]:
    """
    Returns all recorded sessions sorted by creation time (ascending).
    """
    sessions = _read_data(store_path)
    return sorted(sessions, key=lambda x: x["created_at"])


def summarize(store_path: Path) -> Summary:
    """
    Calculates summary statistics for all sessions in the store.
    """
    sessions = _read_data(store_path)
    
    total_minutes = 0
    by_topic: dict[str, int] = {}
    
    for s in sessions:
        topic = s["topic"]
        mins = s["minutes"]
        total_minutes += mins
        by_topic[topic] = by_topic.get(topic, 0) + mins
        
    return {
        "total_sessions": len(sessions),
        "total_minutes": total_minutes,
        "by_topic": by_topic
    }