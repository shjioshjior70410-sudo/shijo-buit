"""
BuildPulse - FastAPI Application Entrypoint.
Serves REST API, Static Web Assets, and Intelligent Construction Analytics.
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.config import FRONTEND_DIR
from backend.database import db_client
from backend.routers import auth_routes, project_routes

app = FastAPI(
    title="BuildPulse - Construction Intelligence Platform",
    description="Intelligent project management, delay risk scoring, and what-if simulation engine for construction tracking.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth_routes.router)
app.include_router(project_routes.router)


@app.get("/api/health")
def health_check():
    """System health check endpoint."""
    return {"status": "healthy", "service": "BuildPulse Backend"}


@app.get("/api/status")
def system_status():
    """Returns database backend status and connectivity details."""
    return db_client.get_status()


import socket


def get_local_ip():
    """Detects the primary local network IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


@app.get("/api/network-info")
def network_info():
    """Returns local network IP and Android mobile access URL."""
    ip = get_local_ip()
    port = 8000
    return {
        "localIp": ip,
        "port": port,
        "mobileUrl": f"http://{ip}:{port}",
        "mobileLoginUrl": f"http://{ip}:{port}/login"
    }


@app.get("/manifest.json")
def get_manifest():
    """Serves Web App Manifest for Android PWA installation."""
    manifest_path = FRONTEND_DIR / "manifest.json"
    if manifest_path.exists():
        return FileResponse(str(manifest_path), media_type="application/manifest+json")
    return {"name": "BuildPulse", "short_name": "BuildPulse"}


# --- Static Frontend Serving ---
# Mount css, js, assets if FRONTEND_DIR exists
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


@app.get("/")
def serve_dashboard():
    """Serves the main construction analytics dashboard."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "BuildPulse API is running. Frontend index.html not found."}


@app.get("/login")
def serve_login():
    """Serves the login & authentication page."""
    login_path = FRONTEND_DIR / "login.html"
    if login_path.exists():
        return FileResponse(str(login_path))
    return FileResponse(str(FRONTEND_DIR / "index.html"))
