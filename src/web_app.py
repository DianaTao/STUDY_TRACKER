"""Flask web app for Study Quest — a gamified study tracker."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from src import quest_engine, session_store

_BASE = Path(__file__).parent.parent
app = Flask(
    __name__,
    template_folder=str(_BASE / "templates"),
    static_folder=str(_BASE / "static"),
)

STORE_PATH = Path(os.environ.get("STUDY_TRACKER_STORE", Path.home() / ".study_tracker" / "sessions.json"))
DAILY_GOAL = int(os.environ.get("STUDY_TRACKER_DAILY_GOAL", "120"))


def _dashboard_stats(sessions: list[dict]) -> dict:
    today = datetime.now(timezone.utc).date()
    today_minutes = sum(
        s["minutes"]
        for s in sessions
        if datetime.fromisoformat(s["created_at"]).astimezone(timezone.utc).date() == today
    )

    # Streak: consecutive days ending today with at least one session
    session_dates = sorted({
        datetime.fromisoformat(s["created_at"]).astimezone(timezone.utc).date()
        for s in sessions
    }, reverse=True)
    streak = 0
    check = today
    for d in session_dates:
        if d == check:
            streak += 1
            check -= timedelta(days=1)
        elif d < check:
            break

    summary = session_store.summarize(STORE_PATH)
    favorite_topic = (
        max(summary["by_topic"], key=lambda t: summary["by_topic"][t])
        if summary["by_topic"] else None
    )

    achievements: list[str] = []
    if summary["total_sessions"] >= 1:
        achievements.append("🎉 First Session")
    if summary["total_minutes"] >= 60:
        achievements.append("⏱️ 1 Hour Club")
    if summary["total_minutes"] >= 300:
        achievements.append("🔥 5 Hour Grind")
    if streak >= 3:
        achievements.append("📅 3-Day Streak")
    if streak >= 7:
        achievements.append("🏆 Week Warrior")

    progress_pct = min(100, int(today_minutes / DAILY_GOAL * 100)) if DAILY_GOAL else 0

    return {
        "today_minutes": today_minutes,
        "streak": streak,
        "favorite_topic": favorite_topic,
        "achievements": achievements,
        "progress_pct": progress_pct,
        "summary": summary,
    }


@app.route("/")
def dashboard():
    sessions = session_store.list_sessions(STORE_PATH)
    stats = _dashboard_stats(sessions)
    quests = quest_engine.generate_daily_quests(sessions, DAILY_GOAL)
    recent = list(reversed(sessions))[:5]
    return render_template(
        "index.html",
        **stats,
        quests=quests,
        recent_sessions=recent,
        daily_goal=DAILY_GOAL,
    )


@app.route("/sessions")
def sessions_list():
    sessions = list(reversed(session_store.list_sessions(STORE_PATH)))
    return render_template("sessions.html", sessions=sessions)


@app.route("/sessions/add", methods=["GET"])
def add_session_form():
    return render_template("add_session.html", error=None)


@app.route("/sessions/add", methods=["POST"])
def add_session_submit():
    topic = request.form.get("topic", "").strip()
    minutes_raw = request.form.get("minutes", "").strip()
    mood = request.form.get("mood", "neutral")
    notes = request.form.get("notes", "").strip() or None

    try:
        minutes = int(minutes_raw)
        session_store.add_session(STORE_PATH, topic, minutes, mood=mood, notes=notes)
    except (ValueError, TypeError) as exc:
        return render_template("add_session.html", error=str(exc)), 400

    return redirect(url_for("dashboard"))


@app.route("/sessions/delete/<int:session_id>", methods=["POST"])
def delete_session(session_id: int):
    session_store.delete_session(STORE_PATH, session_id)
    return redirect(url_for("sessions_list"))


@app.route("/demo-reset", methods=["POST"])
def demo_reset():
    session_store.seed_demo_data(STORE_PATH)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
