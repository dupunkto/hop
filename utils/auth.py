import functools

from flask import current_app, g
from nym import require_auth as _nym_require_auth


def is_authenticated():
    return current_app.debug or g.get("authenticated", False)


def require_auth(view):
    protected = _nym_require_auth(view)

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if current_app.debug:
            return view(*args, **kwargs)
        return protected(*args, **kwargs)

    return wrapper
