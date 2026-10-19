import hmac
import time
from collections import defaultdict, deque
from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for
from services.auth_service import csrf_token, valid_csrf

bp = Blueprint("auth", __name__)
_attempts = defaultdict(deque)


def _limited(ip):
    now = time.monotonic()
    attempts = _attempts[ip]
    while attempts and now - attempts[0] >= current_app.config["LOGIN_ATTEMPT_WINDOW"]:
        attempts.popleft()
    return len(attempts) >= current_app.config["LOGIN_ATTEMPT_LIMIT"]


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not valid_csrf():
            abort(400, "Invalid form token. Reload the login page.")
        ip = request.remote_addr or "unknown"
        if _limited(ip):
            return render_template("login.html", title="Server Login", message="Too many unsuccessful attempts. Try again in a few minutes.", token=csrf_token()), 429
        supplied_username = request.form.get("username", "").strip()
        supplied_password = request.form.get("password", "")
        matched_role = None
        for role, username, password in (("Viewer", current_app.config["VIEWER_USERNAME"], current_app.config["VIEWER_PASSWORD"]), ("Administrator", current_app.config["ADMIN_USERNAME"], current_app.config["ADMIN_PASSWORD"])):
            if hmac.compare_digest(supplied_username, username) and hmac.compare_digest(supplied_password, password):
                matched_role = role
                break
        if matched_role:
            _attempts.pop(ip, None)
            session.clear()
            session.permanent = True
            session.update(authenticated=True, username=supplied_username, role=matched_role, csrf_token=csrf_token())
            return redirect(url_for("folder.index"))
        _attempts[ip].append(time.monotonic())
        return render_template("login.html", title="Server Login", message="Incorrect password.", token=csrf_token()), 401
    if session.get("authenticated"):
        return redirect(url_for("folder.index"))
    return render_template("login.html", title="Server Login", message=None, token=csrf_token())


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
