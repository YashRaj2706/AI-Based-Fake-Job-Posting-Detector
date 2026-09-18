import os
import sqlite3
from datetime import datetime, timedelta

import bcrypt
from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse, RedirectResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

# ── CONFIG ───────────────────────────────────────────────────────────────────
DB_PATH      = os.getenv("SQLITE_DB_PATH", "jobs_search.db")
JWT_SECRET   = os.getenv("JWT_SECRET", "fjd_super_secret_key_change_in_prod")
JWT_ALGO     = "HS256"
JWT_EXPIRE_H = 24
COOKIE_NAME  = "fjd_session"

PUBLIC_PATHS    = {"/", "/login", "/signup", "/favicon.ico"}
PUBLIC_PREFIXES = ("/static/", "/auth/")

# ── SQLITE HELPERS ─────────────────────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

# ── ROUTER ────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/auth", tags=["auth"])

# ── HELPERS ───────────────────────────────────────────────────────────────────
def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def _create_token(email: str, name: str) -> str:
    payload = {
        "sub":  email,
        "name": name,
        "exp":  datetime.utcnow() + timedelta(hours=JWT_EXPIRE_H),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def _decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        return None

def get_current_user(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return _decode_token(token)

# ── MIDDLEWARE ────────────────────────────────────────────────────────────────
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)

        user = get_current_user(request)
        if user is None:
            if path.startswith("/predict") or request.headers.get("content-type", "").startswith("application/json"):
                return JSONResponse(
                    {"ok": False, "error": "Not authenticated. Please log in."},
                    status_code=401
                )
            return RedirectResponse(url=f"/login?next={path}", status_code=302)

        request.state.user = user
        return await call_next(request)

# ── AUTH ROUTES ───────────────────────────────────────────────────────────────
@router.post("/signup")
async def signup(data: dict = Body(...)):
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not name or not email or not password:
        return JSONResponse({"ok": False, "error": "All fields are required"}, status_code=400)
    if len(password) < 8:
        return JSONResponse({"ok": False, "error": "Password must be at least 8 characters"}, status_code=400)
    if "@" not in email:
        return JSONResponse({"ok": False, "error": "Invalid email address"}, status_code=400)

    conn = get_db_connection()
    cursor = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return JSONResponse({"ok": False, "error": "An account with this email already exists"}, status_code=409)

    conn.execute(
        "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
        (name, email, _hash_password(password), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()

    token = _create_token(email, name)
    response = JSONResponse({"ok": True, "name": name, "email": email})
    response.set_cookie(
        key=COOKIE_NAME, value=token,
        httponly=True, samesite="lax",
        max_age=JWT_EXPIRE_H * 3600
    )
    return response

@router.post("/login")
async def login(data: dict = Body(...)):
    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return JSONResponse({"ok": False, "error": "Email and password are required"}, status_code=400)

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user or not _verify_password(password, user["password"]):
        return JSONResponse({"ok": False, "error": "Invalid email or password"}, status_code=401)

    token = _create_token(email, user["name"])
    response = JSONResponse({"ok": True, "name": user["name"], "email": email})
    response.set_cookie(
        key=COOKIE_NAME, value=token,
        httponly=True, samesite="lax",
        max_age=JWT_EXPIRE_H * 3600
    )
    return response

@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response

@router.get("/me")
async def me(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"ok": False, "error": "Not authenticated"}, status_code=401)
    return JSONResponse({"ok": True, "name": user["name"], "email": user["sub"]})