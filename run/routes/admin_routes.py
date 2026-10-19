import os
import shutil
from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from services.activity_logger import log_activity
from services.auth_service import admin_required, csrf_token, valid_csrf
from services.file_service import build_delete_tree, contains_symlink, is_symlink_path, safe_path, search_result_url

bp = Blueprint("admin", __name__)


@bp.route("/manage-delete")
@admin_required
def manage_delete_entry():
    return redirect(url_for("admin.delete_manager"))


@bp.route("/manage-delete/files")
@admin_required
def delete_manager():
    try: tree = build_delete_tree()
    except OSError: abort(500, "Could not read the shared folder")
    deleted = request.args.get("deleted", "").strip()
    if len(deleted) > 300: deleted = ""
    return render_template("manage_delete.html", title="File Management", tree=tree, search_result_url=search_result_url, deleted=deleted, token=csrf_token())


@bp.route("/manage-delete/delete", methods=["POST"])
@admin_required
def delete_file():
    if not valid_csrf(): abort(400, "Invalid security token. Reload the management page.")
    filename = request.form.get("filename", "").strip().replace("\\", "/")
    parts = filename.split("/")
    if not filename or os.path.isabs(filename) or any(part in {"", ".", ".."} for part in parts) or is_symlink_path(filename): abort(400, "Invalid file path")
    path = safe_path(filename)
    if not os.path.isfile(path): abort(404, "File not found")
    try: os.remove(path)
    except OSError: abort(400, "Could not delete the file")
    log_activity("delete", "file", filename)
    return redirect(url_for("admin.delete_manager", deleted=f"Deleted file: {filename}"))


@bp.route("/manage-delete/delete-folder", methods=["POST"])
@admin_required
def delete_folder():
    if not valid_csrf(): abort(400, "Invalid security token. Reload the management page.")
    foldername = request.form.get("foldername", "").strip().replace("\\", "/")
    parts = foldername.split("/")
    if not foldername or os.path.isabs(foldername) or any(part in {"", ".", ".."} for part in parts) or is_symlink_path(foldername): abort(400, "Invalid folder path")
    path = safe_path(foldername)
    if os.path.realpath(path) == current_app.config["FOLDER"] or not os.path.isdir(path) or os.path.islink(path): abort(400, "Invalid folder")
    if contains_symlink(path): abort(400, "Folders containing symbolic links cannot be deleted")
    try: shutil.rmtree(path)
    except OSError: abort(400, "Could not delete the folder")
    log_activity("delete", "folder", foldername)
    return redirect(url_for("admin.delete_manager", deleted=f"Deleted folder: {foldername}"))
