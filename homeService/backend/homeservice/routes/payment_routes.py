import json

from flask import Blueprint, request, g, current_app

from .. import gateway
from ..auth import auth_required
from ..db import db
from ..payments_core import mark_paid
from ..utils import err, ser, oid, now, text

bp = Blueprint("payments", __name__, url_prefix="/api/payments")


def _own_payable(booking_id):
    b = db.bookings.find_one({"_id": oid(booking_id), "user_id": g.user["_id"]})
    if not b:
        return None, err("Booking not found.", 404)
    if b["status"] == "Cancelled":
        return None, err("This booking was cancelled.", 409)
    if b["payment_status"] == "Paid":
        return None, err("This booking is already paid.", 409)
    return b, None


@bp.post("/create-order")
@auth_required("user")
def create_order():
    b, e = _own_payable((request.get_json(silent=True) or {}).get("booking_id"))
    if e:
        return e
    try:
        order_id = gateway.create_order(b["amount"], f"bk_{b['_id']}", {"booking_id": str(b["_id"])})
    except gateway.GatewayError as ex:
        return err(str(ex), 502)
    db.payments.insert_one({
        "booking_id": b["_id"], "user_id": g.user["_id"], "order_id": order_id, "amount": b["amount"],
        "currency": "INR", "status": "created", "gateway": gateway.mode(), "created_at": now(),
    })
    return {
        "mode": gateway.mode(), "order_id": order_id, "amount": b["amount"] * 100, "currency": "INR",
        "key_id": current_app.config["RAZORPAY_KEY_ID"], "booking": ser(b),
        "prefill": {"name": g.user["name"], "email": g.user["email"], "contact": g.user["mobile"]},
    }


@bp.post("/verify")
@auth_required("user")
def verify():
    """Called by the browser after Razorpay Checkout succeeds. The signature is checked with the
    secret key, so a customer cannot mark their own booking paid by calling this directly."""
    d = request.get_json(silent=True) or {}
    order_id, payment_id = d.get("razorpay_order_id"), d.get("razorpay_payment_id")
    pay = db.payments.find_one({"order_id": order_id, "user_id": g.user["_id"]})
    if not pay:
        return err("Unknown payment order.", 404)
    if not gateway.verify_payment(order_id, payment_id, d.get("razorpay_signature")):
        return err("Payment verification failed. If money was deducted, it will be refunded automatically.", 400)
    mark_paid(order_id, payment_id)
    return {"booking": ser(db.bookings.find_one({"_id": pay["booking_id"]}))}


@bp.post("/demo-pay")
@auth_required("user")
def demo_pay():
    """Development-only stand-in for the Razorpay popup. Disabled whenever real keys exist or APP_ENV=production."""
    if gateway.mode() != "demo":
        return err("Not found.", 404)
    order_id = (request.get_json(silent=True) or {}).get("order_id")
    pay = db.payments.find_one({"order_id": order_id, "user_id": g.user["_id"]})
    if not pay:
        return err("Unknown payment order.", 404)
    payment_id = "pay_demo_" + order_id[-10:]
    mark_paid(order_id, payment_id)
    return {"booking": ser(db.bookings.find_one({"_id": pay["booking_id"]}))}


@bp.post("/webhook")
def webhook():
    """Razorpay server-to-server events. This is the safety net when the customer closes the tab
    right after paying. Configure it in the Razorpay dashboard: events payment.captured + order.paid."""
    raw = request.get_data()
    if not gateway.verify_webhook(raw, request.headers.get("X-Razorpay-Signature", "")):
        return err("Invalid signature.", 400)
    event = json.loads(raw or b"{}")
    name = event.get("event")
    ent = (event.get("payload", {}).get("payment", {}) or {}).get("entity", {})
    if name in ("payment.captured", "order.paid") and ent.get("order_id"):
        mark_paid(ent["order_id"], ent.get("id"))
    return {"ok": True}


@bp.get("")
@auth_required("user")
def mine():
    return {"payments": ser(list(db.payments.find({"user_id": g.user["_id"]}).sort("created_at", -1)))}
