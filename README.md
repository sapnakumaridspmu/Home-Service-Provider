# 🏠 Home Service Provider

A Flask-based home service booking app (Urban Company style) — customers can browse
services (AC repair, plumbing, electrician, salon, etc.), sign up, log in, and book a
service. Admins can sign up, log in, manage their profile, and view all bookings.

## What changed from the original upload

The original project would not run or deploy as-is. Fixes made:

- **Database**: swapped hardcoded local MySQL (`localhost`, no password) for **SQLite**,
  so it runs anywhere with zero external setup — no database server needed on Render.
- **Missing routes**: `/card3` through `/card8` (Electrician, Plumber, PC Repair, Salon,
  Mechanics, Kitchen Cleanup) were linked from the homepage but didn't exist → 404s. Added.
- **Wrong content**: every service page from card2–card8 displayed "AC repairing" as the
  heading (copy‑paste leftover). Fixed each to show its real service and image.
- **Booking form bug**: the customer's name was read from the URL query string instead of
  the submitted form, so it was always saved blank. Fixed.
- **Broken redirect**: an invalid `url_for('org_login')` (route didn't exist) would crash
  the app when an unauthenticated user tried to book. Fixed to redirect to login.
- **Admin profile crash**: the form submits a `city` field that the backend never read,
  causing a `TypeError` on every profile update. Fixed.
- **Dead code removed**: `app2.py` imported a module that doesn't exist anywhere in the
  project and would crash if run; the whole project was also duplicated inside itself in
  the zip, plus a 92MB `venv` and `.git` folder were bundled in. All removed.
- **Missing view**: the admin nav bar linked to `/view_booking` with no route or template
  behind it. Added both so admins can see all customer bookings.
- **Forgot Password**: both login pages linked to a page that didn't exist. Added a working
  reset flow (verifies email + mobile match an account, then sets a new password) for both
  users and admins — no email/SMTP server required.
- **My Bookings on profile page**: users could book a service but had no way to see their
  booking history. Added a bookings table to the profile page.
- **Insecure passwords**: passwords were hashed with MD5 (broken, not suitable for real use).
  Replaced with `werkzeug.security`'s salted password hashing (scrypt).
- **Booking status workflow**: bookings previously had no lifecycle. Added a `status` column
  (`Pending → Accepted/Completed/Cancelled`). Admins can update a booking's status from
  `/view_booking`; users can cancel their own booking only while it's still Pending.
- Added `requirements.txt`, `Procfile`, and a startup DB init (with automatic migration for
  older SQLite files) so it's deploy-ready.

## Tech stack

- **Backend**: Python, Flask
- **Database**: SQLite (via Python's built-in `sqlite3`)
- **Auth**: Salted password hashing via `werkzeug.security`
- **Frontend**: HTML, CSS, Bootstrap, vanilla JS

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`.

## Deploy on Render

1. Push this folder to a GitHub repo.
2. On Render: **New → Web Service**, connect the repo.
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (already in `Procfile`, Render picks it up
     automatically)
4. Add an environment variable **`SECRET_KEY`** with any random string (used to sign
   Flask sessions). If you skip this, the app still runs with a built-in default — just
   change it before using this for anything real.
5. Deploy. Render gives your app a public URL.

Note: Render's free tier has an ephemeral filesystem, so the SQLite file resets on
redeploy/restart. That's fine for a demo — if you need bookings/users to persist
long-term, swap to Render's managed Postgres later (the `db.py` module is the only
place that would need to change).

## Project structure

```text
homeService/
│
├── static/            # CSS, JS, images (Bootstrap-based template)
├── templates/          # Jinja2 HTML templates
│
├── app.py              # All routes
├── db.py               # SQLite connection + schema setup
├── user.py             # User signup/login/profile/booking queries
├── admin.py             # Admin signup/login/profile queries
├── encryption.py        # Password hashing (MD5)
├── validation.py         # Simple form validation helpers
├── requirements.txt
├── Procfile
└── .gitignore
```
