import os
from flask import abort, current_app, url_for


def shared_folder():
    return current_app.config["FOLDER"]


def safe_path(relative=""):
    root = shared_folder()
    path = os.path.realpath(os.path.join(root, relative))
    try:
        if os.path.commonpath([root, path]) != root:
            abort(403)
    except ValueError:
        abort(403)
    return path


def is_symlink_path(relative):
    current = shared_folder()
    for part in relative.replace("\\", "/").split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            return True
        current = os.path.join(current, part)
        if os.path.islink(current):
            return True
    return False


def get_root_folders():
    root = shared_folder()
    return sorted([name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name)) and not os.path.islink(os.path.join(root, name))], key=str.lower)


def get_all_folders():
    root = shared_folder()
    folders = [""]
    for current, dirs, _ in os.walk(root, followlinks=False):
        dirs[:] = sorted([name for name in dirs if not os.path.islink(os.path.join(current, name))], key=str.lower)
        for name in dirs:
            folders.append(os.path.relpath(os.path.join(current, name), root).replace("\\", "/"))
    return sorted(set(folders), key=str.lower)


def file_display_info(name, is_dir=False):
    if is_dir:
        return "Folder", "📁"
    extension = os.path.splitext(name)[1].lower()
    if extension in current_app.config["VIDEO_EXT"]:
        return "Video", "🎬"
    if extension == ".pdf":
        return "PDF document", "📕"
    if extension in current_app.config["DOC_EXT"]:
        return "Document", "📄"
    return "File", "📦"


def search_result_url(relative, is_dir):
    if is_dir:
        return url_for("folder.index", subpath=relative)
    extension = os.path.splitext(relative)[1].lower()
    if extension in current_app.config["VIDEO_EXT"]:
        return url_for("file.watch", filename=relative)
    if extension == ".pdf":
        return url_for("file.view_pdf", filename=relative)
    return url_for("file.download_file", filename=relative)


def iter_search_results(query):
    lowered = query.casefold()
    root = shared_folder()
    results = []
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted([name for name in dirs if not os.path.islink(os.path.join(current, name))], key=str.lower)
        for name in sorted(names, key=str.lower):
            full = os.path.join(current, name)
            if os.path.islink(full) or not os.path.isfile(full) or lowered not in name.casefold():
                continue
            relative = os.path.relpath(full, root).replace("\\", "/")
            kind, icon = file_display_info(name)
            results.append({"name": name, "path": relative, "kind": kind, "icon": icon, "url": search_result_url(relative, False)})
        for name in dirs:
            if lowered in name.casefold():
                relative = os.path.relpath(os.path.join(current, name), root).replace("\\", "/")
                results.append({"name": name, "path": relative, "kind": "Folder", "icon": "📁", "url": search_result_url(relative, True)})
    return sorted(results, key=lambda item: (item["name"].casefold(), item["path"].casefold()))


def build_delete_tree(directory=None):
    root = shared_folder()
    directory = root if directory is None else directory
    entries = []
    with os.scandir(directory) as scanned:
        children = sorted((entry for entry in scanned if not entry.is_symlink()), key=lambda entry: (not entry.is_dir(follow_symlinks=False), entry.name.lower()))
        for entry in children:
            relative = os.path.relpath(entry.path, root).replace("\\", "/")
            if entry.is_dir(follow_symlinks=False):
                entries.append({"name": entry.name, "path": relative, "kind": "Folder", "icon": "📁", "is_dir": True, "children": build_delete_tree(entry.path)})
            elif entry.is_file(follow_symlinks=False):
                kind, icon = file_display_info(entry.name)
                entries.append({"name": entry.name, "path": relative, "kind": kind, "icon": icon, "is_dir": False})
    return entries


def contains_symlink(directory):
    for root, dirs, files in os.walk(directory, followlinks=False):
        if any(os.path.islink(os.path.join(root, name)) for name in dirs + files):
            return True
    return False
