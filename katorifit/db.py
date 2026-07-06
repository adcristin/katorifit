"""SQLite persistence, scoped by Supabase user id."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator, List, Optional

from .models import DailyLog, Profile, WeightEntry, Workout

DB_PATH = Path(os.environ.get("KATORIFIT_DB", "data/katorifit.db"))

_DAILY_LOG_FIELDS = [
    "roti", "protein", "katori", "eggs", "fats", "steps",
    "walk1_done", "walk2_done", "circuit_rounds", "hydration_done",
    "meal1_done", "meal2_done", "anchor_done", "fast_locked", "cheat_mode",
]


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def _cursor() -> Iterator[sqlite3.Cursor]:
    conn = _connect()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                user_id     TEXT PRIMARY KEY,
                name        TEXT DEFAULT '',
                age         INTEGER,
                height_cm   REAL,
                weight_kg   REAL,
                goal        TEXT DEFAULT ''
            )
            """
        )
        # Migration: add newer profile columns if this DB predates them.
        existing_cols = {row["name"] for row in cur.execute("PRAGMA table_info(profiles)").fetchall()}
        for col, ddl in [
            ("gender", "TEXT DEFAULT 'Male'"),
            ("activity_label", "TEXT DEFAULT 'Sedentary / College Student (BMR x 1.2)'"),
            ("calorie_target_override", "REAL"),
        ]:
            if col not in existing_cols:
                cur.execute(f"ALTER TABLE profiles ADD COLUMN {col} {ddl}")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       TEXT NOT NULL,
                date          TEXT NOT NULL,
                type          TEXT NOT NULL,
                duration_min  INTEGER NOT NULL,
                calories      INTEGER NOT NULL,
                notes         TEXT DEFAULT ''
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS ix_workouts_user_date ON workouts(user_id, date)")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_logs (
                user_id         TEXT NOT NULL,
                log_date        TEXT NOT NULL,
                roti            INTEGER DEFAULT 0,
                protein         INTEGER DEFAULT 0,
                katori          INTEGER DEFAULT 0,
                eggs            INTEGER DEFAULT 0,
                fats            INTEGER DEFAULT 0,
                steps           INTEGER DEFAULT 0,
                walk1_done      INTEGER DEFAULT 0,
                walk2_done      INTEGER DEFAULT 0,
                circuit_rounds  INTEGER DEFAULT 0,
                hydration_done  INTEGER DEFAULT 0,
                meal1_done      INTEGER DEFAULT 0,
                meal2_done      INTEGER DEFAULT 0,
                anchor_done     INTEGER DEFAULT 0,
                fast_locked     INTEGER DEFAULT 0,
                cheat_mode      INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, log_date)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS weight_history (
                user_id   TEXT NOT NULL,
                log_date  TEXT NOT NULL,
                weight_kg REAL,
                PRIMARY KEY (user_id, log_date)
            )
            """
        )


# ---------- Profiles ----------

def get_profile(user_id: str) -> Profile:
    with _cursor() as cur:
        row = cur.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        return Profile(user_id=user_id)
    keys = row.keys()
    return Profile(
        user_id=row["user_id"],
        name=row["name"] or "",
        age=row["age"],
        height_cm=row["height_cm"],
        weight_kg=row["weight_kg"],
        goal=row["goal"] or "",
        gender=(row["gender"] if "gender" in keys and row["gender"] else "Male"),
        activity_label=(
            row["activity_label"] if "activity_label" in keys and row["activity_label"]
            else "Sedentary / College Student (BMR x 1.2)"
        ),
        calorie_target_override=(row["calorie_target_override"] if "calorie_target_override" in keys else None),
    )


def upsert_profile(profile: Profile) -> None:
    with _cursor() as cur:
        cur.execute(
            """
            INSERT INTO profiles (user_id, name, age, height_cm, weight_kg, goal,
                                   gender, activity_label, calorie_target_override)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name=excluded.name,
                age=excluded.age,
                height_cm=excluded.height_cm,
                weight_kg=excluded.weight_kg,
                goal=excluded.goal,
                gender=excluded.gender,
                activity_label=excluded.activity_label,
                calorie_target_override=excluded.calorie_target_override
            """,
            (
                profile.user_id,
                profile.name,
                profile.age,
                profile.height_cm,
                profile.weight_kg,
                profile.goal,
                profile.gender,
                profile.activity_label,
                profile.calorie_target_override,
            ),
        )
    if profile.weight_kg:
        save_weight(profile.user_id, date.today().isoformat(), profile.weight_kg)


# ---------- Workouts ----------

def add_workout(user_id: str, date: str, type_: str, duration_min: int, calories: int, notes: str = "") -> None:
    with _cursor() as cur:
        cur.execute(
            "INSERT INTO workouts (user_id, date, type, duration_min, calories, notes) VALUES (?,?,?,?,?,?)",
            (user_id, date, type_, duration_min, calories, notes),
        )


def list_workouts(user_id: str, limit: Optional[int] = None) -> List[Workout]:
    q = "SELECT * FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC"
    params: tuple = (user_id,)
    if limit:
        q += " LIMIT ?"
        params = (user_id, limit)
    with _cursor() as cur:
        rows = cur.execute(q, params).fetchall()
    return [
        Workout(
            id=r["id"],
            user_id=r["user_id"],
            date=r["date"],
            type=r["type"],
            duration_min=r["duration_min"],
            calories=r["calories"],
            notes=r["notes"] or "",
        )
        for r in rows
    ]


def delete_workout(user_id: str, workout_id: int) -> None:
    with _cursor() as cur:
        cur.execute("DELETE FROM workouts WHERE id = ? AND user_id = ?", (workout_id, user_id))


# ---------- Daily logs (Hand & Katori food, fasting, activity) ----------

def _row_to_daily_log(row: sqlite3.Row) -> DailyLog:
    return DailyLog(
        user_id=row["user_id"],
        log_date=row["log_date"],
        roti=row["roti"], protein=row["protein"], katori=row["katori"],
        eggs=row["eggs"], fats=row["fats"], steps=row["steps"],
        walk1_done=bool(row["walk1_done"]), walk2_done=bool(row["walk2_done"]),
        circuit_rounds=row["circuit_rounds"], hydration_done=bool(row["hydration_done"]),
        meal1_done=bool(row["meal1_done"]), meal2_done=bool(row["meal2_done"]),
        anchor_done=bool(row["anchor_done"]), fast_locked=bool(row["fast_locked"]),
        cheat_mode=bool(row["cheat_mode"]),
    )


def get_log(user_id: str, log_date: str) -> DailyLog:
    with _cursor() as cur:
        row = cur.execute(
            "SELECT * FROM daily_logs WHERE user_id = ? AND log_date = ?", (user_id, log_date)
        ).fetchone()
    if row:
        return _row_to_daily_log(row)
    return DailyLog(user_id=user_id, log_date=log_date)


def save_log(user_id: str, log_date: str, **fields) -> None:
    current = get_log(user_id, log_date)
    for k, v in fields.items():
        setattr(current, k, v)
    cols = ["user_id", "log_date"] + _DAILY_LOG_FIELDS
    values = [int(getattr(current, c)) if isinstance(getattr(current, c), bool) else getattr(current, c)
              for c in cols]
    placeholders = ", ".join("?" for _ in cols)
    updates = ", ".join(f"{c}=excluded.{c}" for c in _DAILY_LOG_FIELDS)
    with _cursor() as cur:
        cur.execute(
            f"INSERT INTO daily_logs ({', '.join(cols)}) VALUES ({placeholders}) "
            f"ON CONFLICT(user_id, log_date) DO UPDATE SET {updates}",
            values,
        )


def get_log_history(user_id: str, n_days: int = 30) -> List[DailyLog]:
    start = (date.today() - timedelta(days=n_days - 1)).isoformat()
    with _cursor() as cur:
        rows = cur.execute(
            "SELECT * FROM daily_logs WHERE user_id = ? AND log_date >= ? ORDER BY log_date ASC",
            (user_id, start),
        ).fetchall()
    return [_row_to_daily_log(r) for r in rows]


# ---------- Weight history ----------

def save_weight(user_id: str, log_date: str, weight_kg: float) -> None:
    with _cursor() as cur:
        cur.execute(
            """
            INSERT INTO weight_history (user_id, log_date, weight_kg) VALUES (?, ?, ?)
            ON CONFLICT(user_id, log_date) DO UPDATE SET weight_kg=excluded.weight_kg
            """,
            (user_id, log_date, weight_kg),
        )


def get_weight_history(user_id: str, n_days: int = 90) -> List[WeightEntry]:
    start = (date.today() - timedelta(days=n_days - 1)).isoformat()
    with _cursor() as cur:
        rows = cur.execute(
            "SELECT * FROM weight_history WHERE user_id = ? AND log_date >= ? ORDER BY log_date ASC",
            (user_id, start),
        ).fetchall()
    return [WeightEntry(user_id=r["user_id"], log_date=r["log_date"], weight_kg=r["weight_kg"]) for r in rows]


# ---------- Streaks & aggregates ----------

def compute_streak(user_id: str, target_kcal: float) -> tuple:
    """Returns (current_streak, best_streak) of consecutive days where logged
    calories were >0 and at/under target, walking backward from today."""
    from .calculations import calories_from_log

    history = {h.log_date: h for h in get_log_history(user_id, 90)}
    current, best, running = 0, 0, 0
    day = date.today()
    counting_current = True
    for _ in range(90):
        d = day.isoformat()
        log = history.get(d)
        cals = calories_from_log(log) if log else 0
        hit = 0 < cals <= target_kcal
        if hit:
            running += 1
            if counting_current:
                current = running
            best = max(best, running)
        else:
            running = 0
            if counting_current and d != date.today().isoformat():
                counting_current = False
        day -= timedelta(days=1)
    return current, best


def total_steps(user_id: str, n_days: int = 90) -> int:
    return sum(h.steps for h in get_log_history(user_id, n_days))


def katori_days_hit(user_id: str, n_days: int = 90) -> int:
    return sum(1 for h in get_log_history(user_id, n_days) if h.katori >= 2)
