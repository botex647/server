from flask import Blueprint, abort, render_template, request
from services.auth_service import login_required
from services.file_service import iter_search_results

bp = Blueprint("search", __name__)


@bp.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    if len(query) > 100:
        abort(400, "Search query is too long")
    return render_template("search_results.html", title="Search", query=query, results=iter_search_results(query)[:200] if query else [])
