# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"Spendly" — a Flask expense tracker built as a step-by-step teaching project. Much of the code is intentionally stubbed; placeholders say which "Step" implements them. The git repo and project root is `expense-tracker/expense-tracker/` (the outer `expense-tracker/` folder and `__MACOSX/` are zip-extraction leftovers).

## Commands

```
python -m venv venv && venv\Scripts\activate    # Windows; a venv/ already exists (Python 3.12)
pip install -r requirements.txt                 # flask, werkzeug, pytest, pytest-flask
python app.py                                   # dev server on http://localhost:5001 (debug=True)
pytest                                          # run all tests
pytest path/to/test_file.py::test_name          # run a single test
```

No tests, linter, or build step exist yet.

## Architecture

- `app.py` — single Flask app with all routes. Implemented: `/` (landing), `/login`, `/register`, `/terms`, `/privacy` (these only render templates; `GET` only, the auth forms POST to `/login` and `/register` but no POST handling exists yet). Placeholder routes returning plain strings: `/logout` (Step 3), `/profile` (Step 4), `/expenses/add` (Step 7), `/expenses/<id>/edit` (Step 8), `/expenses/<id>/delete` (Step 9).
- `database/db.py` — empty stub (Step 1). Intended to provide `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), and `seed_db()` (sample data). The SQLite file is `expense_tracker.db` (gitignored).
- `templates/` — Jinja templates all extending `base.html` (blocks: `title`, `content`). Auth templates expect an optional `error` variable.
- `static/css/` — `style.css` (shared) and `landing.css`; `static/js/main.js` is an empty stub.
