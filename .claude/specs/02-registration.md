# Spec: Registration

## Overview
Turn the existing `GET /register` page into a working sign-up flow. A visitor submits name, email and password; the server validates the input, hashes the password with werkzeug, creates a row in `users`, and redirects to the login page. This is the first step that writes user-supplied data, and it is the prerequisite for login (Step 3) and every logged-in feature that follows.

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`, `init_db()`).

## Routes
- `GET /register` — render the registration form (already implemented, unchanged) — public
- `POST /register` — validate the form, create the user, redirect to `/login` on success; re-render `register.html` with an `error` message on failure — public

Both methods are handled by the single existing `register()` view via `methods=["GET", "POST"]`.

## Database changes
No database changes. The existing `users` table already has `name`, `email` (UNIQUE), `password_hash` and `created_at`.

New helper functions in `database/db.py` (DB logic must not live in routes):
- `get_user_by_email(email)` — returns the matching `sqlite3.Row` or `None`.
- `create_user(name, email, password_hash)` — inserts the user with a parameterised query, commits, returns the new `id`. Lets `sqlite3.IntegrityError` propagate so the route can handle a duplicate email race.

## Templates
- **Create:** none
- **Modify:** `templates/register.html`
  - Change `action="/register"` to `action="{{ url_for('register') }}"` (no hardcoded URLs).
  - Re-populate the `name` and `email` inputs with the submitted values after a failed submit (never the password).
  - Add `minlength="8"` to the password input to match the placeholder.

## Files to change
- `app.py` — accept POST on `/register`, add validation and redirect; import `redirect`, `url_for`, `request`, `abort` as needed and `generate_password_hash` from `werkzeug.security`.
- `database/db.py` — add `get_user_by_email()` and `create_user()`.
- `templates/register.html` — changes listed above.

## Files to create
- None

## New dependencies
No new dependencies (`werkzeug` is already installed with Flask).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`); never store or log the plain password
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for()` for every internal link and form action
- Route function stays thin: read form, validate, call db helpers, redirect or render
- Validation (server-side, in this order), each failure re-renders `register.html` with HTTP 400 and an `error` string:
  - name, email and password are all present after `strip()` (password is not stripped)
  - email contains an `@` and a `.` after it, and is lowercased before storing/lookup
  - password is at least 8 characters
  - email is not already registered (`get_user_by_email`); also catch `sqlite3.IntegrityError` on insert for the race case
- On success redirect to `url_for('login')`; do not log the user in (sessions arrive in Step 3)
- Do not implement any other stub route (`/logout`, `/profile`, etc.)

## Definition of done
- [ ] `python app.py` starts on port 5001 without errors
- [ ] Visiting `/register` shows the form; the form posts to `/register` via `url_for`
- [ ] Submitting valid details creates a row in `users` and redirects to `/login`
- [ ] The stored `password_hash` is a werkzeug hash, not the plain password
- [ ] Submitting an already-registered email re-renders the form with an error and does not create a second row
- [ ] Email matching is case-insensitive (`A@x.com` after `a@x.com` is rejected) and emails are stored lowercase
- [ ] A password shorter than 8 characters is rejected with an error
- [ ] Blank/whitespace-only name or email is rejected with an error
- [ ] After a failed submit, name and email stay filled in and the password field is empty
- [ ] Failed submissions return HTTP 400; successful ones return a 302 to `/login`
- [ ] No SQL string formatting and no DB code inside `app.py`
