import re
import secrets
import string
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

ID_LENGTH = 8

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def generate_id():
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(ID_LENGTH))


def now():
    return datetime.now(timezone.utc)


class Link(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=generate_id)

    slug = db.Column(db.String(200), unique=True, nullable=False)
    target_url = db.Column(db.String(2000), nullable=False)

    is_disabled = db.Column(db.Boolean, default=False, nullable=False)
    is_permanent = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    @validates("slug")
    def validate_slug(self, key, value):
        value = (value or "").strip().lower().lstrip("/")
        if value and not SLUG_RE.match(value):
            raise ValueError("A slug can only contain lowercase letters, digits and hyphens.")
        return value

    @validates("target_url")
    def validate_target_url(self, key, value):
        value = (value or "").strip()
        if not value.startswith(("http://", "https://")):
            raise ValueError("The target URL must start with http:// or https://.")
        return value

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now() > expires

    @property
    def is_active(self):
        return not self.is_disabled and not self.is_expired

    @property
    def status_label(self):
        if self.is_disabled:
            return "disabled"
        if self.is_expired:
            return "expired"
        return "active"
