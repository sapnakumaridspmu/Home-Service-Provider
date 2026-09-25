from flask import Blueprint

from ..db import db
from ..gateway import mode
from ..utils import err, ser, SLOTS

bp = Blueprint("public", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    return {"ok": True}


@bp.get("/services")
def services():
    return {"services": ser(list(db.services.find({"active": True}).sort("name", 1)))}


@bp.get("/services/<slug>")
def service(slug):
    s = db.services.find_one({"slug": slug, "active": True})
    return ({"service": ser(s)}) if s else err("Service not found.", 404)


@bp.get("/config")
def config():
    return {"slots": SLOTS, "payment_mode": mode()}
