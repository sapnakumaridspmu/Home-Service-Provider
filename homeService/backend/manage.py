"""Helper commands.   python manage.py demo   -> creates demo customer + provider (dev only)"""
import sys
from homeservice import create_app
from homeservice.seed import seed_demo

if __name__ == "__main__":
    app = create_app()
    if app.config["APP_ENV"] == "production":
        sys.exit("Refusing to create demo accounts in production.")
    if sys.argv[1:] == ["demo"]:
        with app.app_context():
            a, b = seed_demo()
            print("Demo customer: user@example.com / Password123!", "(created)" if a else "(already existed)")
            print("Demo provider: provider@example.com / Password123!", "(created)" if b else "(already existed)")
    else:
        print(__doc__)
