# BOTEX Personal File Server

BOTEX is a private Flask-based file server for browsing, searching, viewing, and
managing a shared folder. It supports separate viewer and administrator logins,
file and folder search, uploads, folder creation, protected file viewing, and
activity logging.

## Requirements

- Python 3.10 or newer
- A local folder to share
- Windows or another operating system supported by Python and Flask

Python dependencies are listed in `requirements.txt`.

## Installation

1. Open a terminal in this directory:

   ```powershell
   cd D:\server\run
   ```

2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and replace every placeholder with secure
   values.

## Configuration

The application requires these environment variables:

| Variable | Purpose |
| --- | --- |
| `FILE_SERVER_VIEWER_USERNAME` | Username for read-only viewer access |
| `FILE_SERVER_VIEWER_PASSWORD` | Password for read-only viewer access |
| `FILE_SERVER_ADMIN_USERNAME` | Username for administrator access |
| `FILE_SERVER_ADMIN_PASSWORD` | Password for administrator access |
| `FILE_SERVER_SECRET_KEY` | Secret used to protect Flask sessions and CSRF tokens |
| `FILE_SERVER_HTTPS` | Set to `1`, `true`, `yes`, or `on` when served over HTTPS |

The shared folder is configured in `server.py` through the `FOLDER` setting.
Update it to the absolute path that should be exposed before starting the
server. Do not place `.env` or other secrets inside the shared folder.

## Running

From the `run` directory, with the virtual environment activated:

```powershell
python server.py
```

The default addresses are:

- Local: `http://127.0.0.1:6789/`
- Network: `http://192.168.1.48:6789/`

The network address depends on the host machine's local IP address. The server
listens on all interfaces, so restrict access with a firewall or reverse proxy
when it is not intended to be available to the whole network.

## Features

- Login with viewer or administrator roles
- Session-based authentication with CSRF protection
- Login-attempt throttling
- Browse folders and protected files
- Search files and folders by name
- View supported videos and PDFs in the browser
- Administrator-only upload and folder creation
- Administrator-only file and folder deletion
- CSV activity logging
- Light and dark themed responsive interface
- Circular search button with an accessible magnifying-glass image
- Password visibility toggle on the login page

## Project structure

```text
run/
├── server.py                 Flask application entry point
├── requirements.txt          Python dependencies
├── .env.example              Configuration template
├── routes/                   Flask route blueprints
├── services/                 Authentication, file, and activity services
├── templates/                Jinja2 HTML templates
└── static/
    ├── css/style.css         Application styles
    ├── images/search.svg     Search button icon
    └── js/admin.js           Administrator page behavior
```

## Security notes

- Use long, unique passwords and a random `FILE_SERVER_SECRET_KEY`.
- Use HTTPS when the server is reachable beyond a trusted local network.
- Keep `.env` out of source control and backups that are shared publicly.
- The administrator role can upload and delete files; only give it to trusted
  users.
- Review `activity_log.csv` periodically if audit history is important.

## Development checks

Run a Python syntax check after changes:

```powershell
python -m compileall -q server.py routes services
```
