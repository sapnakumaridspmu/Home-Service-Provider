"""MongoDB access. `db` is a thin proxy so routes can `from ..db import db`
and tests can swap in mongomock via init_db(client=...)."""
from pymongo import MongoClient, ASCENDING, DESCENDING

_db = None


def init_db(uri, name, client=None):
    global _db
    client = client or MongoClient(uri, serverSelectionTimeoutMS=8000)
    _db = client[name]
    _db.users.create_index("email", unique=True)
    _db.services.create_index("slug", unique=True)
    _db.bookings.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    _db.bookings.create_index([("provider_id", ASCENDING), ("status", ASCENDING)])
    _db.payments.create_index("order_id", unique=True)
    return _db


class _Proxy:
    def __getattr__(self, name):
        if _db is None:
            raise RuntimeError("Database not initialised")
        return getattr(_db, name)


db = _Proxy()
