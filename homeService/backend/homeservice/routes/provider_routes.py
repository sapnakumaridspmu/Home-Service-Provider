from flask import Blueprint, request, g, current_app

from ..auth import auth_required, approved_provider
from ..db import db
from ..utils import err, ser, oid, now, hist

bp = Blueprint("provider", __name__, url_prefix="/api/provider")

TRANSITIONS = {"Accepted": ["In Progress", "Completed"], "In Progress": ["Completed"]}


def _fee_split(amount):
    pct = current_app.config["PLATFORM_FEE_PERCENT"]
    fee = round(amount * pct / 100)
    return fee, amount - fee


@bp.get("/stats")
@auth_required("provider")
def stats():
    mine = list(db.bookings.find({"provider_id": g.user["_id"]}))
    done = [b for b in mine if b["status"] == "Completed"]
    active = [b for b in mine if b["status"] in ("Accepted", "In Progress")]
    open_q = {"status": "Pending", "payment_status": "Paid", "provider_id": None,
              "service_slug": {"$in": g.user.get("skills", [])}}
    return {
        "approved": g.user.get("approved", False),
        "available": db.bookings.count_documents(open_q) if g.user.get("approved") else 0,
        "active": len(active), "completed": len(done),
        "earnings": sum(b.get("provider_earning", 0) for b in done),
        "upcoming_earnings": sum(_fee_split(b["amount"])[1] for b in active),
        "fee_percent": current_app.config["PLATFORM_FEE_PERCENT"],
    }


@bp.get("/jobs/available")
@auth_required("provider")
@approved_provider
def available():
    q = {"status": "Pending", "payment_status": "Paid", "provider_id": None,
         "service_slug": {"$in": g.user.get("skills", [])}}
    jobs = list(db.bookings.find(q).sort("date", 1))
    for j in jobs:  # exact address & contact stay hidden until the provider accepts the job
        j["provider_earning"] = _fee_split(j["amount"])[1]
        for k in ("user_email", "user_name", "contact", "address", "landmark"):
            j.pop(k, None)
    return {"jobs": ser(jobs)}


@bp.get("/jobs")
@auth_required("provider")
def mine():
    jobs = list(db.bookings.find({"provider_id": g.user["_id"]}).sort("updated_at", -1))
    for j in jobs:
        j["provider_earning"] = j.get("provider_earning") or _fee_split(j["amount"])[1]
    return {"jobs": ser(jobs)}


@bp.post("/jobs/<bid>/accept")
@auth_required("provider")
@approved_provider
def accept(bid):
    # Atomic claim: if two providers tap Accept together, exactly one wins.
    b = db.bookings.find_one_and_update(
        {"_id": oid(bid), "status": "Pending", "payment_status": "Paid", "provider_id": None,
         "service_slug": {"$in": g.user.get("skills", [])}},
        {"$set": {"provider_id": g.user["_id"], "provider_name": g.user["name"], "provider_mobile": g.user["mobile"],
                  "status": "Accepted", "updated_at": now()},
         "$push": {"history": hist("Accepted", g.user["name"])}},
        return_document=True,
    )
    return {"job": ser(b)} if b else err("This job was just taken or is no longer available.", 409)


@bp.post("/jobs/<bid>/release")
@auth_required("provider")
def release(bid):
    b = db.bookings.find_one_and_update(
        {"_id": oid(bid), "provider_id": g.user["_id"], "status": "Accepted"},
        {"$set": {"provider_id": None, "provider_name": None, "provider_mobile": None, "status": "Pending", "updated_at": now()},
         "$push": {"history": hist("Released by provider", g.user["name"])}},
        return_document=True,
    )
    return {"job": ser(b)} if b else err("Only accepted jobs that haven't started can be released.", 409)


@bp.post("/jobs/<bid>/status")
@auth_required("provider")
def set_status(bid):
    new = (request.get_json(silent=True) or {}).get("status")
    b = db.bookings.find_one({"_id": oid(bid), "provider_id": g.user["_id"]})
    if not b:
        return err("Job not found.", 404)
    if new not in TRANSITIONS.get(b["status"], []):
        return err(f"A job that is {b['status']} can't be moved to {new}.", 409)
    upd = {"status": new, "updated_at": now()}
    if new == "Completed":
        fee, earn = _fee_split(b["amount"])
        upd.update({"platform_fee": fee, "provider_earning": earn, "completed_at": now()})
    res = db.bookings.find_one_and_update(
        {"_id": b["_id"], "status": b["status"]},
        {"$set": upd, "$push": {"history": hist(new, g.user["name"])}}, return_document=True)
    return {"job": ser(res)} if res else err("This job was just updated. Refresh and try again.", 409)
