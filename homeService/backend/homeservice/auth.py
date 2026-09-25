from datetime import timedelta
from functools import wraps

import jwt
from flask import request, g, current_app

from .db import db
from .utils import err, oid, now


def make_token(user, hours=None, purpose="access", extra=None):
    payload = {
        "sub": str(user["_id"]),
        "purpose": purpose,
        "exp": now() + timedelta(hours=hours or current_app.config["JWT_HOURS"]),
    }
    payload.update(extra or {})
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token, purpose="access"):
    data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    if data.get("purpose") != purpose:
        raise jwt.InvalidTokenError("wrong purpose")
    return data


def auth_required(*roles):
    """Require a valid bearer token. Role and active-state are read from the DB on every
    request, so deactivating or demoting someone takes effect immediately."""

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return err("Please log in to continue.", 401)
            try:
                data = decode_token(header[7:])
            except jwt.PyJWTError:
                return err("Your session has expired. Please log in again.", 401)
            user = db.users.find_one({"_id": oid(data["sub"])})
            if not user or not user.get("is_active", True):
                return err("This account is not active.", 401)
            if roles and user["role"] not in roles:
                return err("You don't have access to this page.", 403)
            g.user = user
            return fn(*args, **kwargs)

        return wrapper

    return deco


def approved_provider(fn):
    """Provider routes that act on jobs need an admin-approved provider."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not g.user.get("approved"):
            return err("Your provider account is waiting for admin approval.", 403)
        return fn(*args, **kwargs)

    return wrapper
