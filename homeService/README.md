# Home Service Provider — React + Flask + MongoDB + Razorpay

A marketplace where **service seekers** book home services, **service providers** accept and complete the jobs,
and an **admin** manages both sides. Signup asks whether you are a seeker or a provider.

```
backend/    Flask JSON API (JWT auth, MongoDB, Razorpay payments) + 17 automated tests
frontend/   React (Vite) responsive app: public site + three dashboards
```

## Roles

| Role | How they get in | What they can do |
|---|---|---|
| **Service seeker** | Signs up (Service seeker tab) | Browse services, book a date/slot, pay online, track, cancel (auto-refund), profile |
| **Service provider** | Signs up (Service provider tab), picks the services they offer. **Admin must approve** before they can take jobs | See paid jobs for their services, accept (first one wins), start, complete, release; earnings after platform fee |
| **Admin** | Created from `ADMIN_EMAIL` / `ADMIN_PASSWORD` in `.env` (never via public signup) | Overview + chart, approve/deactivate providers and seekers, view/assign/re-status any booking, refunds, all payments, edit services & prices |

## Run it locally

Requires Python 3.10+, Node 18+, MongoDB (local or Atlas).

```bash
# 1. backend
cd backend
python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # then edit MONGO_URI, ADMIN_* etc.
python manage.py demo                                    # optional: demo seeker + provider accounts
flask --app wsgi run --port 5000

# 2. frontend (new terminal)
cd frontend
npm install
npm run dev                                              # http://localhost:5173  (proxies /api to :5000)
```

Log in as `admin@example.com / ChangeMe123!` (or whatever you set). Demo accounts from `manage.py demo`:
`user@example.com` and `provider@example.com`, password `Password123!`.

Run the tests: `cd backend && pytest` (uses an in-memory Mongo, no database needed).

## Payments (Razorpay, INR)

Flow: seeker books → server creates a Razorpay **order** (price always read from the services collection, never
from the browser) → Razorpay Checkout opens → browser sends `order_id / payment_id / signature` to
`POST /api/payments/verify` → server checks the HMAC-SHA256 signature with your secret → booking becomes **Paid**
and only then becomes visible to providers.

1. Create a Razorpay account, then put `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `backend/.env` (use **test** keys first).
2. **Webhook (recommended, covers the case where the user closes the tab right after paying):** in the Razorpay
   dashboard add `https://YOUR-DOMAIN/api/payments/webhook`, events `payment.captured` and `order.paid`, and put the
   secret you choose in `RAZORPAY_WEBHOOK_SECRET`.
3. Keep **auto-capture** on in Razorpay settings — refunds only work on captured payments.

Also handled: duplicate/late payments are refunded automatically, cancellations refund automatically, and a failed
refund is flagged "Refund Pending" so the admin can retry it from Bookings.

**Demo mode:** with no Razorpay keys and `APP_ENV=development`, a fake checkout dialog is used so you can try the whole
flow. It cannot be used in production: with `APP_ENV=production` and no keys, payments refuse to run.

## Deploy (single service, e.g. Render)

Build command: `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build`
Start command: `cd backend && gunicorn wsgi:app`  (Flask serves the built `frontend/dist`)
Env: `APP_ENV=production`, `SECRET_KEY` (32+ random chars), `MONGO_URI` (Atlas), `FRONTEND_URL` (your site URL),
Razorpay keys, `ADMIN_EMAIL`, `ADMIN_PASSWORD`. The app refuses to start in production with a weak `SECRET_KEY`.

## API summary (all under `/api`)

`auth/` register · login · me · password · forgot · reset — `services` — `bookings` (seeker) —
`payments/` create-order · verify · webhook — `provider/` stats · jobs/available · jobs · jobs/:id/accept|release|status —
`admin/` stats · users · bookings · payments · services

## Things you should know

- **This replaces the old Jinja/Bootstrap pages.** The data model changed (one `users` collection with a `role`,
  plus `services`, `bookings`, `payments`), so old `user`/`admin`/`booking` collections are not read. Old password
  hashes use the same werkzeug format, so a small migration script would be easy if you need one.
- **Public admin signup was removed** (anyone could make themselves an admin). Admins come from `.env`.
- **Forgot password** now uses an emailed one-hour, single-use link instead of "email + mobile number" (which
  anyone who knows both could abuse). Without SMTP settings the link is printed in the server console.
- **Placeholder prices:** AC ₹2000, PC ₹3500, Salon ₹1000, Plumber ₹500, Painting ₹1000 came from your booking form.
  Electrician ₹600, Vehicle mechanic ₹1500 and Kitchen cleaning ₹1200 are made up — change them in Admin → Services.
- **The service photos are iStock previews with visible watermarks** (they were in your original project). Replace the
  files in `frontend/public/img/` with licensed images before launching publicly.
- Platform fee is `PLATFORM_FEE_PERCENT` (default 15%). Provider earnings are tracked, but **paying providers out is
  not automated** (would need Razorpay Route/X).
- Not included: rate limiting, ratings/reviews, SMS/email booking notifications, live provider location.
