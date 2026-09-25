import re
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from bson.errors import InvalidId
from flask import jsonify

IST = timezone(timedelta(hours=5, minutes=30))
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")  # Indian 10-digit mobile
SLOTS = ["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00"]


def now():
    return datetime.now(timezone.utc)


def today_ist():
    return datetime.now(IST).date()


def err(message, status=400):
    return jsonify({"error": message}), status


def oid(value):
    try:
        return ObjectId(str(value))
    except (InvalidId, TypeError):
        return None


def ser(value):
    """Make Mongo documents JSON-safe: _id -> id, ObjectId -> str, datetimes -> ISO (UTC), drop secrets."""
    if isinstance(value, list):
        return [ser(v) for v in value]
    if isinstance(value, dict):
        return {("id" if k == "_id" else k): ser(v) for k, v in value.items() if k != "password"}
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value).isoformat().replace("+00:00", "Z")
    return value


def text(data, key, max_len=300):
    v = data.get(key)
    return v.strip()[:max_len] if isinstance(v, str) else ""


def valid_name(name):
    return bool(name) and name.replace(" ", "").replace(".", "").isalpha()


def hist(status, by):
    return {"status": status, "at": now(), "by": by}
