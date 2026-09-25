import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import Config
from .db import init_db
from .seed import seed_services, seed_admin
from .utils import err


def create_app(overrides=None, mongo_client=None):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    app.config.update(overrides or {})
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

    if app.config["APP_ENV"] == "production" and (
            app.config["SECRET_KEY"].startswith("dev-secret") or len(app.config["SECRET_KEY"]) < 32):
        raise RuntimeError("Set SECRET_KEY to a random string of at least 32 characters before running in production.")

    CORS(app, resources={r"/api/*": {"origins": [app.config["FRONTEND_URL"]]}})
    init_db(app.config["MONGO_URI"], app.config["MONGO_DB"], client=mongo_client)
    seed_services()
    seed_admin(app)

    from .routes import auth_routes, public_routes, booking_routes, payment_routes, provider_routes, admin_routes
    for m in (public_routes, auth_routes, booking_routes, payment_routes, provider_routes, admin_routes):
        app.register_blueprint(m.bp)

    @app.errorhandler(404)
    def _404(_):
        return err("Not found.", 404)

    @app.errorhandler(405)
    def _405(_):
        return err("Method not allowed.", 405)

    @app.errorhandler(413)
    def _413(_):
        return err("Request too large.", 413)

    @app.errorhandler(500)
    def _500(e):
        app.logger.exception(e)
        return err("Something went wrong on our side. Please try again.", 500)

    # Serve the built React app from the same server (single-service deploys, e.g. Render).
    dist = os.path.abspath(app.config["FRONTEND_DIST"])
    if os.path.isdir(dist):
        @app.get("/", defaults={"path": ""})
        @app.get("/<path:path>")
        def spa(path):
            if path.startswith("api/"):
                return err("Not found.", 404)
            if path and os.path.isfile(os.path.join(dist, path)):
                return send_from_directory(dist, path)
            return send_from_directory(dist, "index.html")

    return app
