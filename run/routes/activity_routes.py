from flask import Blueprint, abort, render_template, request
from services.activity_logger import fields, read_activity
from services.auth_service import admin_required

bp = Blueprint("activity", __name__)


@bp.route("/manage-delete/activity")
@admin_required
def activity_log():
    search_query = request.args.get("q", "").strip()
    records = read_activity({})
    if records is None: abort(500, "Could not read the activity log")
    return render_template("activity_log.html", title="Activity Log", search_query=search_query, records=records, fields=fields())
