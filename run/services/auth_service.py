import hmac
import secrets
from functools import wraps
from flask import abort, redirect, request, session, url_for


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def valid_csrf():
    supplied = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    return bool(expected) and hmac.compare_digest(supplied, expected)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("auth.login"))
        if session.get("role") != "Administrator":
            abort(403)
        return func(*args, **kwargs)
    return wrapper
