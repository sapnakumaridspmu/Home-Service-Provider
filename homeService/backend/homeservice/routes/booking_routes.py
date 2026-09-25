from datetime import date

from flask import Blueprint, request, g

from ..auth import auth_required
from ..db import db
from ..payments_core import refund_booking
from ..utils import err, ser, oid, text, now, hist, today_ist, MOBILE_RE, SLOTS

bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bp.post("")
@auth_required("user")
def create():
    d = request.get_json(silent=True) or {}
    service = db.services.find_one({"_id": oid(d.get("service_id")), "active": True})
    if not service:
        return err("That service isn't available.")
    try:
        day = date.fromisoformat(text(d, "date", 10))
    except ValueError:
        return err("Choose a date for the visit.")
    if day < today_ist():
        return err("The visit date can't be in the past.")
    slot = text(d, "slot", 20)
    if slot not in SLOTS:
        return err("Choose a time slot.")
    address, city = text(d, "address", 300), text(d, "city", 60)
    contact = text(d, "contact", 10) or g.user["mobile"]
    if len(address) < 8:
        return err("Enter the full address where the service is needed.")
    if not MOBILE_RE.match(contact):
        return err("Enter a valid 10-digit contact number.")
    doc = {
        "user_id": g.user["_id"], "user_name": g.user["name"], "user_email": g.user["email"],
        "contact": contact, "service_id": service["_id"], "service_name": service["name"],
        "service_slug": service["slug"],
        "amount": int(service["price"]),  # always priced server-side
        "date": day.isoformat(), "slot": slot, "address": address, "landmark": text(d, "landmark", 120),
        "city": city, "notes": text(d, "notes", 500),
        "status": "Pending", "payment_status": "Unpaid", "provider_id": None, "provider_name": None,
        "created_at": now(), "updated_at": now(), "history": [hist("Booked", g.user["name"])],
    }
    doc["_id"] = db.bookings.insert_one(doc).inserted_id
    return {"booking": ser(doc)}, 201


@bp.get("")
@auth_required("user")
def mine():
    rows = db.bookings.find({"user_id": g.user["_id"]}).sort("created_at", -1)
    return {"bookings": ser(list(rows))}


@bp.get("/<bid>")
@auth_required("user")
def one(bid):
    b = db.bookings.find_one({"_id": oid(bid), "user_id": g.user["_id"]})
    return {"booking": ser(b)} if b else err("Booking not found.", 404)


@bp.post("/<bid>/cancel")
@auth_required("user")
def cancel(bid):
    # Atomic: only cancels if still Pending/Accepted, so it can't race with a provider starting the job.
    b = db.bookings.find_one_and_update(
        {"_id": oid(bid), "user_id": g.user["_id"], "status": {"$in": ["Pending", "Accepted"]}},
        {"$set": {"status": "Cancelled", "updated_at": now()}, "$push": {"history": hist("Cancelled", g.user["name"])}},
        return_document=True,
    )
    if not b:
        return err("This booking can no longer be cancelled.", 409)
    ok, msg = refund_booking(b, "Cancelled by customer")
    b = db.bookings.find_one({"_id": b["_id"]})
    return {"booking": ser(b), "refund": {"ok": ok, "message": msg}}
