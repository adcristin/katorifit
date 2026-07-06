"""Simple typed models shared across modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    id: str
    email: str


@dataclass
class Profile:
    user_id: str
    name: str = ""
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: str = ""
    gender: str = "Male"
    activity_label: str = "Sedentary / College Student (BMR x 1.2)"
    calorie_target_override: Optional[float] = None


@dataclass
class Workout:
    id: int
    user_id: str
    date: str          # ISO date
    type: str
    duration_min: int
    calories: int
    notes: str = ""


@dataclass
class DailyLog:
    """One row per user per day — Hand & Katori food log, fasting
    checkpoints, and activity/circuit tracking."""
    user_id: str
    log_date: str  # ISO date
    roti: int = 0
    protein: int = 0
    katori: int = 0
    eggs: int = 0
    fats: int = 0
    steps: int = 0
    walk1_done: bool = False
    walk2_done: bool = False
    circuit_rounds: int = 0
    hydration_done: bool = False
    meal1_done: bool = False
    meal2_done: bool = False
    anchor_done: bool = False
    fast_locked: bool = False
    cheat_mode: bool = False


@dataclass
class WeightEntry:
    user_id: str
    log_date: str  # ISO date
    weight_kg: float
