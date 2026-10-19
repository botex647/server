from datetime import timedelta
import os
from flask import Flask, render_template
from dotenv import load_dotenv

from routes.auth_routes import bp as auth_bp
from routes.file_routes import bp as file_bp
from routes.folder_routes import bp as folder_bp
from routes.search_routes import bp as search_bp
from routes.admin_routes import bp as admin_bp
from routes.activity_routes import bp as activity_bp

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

app = Flask(__name__)
FOLDER = os.path.realpath(r"D:\server\server_share")
VIDEO_EXT = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"}
DOC_EXT = {".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"}
app.config.update(
    FOLDER=FOLDER,
    VIDEO_EXT=VIDEO_EXT,
    DOC_EXT=DOC_EXT,
    MAX_CONTENT_LENGTH=10 * 1024 * 1024 * 1024,
    MAX_FORM_MEMORY_SIZE=1024 * 1024,
    SECRET_KEY=os.environ.get("FILE_SERVER_SECRET_KEY"),
    VIEWER_USERNAME=os.environ.get("FILE_SERVER_VIEWER_USERNAME"),
    VIEWER_PASSWORD=os.environ.get("FILE_SERVER_VIEWER_PASSWORD"),
    ADMIN_USERNAME=os.environ.get("FILE_SERVER_ADMIN_USERNAME"),
    ADMIN_PASSWORD=os.environ.get("FILE_SERVER_ADMIN_PASSWORD"),
    ACTIVITY_LOG_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)), "activity_log.csv"),
    LOGIN_ATTEMPT_WINDOW=300,
    LOGIN_ATTEMPT_LIMIT=5,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FILE_SERVER_HTTPS", "").strip().lower() in {"1", "true", "yes", "on"},
)
required = {
    "FILE_SERVER_VIEWER_USERNAME": app.config["VIEWER_USERNAME"],
    "FILE_SERVER_VIEWER_PASSWORD": app.config["VIEWER_PASSWORD"],
    "FILE_SERVER_ADMIN_USERNAME": app.config["ADMIN_USERNAME"],
    "FILE_SERVER_ADMIN_PASSWORD": app.config["ADMIN_PASSWORD"],
    "FILE_SERVER_SECRET_KEY": app.config["SECRET_KEY"],
}
missing_config = [name for name, value in required.items() if not value]
if missing_config:
    raise RuntimeError("Missing required file server configuration: " + ", ".join(missing_config) + ". Set these values in .env before starting the server.")

app.register_blueprint(auth_bp)
app.register_blueprint(file_bp)
app.register_blueprint(folder_bp)
app.register_blueprint(search_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(activity_bp)


@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", title="Bad Request", message=getattr(error, "description", "Invalid request")), 400


@app.errorhandler(403)
def forbidden(error):
    return render_template("error.html", title="Access Denied", message="You do not have permission to access this resource."), 403


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", title="Not Found", message="The resource may have been moved or deleted."), 404


@app.errorhandler(413)
def too_large(error):
    return render_template("error.html", title="Upload Too Large", message="The maximum request size is 10 GB."), 413


if __name__ == "__main__":
    if not os.path.isdir(FOLDER):
        raise SystemExit(f"Shared folder not found: {FOLDER}")
    print("=" * 50)
    print("BOTEX PERSONAL FILE SERVER")
    print("=" * 50)
    print(f"Shared folder: {FOLDER}")
    print("Local:           http://127.0.0.1:6789/")
    print("Network:         http://192.168.1.48:6789/")
    print("Upload:          http://192.168.1.48:6789/upload")
    print("Create folder:   http://192.168.1.48:6789/new-folder")
    print("Manage delete:   http://192.168.1.48:6789/manage-delete")
    print("=" * 50)
    app.run(host="0.0.0.0", port=6789, threaded=True, debug=False)
