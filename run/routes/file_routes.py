import os
from flask import Blueprint, abort, current_app, render_template, send_from_directory
from services.auth_service import login_required
from services.file_service import is_symlink_path, safe_path

bp = Blueprint("file", __name__)


@bp.route("/watch/<path:filename>")
@login_required
def watch(filename):
    path = safe_path(filename)
    if is_symlink_path(filename) or not os.path.isfile(path): abort(404)
    if os.path.splitext(filename)[1].lower() not in current_app.config["VIDEO_EXT"]: abort(400, "Unsupported video extension")
    return render_template("video.html", title="Video Player", filename=filename)


@bp.route("/pdf/<path:filename>")
@login_required
def view_pdf(filename):
    path = safe_path(filename)
    if is_symlink_path(filename) or not os.path.isfile(path): abort(404)
    if os.path.splitext(filename)[1].lower() != ".pdf": abort(400, "Not a PDF file")
    return render_template("pdf.html", title="PDF Reader", filename=filename)


@bp.route("/files/<path:filename>")
@login_required
def serve_file(filename):
    path = safe_path(filename)
    if is_symlink_path(filename) or not os.path.isfile(path): abort(404)
    return send_from_directory(current_app.config["FOLDER"], filename, conditional=True)


@bp.route("/download/<path:filename>")
@login_required
def download_file(filename):
    path = safe_path(filename)
    if is_symlink_path(filename) or not os.path.isfile(path): abort(404)
    return send_from_directory(current_app.config["FOLDER"], filename, as_attachment=True)
