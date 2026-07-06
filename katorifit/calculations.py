"""Mifflin-St Jeor BMR/TDEE math and Hand & Katori portion-unit constants."""
from __future__ import annotations

ACTIVITY_MULTIPLIERS = {
    "Sedentary / College Student (BMR x 1.2)": 1.2,
    "Lightly Active (BMR x 1.375)": 1.375,
    "Moderately Active (BMR x 1.55)": 1.55,
    "Very Active (BMR x 1.725)": 1.725,
}

CAL_PER_UNIT = {"roti": 90, "protein": 200, "katori": 30, "eggs": 70, "fats": 45}


def calc_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    if gender == "Male":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161


def calc_tdee(bmr: float, activity_label: str) -> float:
    return bmr * ACTIVITY_MULTIPLIERS.get(activity_label, 1.2)


def calc_fat_loss_target(tdee: float, deficit: int = 500) -> float:
    return tdee - deficit


def calories_from_log(log) -> float:
    """Accepts a DailyLog instance or a dict with the same field names."""
    get = (lambda k: getattr(log, k)) if not isinstance(log, dict) else (lambda k: log.get(k, 0))
    return sum(get(k) * cal for k, cal in CAL_PER_UNIT.items())


MYTH_TIPS = [
    ("🍯 Sugar Warning", "Jaggery and honey cause the exact same insulin "
     "spikes and facial bloating as white sugar. Stick to stevia or dark "
     "chocolate!"),
    ("🥔 The Potato Rule", "Substitute potatoes in your traditional gravies "
     "with carrots or raw papaya to save ~150 calories instantly."),
    ("🍚 The Rice Refill", "A second helping of rice adds up faster than a "
     "second roti — rice is denser in calories per katori than you'd think."),
    ("🥛 Milk Math", "Full-cream milk chai adds ~60 kcal a cup. Switch to "
     "toned/skim milk and save ~200 kcal across 3-4 cups a day."),
]
