from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError

from .db import db
from .utils import now

# Prices for AC, PC repair, Salon, Plumber and Painting come from your original booking form.
# Electrician, Vehicle mechanic and Kitchen cleaning had no price there — those are placeholders; edit them in Admin > Services.
SERVICES = [
    ("ac-repair", "AC repair", 2000, "snowflake", "#f8d7df", "/img/ac.jpg", "60–120 min",
     "Servicing, gas top-up, leak fixes and installation for split and window ACs."),
    ("painting", "Painting", 1000, "paintbrush", "#cfeef1", "/img/painter.jpg", "Half day",
     "Interior and exterior wall painting, touch-ups and waterproof coating."),
    ("electrician", "Electrician", 600, "zap", "#fbecc0", "/img/electrician.jpg", "45–90 min",
     "Wiring, switches, fans, lights, MCB and inverter fixes by a verified electrician."),
    ("plumber", "Plumber", 500, "droplets", "#d6e2fb", "/img/plumber.jpg", "45–90 min",
     "Leaks, taps, blocked drains, tank and bathroom fittings repaired the same day."),
    ("pc-repair", "PC repair", 3500, "laptop", "#e5dcf7", "/img/pc-repair.jpg", "1–3 hours",
     "Laptop and desktop diagnosis, hardware swaps, OS reinstall and data recovery."),
    ("salon", "Salon at home", 1000, "scissors", "#fde2cf", "/img/salon.jpg", "60–90 min",
     "Haircut, grooming and beauty services at your doorstep with sanitised tools."),
    ("vehicle-mechanic", "Vehicle mechanic", 1500, "car", "#d9eed3", "/img/vehicles.jpg", "1–2 hours",
     "Doorstep car and bike check-ups, battery, brake and minor repairs."),
    ("kitchen-cleaning", "Kitchen cleaning", 1200, "sparkles", "#cdeee3", "/img/kitchen.jpg", "2–3 hours",
     "Deep clean of counters, chimney, cabinets, sink and appliances."),
]


def seed_services():
    if db.services.count_documents({}) > 0:
        return
    for slug, name, price, icon, color, image, duration, desc in SERVICES:
        db.services.insert_one({"slug": slug, "name": name, "price": price, "icon": icon, "color": color,
                                "image": image, "duration": duration, "description": desc,
                                "active": True, "created_at": now()})


def _user(name, email, mobile, password, role, **extra):
    try:
        db.users.insert_one({"name": name, "email": email, "mobile": mobile, "city": "Ranchi", "role": role,
                             "password": generate_password_hash(password), "is_active": True,
                             "created_at": now(), **extra})
        return True
    except DuplicateKeyError:
        return False


def seed_admin(app):
    email, pw = app.config["ADMIN_EMAIL"].lower(), app.config["ADMIN_PASSWORD"]
    if not email or not pw:
        app.logger.warning("ADMIN_EMAIL / ADMIN_PASSWORD not set — no admin account was created.")
        return
    if _user(app.config["ADMIN_NAME"], email, "9000000000", pw, "admin"):
        app.logger.info("Created admin account %s", email)


def seed_demo():
    """Sample accounts for trying the three dashboards. Never run in production."""
    slugs = [s[0] for s in SERVICES]
    a = _user("Demo Customer", "user@example.com", "9111111111", "Password123!", "user")
    b = _user("Demo Provider", "provider@example.com", "9222222222", "Password123!", "provider",
              skills=slugs, bio="Multi-skilled technician, 8 years experience.", approved=True)
    return a, b
