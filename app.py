import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, abort, redirect, request

from migrations import run_migrations
from models import Link, db
from routes import register_routes
from utils.filters import register_filters

load_dotenv(override=True)

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY_BASE", os.urandom(100).hex())
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///hop.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

ADMIN_DOMAIN = os.getenv("ADMIN_DOMAIN", "")
REDIRECT_DOMAIN = os.getenv("REDIRECT_DOMAIN", "")

db.init_app(app)
register_filters(app)
register_routes(app)

with app.app_context():
    db.create_all()
    run_migrations()


def resolve_redirect(slug):
    link = Link.query.filter_by(slug=slug.lower()).first()
    if not link or not link.is_active:
        abort(404)
    return redirect(link.target_url, code=301 if link.is_permanent else 302)


@app.before_request
def enforce_domain_split():
    if not ADMIN_DOMAIN and not REDIRECT_DOMAIN:
        return

    host = request.host.split(":")[0]
    is_redirect_endpoint = request.endpoint == "redirect_slug"

    if host == REDIRECT_DOMAIN:
        if request.path == "/":
            return resolve_redirect("")
        if not is_redirect_endpoint:
            abort(404)
    elif host == ADMIN_DOMAIN:
        if is_redirect_endpoint:
            abort(404)
    else:
        abort(404)


@app.get("/<slug>")
def redirect_slug(slug):
    return resolve_redirect(slug)


if __name__ == "__main__":
    app.run(debug=True, port=4000, host="0.0.0.0")
