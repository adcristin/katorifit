# KatoriFit 🏃🥗

A minimal, cross-device fitness **and portion-control fat-loss tracker** built
with **Python + Streamlit**. Sign in with Supabase, log workouts *and* meals,
follow a 16:8 fasting timeline, track steps/circuits, and view long-term
progress — all stored per-user in SQLite. Installs as a home-screen app on
phone and desktop (PWA).

## Features

**Account & sync**
- Supabase email/password auth (BYO Supabase project)
- Per-user SQLite persistence — every table is scoped by `user_id`, so
  multiple people can use the same deployment without seeing each other's data
- PWA — installs as an app icon on iOS & Android

**Fitness tracking (original)**
- Free-form workout log (type, duration, calories, notes) with history
- Progress charts: minutes/calories per day, breakdown by workout type

**Portion-control fat-loss tracking (KatoriFit method)**
- User profile with BMR/TDEE calculator (Mifflin-St Jeor equation) and a
  configurable fat-loss calorie target (TDEE − 500 kcal, or your own override)
- **Hand & Katori food tracker** — log meals in portion units instead of
  grams: roti, hand-sized protein, carotenoid katori (veg), eggs, ghee —
  with sensible daily caps and a low-carotenoid warning
- **16:8 fasting timeline** — a late-rise daily schedule (10am wake → 8:30pm
  lock) with time-aware nudges
- **Activity tracker** — step counter, walk-alert checklist, 4-round
  bodyweight circuit tracker with a live plank timer
- **Streaks & achievement badges** (3/7-day streaks, carotenoid champ,
  century walker)
- **Progress page** — weight trend, 30-day calorie adherence, steps chart,
  weekly summary — alongside the original workout charts
- **Cheat Day** — one-tap Sunday cheat template gated behind a 10,000-step
  requirement
- Custom calorie-target override, CSV data export, and a "reset today's log"
  option, all on the Profile page

## 1. Setup

```bash
git clone <your repo>
cd katorifit
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # fill in SUPABASE_URL and SUPABASE_ANON_KEY
```

Get your Supabase URL + anon key from your Supabase project → Settings → API.
Enable **Email** auth in Authentication → Providers.

### Making your data permanent (recommended for any real deployment)
By default, this app stores logged data (profile, food/fasting/activity
logs, weight, workouts) in a local SQLite file at `data/katorifit.db`. That's
fine for local development, but most free hosts (including Streamlit
Community Cloud) have **ephemeral filesystems** — that file gets wiped on
every redeploy or restart. Your Supabase login always persists regardless;
it's your *logged data* that needs this extra step.

To make logged data permanent, point the app at your Supabase project's own
Postgres database instead:
1. In your Supabase project → **Settings → Database → Connection string → URI**
2. Add it to your `.env` as `DATABASE_URL=postgresql://...`
3. That's it — `init_db()` detects `DATABASE_URL` and switches to Postgres
   automatically, creating tables (and migrating any existing schema) on
   first run. Leave `DATABASE_URL` unset to keep using local SQLite.

## 2. Run — three ways

### Local
```bash
streamlit run app.py
```
Open http://localhost:8501. To reach it from your phone on the same Wi-Fi:
```bash
streamlit run app.py --server.address 0.0.0.0
```
then open `http://<your-computer-ip>:8501` on the phone.

### Streamlit Community Cloud (recommended for phone install)
1. Push this repo to GitHub.
2. Go to https://share.streamlit.io, connect the repo, pick `app.py`.
3. Add `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and (recommended) `DATABASE_URL`
   under **Secrets** — without `DATABASE_URL`, logged data resets whenever
   the app redeploys or sleeps from inactivity, since this host's filesystem
   is ephemeral.
4. You get a free HTTPS URL — needed for PWA install.

### Docker
```bash
docker build -t katorifit .
docker run -p 8501:8501 --env-file .env katorifit
```

## 3. Install as a phone app

Open the **deployed HTTPS URL** in your phone browser:

- **Android (Chrome):** tap the ⋮ menu → *Install app* / *Add to Home screen*.
- **iOS (Safari):** tap the Share icon → *Add to Home Screen*.

The doodle-runner icon will appear on your home screen and open in
standalone (no browser chrome). PWA install requires HTTPS, so it works on
the deployed URL but not on plain `http://LAN-IP:8501`.

## Project layout

```
katorifit/
├── app.py                  # Streamlit entry point / sidebar routing
├── requirements.txt
├── Dockerfile
├── .streamlit/config.toml
├── static/                 # PWA manifest + icons
└── katorifit/              # app package
    ├── auth.py             # Supabase auth
    ├── db.py               # SQLite persistence (profiles, workouts,
    │                        #   daily food/fasting/activity logs, weight)
    ├── models.py           # dataclasses: User, Profile, Workout,
    │                        #   DailyLog, WeightEntry
    ├── calculations.py     # BMR/TDEE math + Hand & Katori unit constants
    └── ui/
        ├── layout.py        # PWA head, CSS, sidebar nav
        ├── pages_home.py    # Dashboard: BMR/TDEE/target, streaks,
        │                    #   badges, tip banner, workout summary
        ├── pages_food.py    # Hand & Katori food tracker
        ├── pages_fasting.py # 16:8 timeline
        ├── pages_activity.py # Steps, walks, circuit, plank timer
        ├── pages_workout.py # Free-form workout log (original)
        ├── pages_cheat.py   # Sunday cheat-meal strategy
        ├── pages_progress.py # Weight/calorie/step charts + workout charts
        └── pages_profile.py # Profile, calorie target override, export, reset
```

## Note on existing databases
If you already have data in an earlier version of this app — either a local
`data/katorifit.db` or a Postgres database from before the `gender`/
`activity_label`/`calorie_target_override` fields existed — `init_db()`
migrates it in place on next run, adding the new profile columns with safe
defaults and creating the new `daily_logs`/`weight_history` tables. Your
existing profiles and workouts are preserved either way.

## License

MIT
