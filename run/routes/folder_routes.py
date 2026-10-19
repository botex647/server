import os
from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
from services.activity_logger import log_activity
from services.auth_service import admin_required, csrf_token, valid_csrf, login_required
from services.file_service import get_all_folders, get_root_folders, is_symlink_path, safe_path

bp = Blueprint("folder", __name__)


@bp.route("/browse/<path:subpath>")
@bp.route("/browse/")
@bp.route("/")
@login_required
def index(subpath=""):
    current = safe_path(subpath)
    if is_symlink_path(subpath) or not os.path.isdir(current): abort(404)
    items = []
    for name in sorted(os.listdir(current), key=str.lower):
        full = os.path.join(current, name)
        if os.path.islink(full): continue
        relative = os.path.relpath(full, current_app.config["FOLDER"]).replace("\\", "/")
        extension = os.path.splitext(name)[1].lower()
        is_dir = os.path.isdir(full)
        if is_dir: kind, icon, link = "Folder", "📁", url_for("folder.index", subpath=relative)
        elif extension in current_app.config["VIDEO_EXT"]: kind, icon, link = "Video", "🎬", url_for("file.watch", filename=relative)
        elif extension == ".pdf": kind, icon, link = "PDF document", "📕", url_for("file.view_pdf", filename=relative)
        elif extension in current_app.config["DOC_EXT"]: kind, icon, link = "Document · Download", "📄", url_for("file.download_file", filename=relative)
        else: kind, icon, link = "File · Download", "📦", url_for("file.download_file", filename=relative)
        items.append({"name": name, "kind": kind, "icon": icon, "url": link, "is_dir": is_dir})
    normalized = subpath.replace("\\", "/").strip("/")
    breadcrumbs, cumulative = [], []
    for component in normalized.split("/"):
        if component:
            cumulative.append(component)
            breadcrumbs.append({"name": component, "url": url_for("folder.index", subpath="/".join(cumulative))})
    parent = os.path.dirname(normalized) if normalized else None
    return render_template("index.html", title="My Library", subpath=subpath, parent=parent, items=items, breadcrumb_items=breadcrumbs, root_folders=get_root_folders())


@bp.route("/upload", methods=["GET", "POST"])
@admin_required
def upload():
    if request.method == "POST":
        if not valid_csrf(): abort(400, "Invalid form token. Reload the page.")
        target = request.form.get("folder", "")
        destination = safe_path(target)
        if is_symlink_path(target) or not os.path.isdir(destination): abort(400, "Invalid destination folder")
        uploaded_files = request.files.getlist("files")
        if not uploaded_files or all(not file.filename for file in uploaded_files): abort(400, "Please select at least one file")
        saved = []
        for file in uploaded_files:
            if not file.filename: continue
            filename = secure_filename(file.filename)
            if not filename: continue
            base, extension = os.path.splitext(filename)
            candidate, counter = filename, 1
            while os.path.exists(os.path.join(destination, candidate)):
                candidate = f"{base}_{counter}{extension}"
                counter += 1
            file.save(os.path.join(destination, candidate))
            saved.append(candidate)
            log_activity("upload", "file", os.path.join(target, candidate))
        return render_template("upload_complete.html", title="Upload Complete", saved=saved, target=target)
    return render_template("upload.html", title="Upload Files", folders=get_all_folders(), token=csrf_token())


@bp.route("/new-folder", methods=["GET", "POST"])
@admin_required
def new_folder():
    if request.method == "POST":
        if not valid_csrf(): abort(400, "Invalid form token. Reload the page.")
        parent = request.form.get("parent", "")
        name = request.form.get("folder_name", "").strip()
        parent_path = safe_path(parent)
        if is_symlink_path(parent) or not os.path.isdir(parent_path): abort(400, "Invalid parent folder")
        invalid_chars = '<>:"/\\|?*'
        if not name or name in {".", ".."} or any(char in invalid_chars for char in name) or any(ord(char) < 32 for char in name) or name.endswith((" ", ".")) or len(name) > 100: abort(400, "Invalid folder name")
        new_path = os.path.join(parent_path, name)
        if os.path.exists(new_path): abort(400, "A file or folder with that name already exists")
        try: os.mkdir(new_path)
        except OSError: abort(400, "Could not create the folder")
        relative = os.path.relpath(new_path, current_app.config["FOLDER"]).replace("\\", "/")
        log_activity("create", "folder", relative)
        return redirect(url_for("folder.index", subpath=parent))
    return render_template("folder.html", title="Create Folder", folders=get_all_folders(), token=csrf_token())
