import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

# Security / JWT
SECRET_KEY = os.getenv("SECRET_KEY", "buildpulse-super-secret-production-key-2026-xyz-987")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Firebase Settings
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", str(BASE_DIR / "serviceAccountKey.json"))
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "")
USE_MOCK_IF_FIREBASE_UNAVAILABLE = True
