"""Payment gateway: Razorpay (INR) with a built-in demo mode for development.

Modes
  razorpay  - RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET are set
  demo      - no keys and APP_ENV != production (fake orders, confirmed from the UI)
  disabled  - no keys in production: payments refuse to run instead of silently faking success
"""
import hashlib
import hmac
import uuid

import requests
from flask import current_app

API = "https://api.razorpay.com/v1"


class GatewayError(Exception):
    pass


def mode():
    c = current_app.config
    if c["RAZORPAY_KEY_ID"] and c["RAZORPAY_KEY_SECRET"]:
        return "razorpay"
    return "disabled" if c["APP_ENV"] == "production" else "demo"


def _auth():
    c = current_app.config
    return (c["RAZORPAY_KEY_ID"], c["RAZORPAY_KEY_SECRET"])


def _secret():
    c = current_app.config
    return c["RAZORPAY_KEY_SECRET"] or c["SECRET_KEY"]


def _post(path, payload):
    try:
        r = requests.post(f"{API}{path}", auth=_auth(), json=payload, timeout=20)
    except requests.RequestException as e:
        raise GatewayError(f"Could not reach the payment gateway: {e}")
    if r.status_code >= 400:
        try:
            msg = r.json().get("error", {}).get("description", r.text)
        except ValueError:
            msg = r.text
        raise GatewayError(msg)
    return r.json()


def create_order(amount_inr, receipt, notes=None):
    """Returns the gateway order id. Amount is converted to paise here, once."""
    m = mode()
    if m == "razorpay":
        data = _post("/orders", {"amount": int(round(amount_inr * 100)), "currency": "INR",
                                 "receipt": receipt[:40], "notes": notes or {}})
        return data["id"]
    if m == "demo":
        return "order_demo_" + uuid.uuid4().hex[:14]
    raise GatewayError("Online payments are not configured yet.")


def _hmac(message: str) -> str:
    return hmac.new(_secret().encode(), message.encode(), hashlib.sha256).hexdigest()


def sign(order_id, payment_id):
    return _hmac(f"{order_id}|{payment_id}")


def verify_payment(order_id, payment_id, signature):
    return hmac.compare_digest(sign(order_id, payment_id), signature or "")


def verify_webhook(raw_body: bytes, signature: str):
    secret = current_app.config["RAZORPAY_WEBHOOK_SECRET"]
    if not secret:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")


def refund(payment_id, amount_inr, notes=None):
    """Full/partial refund. Returns the refund id."""
    m = mode()
    if m == "razorpay":
        data = _post(f"/payments/{payment_id}/refund",
                     {"amount": int(round(amount_inr * 100)), "notes": notes or {}})
        return data["id"]
    if m == "demo":
        return "rfnd_demo_" + uuid.uuid4().hex[:12]
    raise GatewayError("Online payments are not configured yet.")
