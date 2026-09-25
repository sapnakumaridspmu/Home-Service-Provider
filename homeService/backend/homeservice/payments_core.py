"""Shared payment state transitions (used by the verify endpoint, webhook and cancellations).
Every transition is idempotent: the gateway can and will deliver the same event twice."""
from . import gateway
from .db import db
from .utils import now


def _refund_payment_only(pay, reason):
    """Refund a single payment that can't be attached to its booking (duplicate or late payment)."""
    try:
        rid = gateway.refund(pay["payment_id"], pay["amount"], {"reason": reason})
        db.payments.update_one({"_id": pay["_id"]}, {"$set": {"status": "refunded", "refund_id": rid, "refunded_at": now()}})
    except gateway.GatewayError:
        db.payments.update_one({"_id": pay["_id"]}, {"$set": {"status": "refund_failed"}})


def mark_paid(order_id, payment_id):
    """Flip payment + booking to Paid exactly once. Returns the payment doc, or None if unknown."""
    pay = db.payments.find_one_and_update(
        {"order_id": order_id, "status": "created"},
        {"$set": {"status": "paid", "payment_id": payment_id, "paid_at": now()}},
        return_document=True,
    )
    if pay is None:
        return db.payments.find_one({"order_id": order_id})  # already processed, or unknown
    res = db.bookings.update_one(
        {"_id": pay["booking_id"], "payment_status": "Unpaid"},
        {"$set": {"payment_status": "Paid", "payment_id": payment_id, "paid_at": now(), "updated_at": now()},
         "$push": {"history": {"status": "Payment received", "at": now(), "by": "system"}}},
    )
    if res.matched_count == 0:  # booking was already paid through another order
        _refund_payment_only(pay, "Duplicate payment")
        return pay
    booking = db.bookings.find_one({"_id": pay["booking_id"]})
    if booking["status"] == "Cancelled":  # paid just after cancelling
        refund_booking(booking, "Payment arrived after cancellation")
    return pay


def refund_booking(booking, reason):
    """Refund a paid booking. Returns (ok, message). On gateway failure the booking is flagged
    'Refund Pending' so an admin can retry from the dashboard."""
    if booking.get("payment_status") not in ("Paid", "Refund Pending"):
        return True, "Nothing to refund"
    pay = db.payments.find_one({"booking_id": booking["_id"], "status": "paid"})
    if not pay:
        return False, "No captured payment found for this booking"
    try:
        refund_id = gateway.refund(pay["payment_id"], booking["amount"], {"booking": str(booking["_id"]), "reason": reason})
    except gateway.GatewayError as e:
        db.bookings.update_one({"_id": booking["_id"]}, {"$set": {"payment_status": "Refund Pending", "updated_at": now()}})
        return False, str(e)
    db.payments.update_one({"_id": pay["_id"]}, {"$set": {"status": "refunded", "refund_id": refund_id, "refunded_at": now()}})
    db.bookings.update_one(
        {"_id": booking["_id"]},
        {"$set": {"payment_status": "Refunded", "updated_at": now()},
         "$push": {"history": {"status": "Refunded", "at": now(), "by": "system"}}},
    )
    return True, "Refunded"
