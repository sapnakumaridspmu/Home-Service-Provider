import jwt
from flask import Blueprint, request, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError

from ..auth import make_token, decode_token, auth_required
from ..db import db
from ..mailer import send_mail
from ..utils import err, ser, text, now, oid, EMAIL_RE, MOBILE_RE, valid_name

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _check_password(pw):
    if not isinstance(pw, str) or len(pw) < 8:
        return "Password must be at least 8 characters."
    return None


def _skills(raw):
    """Keep only slugs of real, active services."""
    if not isinstance(raw, list):
        return []
    valid = {s["slug"] for s in db.services.find({"active": True}, {"slug": 1})}
    return [s for s in raw if s in valid]


@bp.post("/register")
def register():
    d = request.get_json(silent=True) or {}
    name, email = text(d, "name", 80), text(d, "email", 120).lower()
    mobile, city = text(d, "mobile", 10), text(d, "city", 60)
    role = d.get("role", "user")
    if role not in ("user", "provider"):  # admins are never self-registered
        return err("Choose a valid account type.")
    if not valid_name(name):
        return err("Enter your name using letters only.")
    if not EMAIL_RE.match(email):
        return err("Enter a valid email address.")
    if not MOBILE_RE.match(mobile):
        return err("Enter a valid 10-digit mobile number.")
    if e := _check_password(d.get("password")):
        return err(e)
    doc = {"name": name, "email": email, "mobile": mobile, "city": city, "role": role,
           "password": generate_password_hash(d["password"]), "is_active": True, "created_at": now()}
    if role == "provider":
        skills = _skills(d.get("skills"))
        if not skills:
            return err("Pick at least one service you offer.")
        doc.update({"skills": skills, "bio": text(d, "bio", 500), "approved": False})
    try:
        res = db.users.insert_one(doc)
    except DuplicateKeyError:
        return err("This email is already registered. Please log in instead.", 409)
    user = db.users.find_one({"_id": res.inserted_id})
    return {"token": make_token(user), "user": ser(user)}, 201


@bp.post("/login")
def login():
    d = request.get_json(silent=True) or {}
    user = db.users.find_one({"email": text(d, "email", 120).lower()})
    if not user or not check_password_hash(user["password"], d.get("password") or ""):
        return err("Incorrect email or password.", 401)
    if not user.get("is_active", True):
        return err("This account has been deactivated. Contact support.", 403)
    return {"token": make_token(user), "user": ser(user)}


@bp.get("/me")
@auth_required()
def me():
    return {"user": ser(g.user)}


@bp.put("/me")
@auth_required()
def update_me():
    d = request.get_json(silent=True) or {}
    name, mobile, city = text(d, "name", 80), text(d, "mobile", 10), text(d, "city", 60)
    if not valid_name(name):
        return err("Enter your name using letters only.")
    if not MOBILE_RE.match(mobile):
        return err("Enter a valid 10-digit mobile number.")
    upd = {"name": name, "mobile": mobile, "city": city}
    if g.user["role"] == "provider":
        skills = _skills(d.get("skills"))
        if not skills:
            return err("Pick at least one service you offer.")
        upd.update({"skills": skills, "bio": text(d, "bio", 500)})
    db.users.update_one({"_id": g.user["_id"]}, {"$set": upd})
    return {"user": ser(db.users.find_one({"_id": g.user["_id"]}))}


@bp.put("/password")
@auth_required()
def change_password():
    d = request.get_json(silent=True) or {}
    if not check_password_hash(g.user["password"], d.get("current_password") or ""):
        return err("Your current password is incorrect.")
    if e := _check_password(d.get("new_password")):
        return err(e)
    db.users.update_one({"_id": g.user["_id"]}, {"$set": {"password": generate_password_hash(d["new_password"])}})
    return {"ok": True}


@bp.post("/forgot")
def forgot():
    """Always answers the same way so it can't be used to discover which emails have accounts."""
    email = text(request.get_json(silent=True) or {}, "email", 120).lower()
    user = db.users.find_one({"email": email, "is_active": True})
    if user:
        # `pw` ties the token to the current password hash, so it stops working once used.
        token = make_token(user, hours=1, purpose="reset", extra={"pw": user["password"][-12:]})
        link = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
        send_mail(email, "Reset your password",
                  f"Hi {user['name']},\n\nUse this link to set a new password (valid for 1 hour):\n{link}\n\n"
                  "If you didn't ask for this, you can ignore this email.")
    return {"message": "If an account exists for that email, a reset link is on its way."}


@bp.post("/reset")
def reset():
    d = request.get_json(silent=True) or {}
    try:
        data = decode_token(d.get("token", ""), purpose="reset")
    except jwt.PyJWTError:
        return err("This reset link is invalid or has expired. Request a new one.")
    user = db.users.find_one({"_id": oid(data["sub"])})
    if not user or user["password"][-12:] != data.get("pw"):
        return err("This reset link has already been used. Request a new one.")
    if e := _check_password(d.get("password")):
        return err(e)
    db.users.update_one({"_id": user["_id"]}, {"$set": {"password": generate_password_hash(d["password"])}})
    return {"message": "Password updated. You can log in now."}
