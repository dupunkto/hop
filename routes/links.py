from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from models import Link, db, now
from utils.auth import is_authenticated, require_auth

links_bp = Blueprint("links", __name__)


def read_link_form():
    expires_at = request.form.get("expires_at") or None
    return {
        "slug": (request.form.get("slug") or "").strip().lower().lstrip("/"),
        "target_url": (request.form.get("target_url") or "").strip(),
        "expires_at": expires_at,
        "is_permanent": request.form.get("is_permanent") == "true",
        "is_disabled": request.form.get("is_disabled") == "true",
    }


@links_bp.get("/")
def list_links():
    if not is_authenticated():
        return render_template("landing.jinja")

    links = Link.query.order_by(Link.created_at.desc()).all()
    return render_template("links/list.jinja", links=links)


@links_bp.get("/login")
@require_auth
def login():
    return redirect(url_for("links.list_links"))


@links_bp.get("/new")
@require_auth
def new_link():
    return render_template("links/form.jinja", link=None)


@links_bp.post("/")
@require_auth
def create_link():
    fields = read_link_form()

    if not fields["target_url"]:
        flash("A link needs a target URL.", "error")
        return render_template("links/form.jinja", link=None), 400

    link = Link(
        expires_at=fields["expires_at"],
        is_permanent=fields["is_permanent"],
        is_disabled=fields["is_disabled"],
    )
    try:
        link.target_url = fields["target_url"]
        link.slug = fields["slug"]
        db.session.add(link)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "error")
        return render_template("links/form.jinja", link=link), 400
    except IntegrityError:
        db.session.rollback()
        if fields["slug"]:
            flash("That path is already in use.", "error")
        else:
            flash("The / redirect is already in use.", "error")
        return render_template("links/form.jinja", link=link), 400

    flash("Link created.", "success")
    return redirect(url_for("links.list_links"), code=303)


@links_bp.get("/<link_id>/edit")
@require_auth
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    return render_template("links/form.jinja", link=link)


@links_bp.post("/<link_id>/update")
@require_auth
def update_link(link_id):
    link = Link.query.get_or_404(link_id)
    fields = read_link_form()

    if not fields["target_url"]:
        flash("A link needs a target URL.", "error")
        return render_template("links/form.jinja", link=link), 400

    try:
        link.slug = fields["slug"]
        link.target_url = fields["target_url"]
        link.expires_at = fields["expires_at"]
        link.is_permanent = fields["is_permanent"]
        link.is_disabled = fields["is_disabled"]
        link.updated_at = now()
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "error")
        return render_template("links/form.jinja", link=link), 400
    except IntegrityError:
        db.session.rollback()
        flash("That path is already in use.", "error")
        return render_template("links/form.jinja", link=link), 400

    flash("Link saved.", "success")
    return redirect(url_for("links.list_links"), code=303)


@links_bp.post("/<link_id>/delete")
@require_auth
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash("Link deleted.", "success")
    return redirect(url_for("links.list_links"), code=303)
