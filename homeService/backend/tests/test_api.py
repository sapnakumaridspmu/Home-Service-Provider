import hashlib, hmac, json
from datetime import date, timedelta

import mongomock
import pytest

from homeservice import create_app, gateway

WEBHOOK_SECRET = "whsec_test"


@pytest.fixture()
def app():
    app = create_app(
        {"TESTING": True, "SECRET_KEY": "test-secret", "MONGO_DB": "t", "ADMIN_EMAIL": "admin@x.com",
         "ADMIN_PASSWORD": "AdminPass123", "RAZORPAY_KEY_ID": "", "RAZORPAY_KEY_SECRET": "",
         "RAZORPAY_WEBHOOK_SECRET": WEBHOOK_SECRET, "PLATFORM_FEE_PERCENT": 20},
        mongo_client=mongomock.MongoClient(),
    )
    return app


@pytest.fixture()
def c(app):
    return app.test_client()


def H(tok):
    return {"Authorization": f"Bearer {tok}"}


def register(c, role="user", email="u@x.com", **kw):
    body = {"name": "Test Person", "email": email, "mobile": "9876543210", "password": "Password123", "role": role}
    body.update(kw)
    r = c.post("/api/auth/register", json=body)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["token"], r.get_json()["user"]


def login(c, email, pw):
    return c.post("/api/auth/login", json={"email": email, "password": pw}).get_json()["token"]


def service(c, slug="plumber"):
    return next(s for s in c.get("/api/services").get_json()["services"] if s["slug"] == slug)


def book(c, tok, slug="plumber"):
    s = service(c, slug)
    r = c.post("/api/bookings", headers=H(tok), json={
        "service_id": s["id"], "date": (date.today() + timedelta(days=2)).isoformat(),
        "slot": "09:00-11:00", "address": "12 Main Road, Lalpur", "city": "Ranchi"})
    assert r.status_code == 201, r.get_json()
    return r.get_json()["booking"]


def pay(c, tok, bid):
    o = c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": bid}).get_json()
    assert o["mode"] == "demo"
    r = c.post("/api/payments/demo-pay", headers=H(tok), json={"order_id": o["order_id"]})
    assert r.status_code == 200
    return o, r.get_json()["booking"]


def approved_provider(c, email="p@x.com", skills=("plumber",)):
    tok, u = register(c, "provider", email, skills=list(skills))
    adm = login(c, "admin@x.com", "AdminPass123")
    assert c.patch(f"/api/admin/users/{u['id']}", headers=H(adm), json={"approved": True}).status_code == 200
    return tok, u, adm


# ---------------- auth ----------------
def test_register_login_and_no_self_admin(c):
    register(c)
    assert c.post("/api/auth/register", json={"name": "A", "email": "u@x.com", "mobile": "9876543210", "password": "Password123"}).status_code == 409
    r = c.post("/api/auth/register", json={"name": "Evil", "email": "e@x.com", "mobile": "9876543210", "password": "Password123", "role": "admin"})
    assert r.status_code == 400
    assert "password" not in json.dumps(c.get("/api/auth/me", headers=H(login(c, "u@x.com", "Password123"))).get_json())
    assert c.post("/api/auth/login", json={"email": "u@x.com", "password": "nope"}).status_code == 401


def test_role_protection(c):
    utok, _ = register(c)
    assert c.get("/api/admin/stats").status_code == 401
    assert c.get("/api/admin/stats", headers=H(utok)).status_code == 403
    assert c.get("/api/provider/stats", headers=H(utok)).status_code == 403
    adm = login(c, "admin@x.com", "AdminPass123")
    assert c.get("/api/bookings", headers=H(adm)).status_code == 403


def test_password_reset_is_single_use(c, app):
    register(c)
    logs = []
    import homeservice.routes.auth_routes as ar
    ar.send_mail = lambda to, sub, body: logs.append(body)
    assert c.post("/api/auth/forgot", json={"email": "nobody@x.com"}).status_code == 200 and not logs
    c.post("/api/auth/forgot", json={"email": "u@x.com"})
    token = logs[0].split("token=")[1].split()[0]
    assert c.post("/api/auth/reset", json={"token": token, "password": "NewPassword1"}).status_code == 200
    assert login(c, "u@x.com", "NewPassword1")
    assert c.post("/api/auth/reset", json={"token": token, "password": "Another12345"}).status_code == 400
    assert c.post("/api/auth/reset", json={"token": "garbage", "password": "Another12345"}).status_code == 400


# ---------------- booking + payment ----------------
def test_price_is_server_side_and_validation(c):
    tok, _ = register(c)
    s = service(c)
    r = c.post("/api/bookings", headers=H(tok), json={"service_id": s["id"], "amount": 1, "date": (date.today() + timedelta(days=1)).isoformat(),
                                                       "slot": "09:00-11:00", "address": "12 Main Road, Lalpur"})
    assert r.get_json()["booking"]["amount"] == s["price"]
    bad = c.post("/api/bookings", headers=H(tok), json={"service_id": s["id"], "date": "2000-01-01", "slot": "09:00-11:00", "address": "12 Main Road, Lalpur"})
    assert bad.status_code == 400


def test_demo_payment_flow_and_verify_rejects_forged_signature(c):
    tok, _ = register(c)
    b = book(c, tok)
    o = c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": b["id"]}).get_json()
    assert o["amount"] == b["amount"] * 100
    forged = c.post("/api/payments/verify", headers=H(tok), json={"razorpay_order_id": o["order_id"], "razorpay_payment_id": "pay_x", "razorpay_signature": "bad"})
    assert forged.status_code == 400
    assert c.get(f"/api/bookings/{b['id']}", headers=H(tok)).get_json()["booking"]["payment_status"] == "Unpaid"
    with c.application.app_context():
        sig = gateway.sign(o["order_id"], "pay_real1")
    ok = c.post("/api/payments/verify", headers=H(tok), json={"razorpay_order_id": o["order_id"], "razorpay_payment_id": "pay_real1", "razorpay_signature": sig})
    assert ok.status_code == 200 and ok.get_json()["booking"]["payment_status"] == "Paid"
    assert c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": b["id"]}).status_code == 409


def test_cannot_pay_someone_elses_booking(c):
    t1, _ = register(c); t2, _ = register(c, email="o@x.com")
    b = book(c, t1)
    assert c.post("/api/payments/create-order", headers=H(t2), json={"booking_id": b["id"]}).status_code == 404


def test_webhook_signature_and_idempotency(c):
    tok, _ = register(c)
    b = book(c, tok)
    o = c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": b["id"]}).get_json()
    body = json.dumps({"event": "payment.captured", "payload": {"payment": {"entity": {"id": "pay_w1", "order_id": o["order_id"]}}}}).encode()
    assert c.post("/api/payments/webhook", data=body, headers={"X-Razorpay-Signature": "wrong"}).status_code == 400
    sig = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    for _ in range(2):  # delivered twice
        assert c.post("/api/payments/webhook", data=body, headers={"X-Razorpay-Signature": sig}).status_code == 200
    bk = c.get(f"/api/bookings/{b['id']}", headers=H(tok)).get_json()["booking"]
    assert bk["payment_status"] == "Paid" and sum(1 for h in bk["history"] if h["status"] == "Payment received") == 1


def test_duplicate_payment_from_second_order_is_refunded(c):
    tok, _ = register(c)
    b = book(c, tok)
    o1 = c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": b["id"]}).get_json()
    o2 = c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": b["id"]}).get_json()
    c.post("/api/payments/demo-pay", headers=H(tok), json={"order_id": o1["order_id"]})
    c.post("/api/payments/demo-pay", headers=H(tok), json={"order_id": o2["order_id"]})
    adm = login(c, "admin@x.com", "AdminPass123")
    statuses = sorted(p["status"] for p in c.get("/api/admin/payments", headers=H(adm)).get_json()["payments"])
    assert statuses == ["paid", "refunded"]


def test_demo_pay_disabled_in_production(app):
    app.config["APP_ENV"] = "production"
    c = app.test_client()
    tok, _ = register(c)
    b = book(c, tok)
    r = c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": b["id"]})
    assert r.status_code == 502  # gateway not configured -> refuses, never fakes success
    assert c.post("/api/payments/demo-pay", headers=H(tok), json={"order_id": "order_demo_x"}).status_code == 404


def test_cancel_paid_booking_refunds(c):
    tok, _ = register(c)
    b = book(c, tok); pay(c, tok, b["id"])
    r = c.post(f"/api/bookings/{b['id']}/cancel", headers=H(tok)).get_json()
    assert r["booking"]["status"] == "Cancelled" and r["booking"]["payment_status"] == "Refunded"
    assert c.post(f"/api/bookings/{b['id']}/cancel", headers=H(tok)).status_code == 409


# ---------------- provider workflow ----------------
def test_provider_needs_approval_and_only_sees_paid_matching_jobs(c):
    utok, _ = register(c)
    ptok, pu = register(c, "provider", "p@x.com", skills=["plumber"])
    assert c.get("/api/provider/jobs/available", headers=H(ptok)).status_code == 403
    adm = login(c, "admin@x.com", "AdminPass123")
    c.patch(f"/api/admin/users/{pu['id']}", headers=H(adm), json={"approved": True})
    unpaid = book(c, utok)
    paid = book(c, utok); pay(c, utok, paid["id"])
    elec = book(c, utok, "electrician"); pay(c, utok, elec["id"])
    jobs = c.get("/api/provider/jobs/available", headers=H(ptok)).get_json()["jobs"]
    assert [j["id"] for j in jobs] == [paid["id"]]
    assert jobs[0]["provider_earning"] == 400  # 500 - 20%
    assert not {"user_email", "user_name", "contact", "address", "landmark"} & set(jobs[0])
    assert jobs[0]["city"] == "Ranchi"
    accepted = c.post(f"/api/provider/jobs/{paid['id']}/accept", headers=H(ptok)).get_json()["job"]
    assert accepted["address"] and accepted["contact"]  # revealed after accepting
    paid = book(c, utok); pay(c, utok, paid["id"])
    assert c.post(f"/api/provider/jobs/{unpaid['id']}/accept", headers=H(ptok)).status_code == 409
    assert c.post(f"/api/provider/jobs/{elec['id']}/accept", headers=H(ptok)).status_code == 409


def test_only_one_provider_can_claim_and_full_lifecycle(c):
    utok, _ = register(c)
    p1, _, adm = approved_provider(c, "p1@x.com"); p2, _, _ = approved_provider(c, "p2@x.com")
    b = book(c, utok); pay(c, utok, b["id"])
    assert c.post(f"/api/provider/jobs/{b['id']}/accept", headers=H(p1)).status_code == 200
    assert c.post(f"/api/provider/jobs/{b['id']}/accept", headers=H(p2)).status_code == 409
    assert c.post(f"/api/provider/jobs/{b['id']}/status", headers=H(p2), json={"status": "Completed"}).status_code == 404
    assert c.post(f"/api/provider/jobs/{b['id']}/status", headers=H(p1), json={"status": "In Progress"}).status_code == 200
    assert c.post(f"/api/provider/jobs/{b['id']}/release", headers=H(p1)).status_code == 409  # already started
    assert c.post(f"/api/provider/jobs/{b['id']}/status", headers=H(p1), json={"status": "Completed"}).status_code == 200
    assert c.post(f"/api/provider/jobs/{b['id']}/status", headers=H(p1), json={"status": "In Progress"}).status_code == 409
    st = c.get("/api/provider/stats", headers=H(p1)).get_json()
    assert st["completed"] == 1 and st["earnings"] == 400
    a = c.get("/api/admin/stats", headers=H(adm)).get_json()
    assert a["revenue"] == 500 and a["platform_fees"] == 100 and a["by_status"]["Completed"] == 1
    assert c.post(f"/api/bookings/{b['id']}/cancel", headers=H(utok)).status_code == 409  # can't cancel a done job


def test_user_cancel_after_accept_frees_provider_view(c):
    utok, _ = register(c); p1, _, _ = approved_provider(c)
    b = book(c, utok); pay(c, utok, b["id"])
    c.post(f"/api/provider/jobs/{b['id']}/accept", headers=H(p1))
    assert c.post(f"/api/bookings/{b['id']}/cancel", headers=H(utok)).status_code == 200
    assert c.post(f"/api/provider/jobs/{b['id']}/status", headers=H(p1), json={"status": "In Progress"}).status_code == 409


# ---------------- admin ----------------
def test_admin_manages_users_bookings_services(c):
    utok, u = register(c); ptok, p, adm = approved_provider(c)
    b = book(c, utok); pay(c, utok, b["id"])
    r = c.patch(f"/api/admin/bookings/{b['id']}", headers=H(adm), json={"provider_id": p["id"]}).get_json()["booking"]
    assert r["status"] == "Accepted" and r["provider_name"] == "Test Person"
    r = c.patch(f"/api/admin/bookings/{b['id']}", headers=H(adm), json={"status": "Cancelled"}).get_json()
    assert r["booking"]["payment_status"] == "Refunded" and r["refund"]["ok"]
    # deactivate user -> token stops working immediately
    assert c.patch(f"/api/admin/users/{u['id']}", headers=H(adm), json={"is_active": False}).status_code == 200
    assert c.get("/api/bookings", headers=H(utok)).status_code == 401
    assert c.post("/api/auth/login", json={"email": "u@x.com", "password": "Password123"}).status_code == 403
    me = c.get("/api/auth/me", headers=H(adm)).get_json()["user"]
    assert c.patch(f"/api/admin/users/{me['id']}", headers=H(adm), json={"is_active": False}).status_code == 400
    # services
    new = c.post("/api/admin/services", headers=H(adm), json={"name": "Pest control", "price": 899, "description": "x"})
    assert new.status_code == 201 and new.get_json()["service"]["slug"] == "pest-control"
    sid = new.get_json()["service"]["id"]
    assert c.put(f"/api/admin/services/{sid}", headers=H(adm), json={"active": False}).get_json()["service"]["active"] is False
    assert "pest-control" not in [s["slug"] for s in c.get("/api/services").get_json()["services"]]
    assert c.post("/api/admin/services", headers=H(adm), json={"name": "X", "price": "abc"}).status_code == 400


# ---------------- real Razorpay path (HTTP mocked) ----------------
def test_razorpay_mode_sends_paise_and_refunds(app, monkeypatch):
    app.config.update({"RAZORPAY_KEY_ID": "rzp_test_abc", "RAZORPAY_KEY_SECRET": "sekret"})
    calls = []

    class R:
        status_code = 200
        def __init__(self, data): self._d = data
        def json(self): return self._d

    def fake_post(url, auth=None, json=None, timeout=None):
        calls.append((url, auth, json))
        return R({"id": "order_RZ1"} if url.endswith("/orders") else {"id": "rfnd_RZ1"})

    monkeypatch.setattr(gateway.requests, "post", fake_post)
    c = app.test_client()
    tok, _ = register(c)
    b = book(c, tok)  # plumber = 500
    o = c.post("/api/payments/create-order", headers=H(tok), json={"booking_id": b["id"]}).get_json()
    assert o["mode"] == "razorpay" and o["order_id"] == "order_RZ1" and o["key_id"] == "rzp_test_abc"
    url, auth, body = calls[0]
    assert url == "https://api.razorpay.com/v1/orders" and auth == ("rzp_test_abc", "sekret")
    assert body["amount"] == 50000 and body["currency"] == "INR"
    # demo endpoint must be closed once real keys exist
    assert c.post("/api/payments/demo-pay", headers=H(tok), json={"order_id": "order_RZ1"}).status_code == 404
    # signature per Razorpay spec: HMAC_SHA256(order_id|payment_id, key_secret)
    sig = hmac.new(b"sekret", b"order_RZ1|pay_RZ1", hashlib.sha256).hexdigest()
    ok = c.post("/api/payments/verify", headers=H(tok), json={"razorpay_order_id": "order_RZ1", "razorpay_payment_id": "pay_RZ1", "razorpay_signature": sig})
    assert ok.status_code == 200
    r = c.post(f"/api/bookings/{b['id']}/cancel", headers=H(tok)).get_json()
    assert r["booking"]["payment_status"] == "Refunded"
    url, auth, body = calls[-1]
    assert url == "https://api.razorpay.com/v1/payments/pay_RZ1/refund" and body["amount"] == 50000


def test_refund_failure_is_flagged_for_admin_retry(app, monkeypatch):
    c = app.test_client()
    tok, _ = register(c)
    b = book(c, tok); pay(c, tok, b["id"])
    monkeypatch.setattr(gateway, "refund", lambda *a, **k: (_ for _ in ()).throw(gateway.GatewayError("gateway down")))
    r = c.post(f"/api/bookings/{b['id']}/cancel", headers=H(tok)).get_json()
    assert r["booking"]["payment_status"] == "Refund Pending" and r["refund"]["ok"] is False
    adm = login(c, "admin@x.com", "AdminPass123")
    monkeypatch.undo()
    assert c.post(f"/api/admin/bookings/{b['id']}/refund", headers=H(adm)).get_json()["booking"]["payment_status"] == "Refunded"


def test_production_refuses_weak_secret():
    with pytest.raises(RuntimeError):
        create_app({"APP_ENV": "production", "SECRET_KEY": "short"}, mongo_client=mongomock.MongoClient())
