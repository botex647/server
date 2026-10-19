import csv
import os
import threading
from datetime import datetime, timezone
from flask import current_app, request, session

_lock = threading.Lock()
_FIELDS = ["timestamp", "ip_address", "username", "role", "action", "item_type", "item_path", "status"]


def fields():
    return list(_FIELDS)


def log_activity(action, item_type, item_path, status="success"):
    path = current_app.config["ACTIVITY_LOG_PATH"]
    record = {"timestamp": datetime.now(timezone.utc).astimezone().isoformat(), "ip_address": request.remote_addr or "unknown", "username": session.get("username", ""), "role": session.get("role", ""), "action": action, "item_type": item_type, "item_path": item_path.replace("\\", "/"), "status": status}
    with _lock:
        exists = os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as log:
            writer = csv.DictWriter(log, fieldnames=_FIELDS)
            if not exists or os.path.getsize(path) == 0:
                writer.writeheader()
            writer.writerow(record)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


def read_activity(filters, limit=None):
    path = current_app.config["ACTIVITY_LOG_PATH"]
    if not os.path.exists(path):
        return []
    with _lock:
        try:
            with open(path, "r", newline="", encoding="utf-8") as log:
                rows = list(csv.DictReader(log))
        except (OSError, csv.Error):
            return None
    records = []
    for row in reversed(rows):
        if all(not value or value.casefold() in row.get(key, "").casefold() for key, value in filters.items()):
            records.append(row)
            if limit is not None and len(records) >= limit:
                break
    return records
