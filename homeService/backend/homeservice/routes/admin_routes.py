import re
from datetime import timedelta

from flask import Blueprint, request, g, current_app
from pymongo.errors import DuplicateKeyError

from ..auth import auth_required
from ..db import db
from ..payments_core import refund_booking
from ..utils import err, ser, oid, text, now, hist, today_ist

bp = Blueprint("admin", __name__, url_prefix="/api/admin")
STATUSES = ["Pending", "Accepted", "In Progress", "Completed", "Cancelled"]


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


@bp.get("/stats")
@auth_required("admin")
def stats():
    paid = list(db.bookings.find({"payment_status": {"$in": ["Paid", "Refund Pending"]}}, {"amount": 1, "created_at": 1, "status": 1}))
    revenue = sum(b["amount"] for b in paid if b["status"] != "Cancelled")
    fee = sum(b.get("platform_fee", 0) for b in db.bookings.find({"status": "Completed"}, {"platform_fee": 1}))
    start = today_ist() - timedelta(days=6)
    days = {(start + timedelta(days=i)).isoformat(): {"bookings": 0, "revenue": 0} for i in range(7)}
    for b in db.bookings.find({"created_at": {"$gte": now() - timedelta(days=8)}}, {"created_at": 1, "amount": 1, "payment_status": 1}):
        k = (b["created_at"].replace(tzinfo=None) + timedelta(hours=5, minutes=30)).date().isoformat()
        if k in days:
            days[k]["bookings"] += 1
            if b["payment_status"] == "Paid":
                days[k]["revenue"] += b["amount"]
    return {
        "users": db.users.count_documents({"role": "user"}),
        "providers": db.users.count_documents({"role": "provider", "approved": True}),
        "pending_providers": db.users.count_documents({"role": "provider", "approved": False, "is_active": True}),
        "bookings": db.bookings.count_documents({}),
        "by_status": {s: db.bookings.count_documents({"status": s}) for s in STATUSES},
        "unassigned_paid": db.bookings.count_documents({"status": "Pending", "payment_status": "Paid", "provider_id": None}),
        "revenue": revenue, "platform_fees": fee,
        "refund_pending": db.bookings.count_documents({"payment_status": "Refund Pending"}),
        "series": [{"date": k, **v} for k, v in days.items()],
    }


# ---------------- users & providers ----------------
@bp.get("/users")
@auth_required("admin")
def users():
    q = {}
    role = request.args.get("role")
    if role in ("user", "provider", "admin"):
        q["role"] = role
    if s := request.args.get("q", "").strip()[:60]:
        rx = {"$regex": re.escape(s), "$options": "i"}
        q["$or"] = [{"name": rx}, {"email": rx}, {"mobile": rx}]
    rows = list(db.users.find(q).sort("created_at", -1).limit(300))
    for u in rows:
        if u["role"] == "provider":
            u["jobs_done"] = db.bookings.count_documents({"provider_id": u["_id"], "status": "Completed"})
        elif u["role"] == "user":
            u["bookings"] = db.bookings.count_documents({"user_id": u["_id"]})
    return {"users": ser(rows)}


@bp.patch("/users/<uid>")
@auth_required("admin")
def update_user(uid):
    d = request.get_json(silent=True) or {}
    target = db.users.find_one({"_id": oid(uid)})
    if not target:
        return err("User not found.", 404)
    upd = {}
    if "is_active" in d:
        if target["_id"] == g.user["_id"]:
            return err("You can't deactivate your own account.")
        upd["is_active"] = bool(d["is_active"])
    if "approved" in d and target["role"] == "provider":
        upd["approved"] = bool(d["approved"])
    if not upd:
        return err("Nothing to update.")
    db.users.update_one({"_id": target["_id"]}, {"$set": upd})
    return {"user": ser(db.users.find_one({"_id": target["_id"]}))}


# ---------------- bookings ----------------
@bp.get("/bookings")
@auth_required("admin")
def bookings():
    q = {}
    if (st := request.args.get("status")) in STATUSES:
        q["status"] = st
    if request.args.get("payment") in ("Unpaid", "Paid", "Refunded", "Refund Pending"):
        q["payment_status"] = request.args["payment"]
    if s := request.args.get("q", "").strip()[:60]:
        rx = {"$regex": re.escape(s), "$options": "i"}
        q["$or"] = [{"user_name": rx}, {"service_name": rx}, {"contact": rx}, {"provider_name": rx}, {"city": rx}]
    return {"bookings": ser(list(db.bookings.find(q).sort("created_at", -1).limit(300)))}


@bp.patch("/bookings/<bid>")
@auth_required("admin")
def update_booking(bid):
    d = request.get_json(silent=True) or {}
    b = db.bookings.find_one({"_id": oid(bid)})
    if not b:
        return err("Booking not found.", 404)
    upd, log = {"updated_at": now()}, []
    if "provider_id" in d:
        if d["provider_id"] in (None, ""):
            upd.update({"provider_id": None, "provider_name": None, "provider_mobile": None})
            if b["status"] in ("Accepted", "In Progress"):
                upd["status"] = "Pending"
            log.append(hist("Provider unassigned", g.user["name"]))
        else:
            p = db.users.find_one({"_id": oid(d["provider_id"]), "role": "provider", "approved": True, "is_active": True})
            if not p:
                return err("Choose an approved, active provider.")
            upd.update({"provider_id": p["_id"], "provider_name": p["name"], "provider_mobile": p["mobile"]})
            if b["status"] == "Pending":
                upd["status"] = "Accepted"
            log.append(hist(f"Assigned to {p['name']}", g.user["name"]))
    status = d.get("status")
    if status:
        if status not in STATUSES:
            return err("Invalid status.")
        upd["status"] = status
        log.append(hist(status, g.user["name"]))
        if status == "Completed":
            pct = current_app.config["PLATFORM_FEE_PERCENT"]
            fee = round(b["amount"] * pct / 100)
            upd.update({"platform_fee": fee, "provider_earning": b["amount"] - fee, "completed_at": now()})
    op = {"$set": upd}
    if log:
        op["$push"] = {"history": {"$each": log}}
    db.bookings.update_one({"_id": b["_id"]}, op)
    fresh = db.bookings.find_one({"_id": b["_id"]})
    refund = None
    if upd.get("status") == "Cancelled" and b["status"] != "Cancelled":
        ok, msg = refund_booking(fresh, "Cancelled by admin")
        refund = {"ok": ok, "message": msg}
        fresh = db.bookings.find_one({"_id": b["_id"]})
    return {"booking": ser(fresh), "refund": refund}


@bp.post("/bookings/<bid>/refund")
@auth_required("admin")
def refund(bid):
    b = db.bookings.find_one({"_id": oid(bid)})
    if not b:
        return err("Booking not found.", 404)
    if b["payment_status"] not in ("Paid", "Refund Pending"):
        return err("This booking has no payment to refund.", 409)
    ok, msg = refund_booking(b, "Refunded by admin")
    if not ok:
        return err(f"Refund failed: {msg}", 502)
    if b["status"] not in ("Cancelled", "Completed"):
        db.bookings.update_one({"_id": b["_id"]}, {"$set": {"status": "Cancelled", "updated_at": now()},
                               "$push": {"history": hist("Cancelled", g.user["name"])}})
    return {"booking": ser(db.bookings.find_one({"_id": b["_id"]}))}


@bp.get("/payments")
@auth_required("admin")
def payments():
    rows = list(db.payments.find({}).sort("created_at", -1).limit(300))
    users = {u["_id"]: u for u in db.users.find({"_id": {"$in": [r["user_id"] for r in rows]}}, {"name": 1, "email": 1})}
    books = {b["_id"]: b for b in db.bookings.find({"_id": {"$in": [r["booking_id"] for r in rows]}}, {"service_name": 1})}
    for r in rows:
        r["user_name"] = users.get(r["user_id"], {}).get("name", "—")
        r["service_name"] = books.get(r["booking_id"], {}).get("service_name", "—")
    return {"payments": ser(rows)}


# ---------------- services ----------------
def _service_fields(d, partial=False):
    out = {}
    name, desc = text(d, "name", 80), text(d, "description", 600)
    if name or not partial:
        if not name:
            return None, "Enter a service name."
        out["name"] = name
    if desc or not partial:
        out["description"] = desc
    if "price" in d or not partial:
        try:
            price = int(d.get("price"))
        except (TypeError, ValueError):
            return None, "Enter the price as a whole number of rupees."
        if not 1 <= price <= 500000:
            return None, "Price must be between ₹1 and ₹5,00,000."
        out["price"] = price
    for k in ("image", "color", "icon", "duration"):
        if k in d:
            out[k] = text(d, k, 120)
    if "active" in d:
        out["active"] = bool(d["active"])
    return out, None


@bp.get("/services")
@auth_required("admin")
def all_services():
    return {"services": ser(list(db.services.find({}).sort("name", 1)))}


@bp.post("/services")
@auth_required("admin")
def create_service():
    d = request.get_json(silent=True) or {}
    f, e = _service_fields(d)
    if e:
        return err(e)
    f.update({"slug": _slug(f["name"]), "active": f.get("active", True), "created_at": now()})
    f.setdefault("color", "#d6e2fb"); f.setdefault("icon", "wrench"); f.setdefault("image", ""); f.setdefault("duration", "60–90 min")
    try:
        f["_id"] = db.services.insert_one(f).inserted_id
    except DuplicateKeyError:
        return err("A service with this name already exists.", 409)
    return {"service": ser(f)}, 201


@bp.put("/services/<sid>")
@auth_required("admin")
def update_service(sid):
    f, e = _service_fields(request.get_json(silent=True) or {}, partial=True)
    if e:
        return err(e)
    res = db.services.find_one_and_update({"_id": oid(sid)}, {"$set": f}, return_document=True)
    return {"service": ser(res)} if res else err("Service not found.", 404)
