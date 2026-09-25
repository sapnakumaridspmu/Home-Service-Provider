import os
from dotenv import load_dotenv

load_dotenv()


def _f(name, default):
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return float(default)


class Config:
    APP_ENV = os.environ.get("APP_ENV", "development")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.environ.get("MONGO_DB", "home_service_provider")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    FRONTEND_DIST = os.environ.get(
        "FRONTEND_DIST",
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"),
    )
    JWT_HOURS = int(_f("JWT_HOURS", 168))

    RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
    PLATFORM_FEE_PERCENT = _f("PLATFORM_FEE_PERCENT", 15)

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "Site Admin")

    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(_f("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", "Home Service Provider <no-reply@example.com>")

    TESTING = False
