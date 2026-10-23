"""Email + password accounts, cookie sessions, and per-user personalization.

Provider-agnostic on purpose: preferences and interactions hang off users.id, so Reddit/Google
identities can later be linked to the same user (see user_identities note in the PR).
"""
import hashlib
import hmac
import os
import re
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Literal, Optional, Tuple

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/api")

SESSION_COOKIE = "newsea_session"
SESSION_TTL = timedelta(days=30)
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2**14, 8, 1
RATE_LIMIT_ATTEMPTS = 10
RATE_LIMIT_WINDOW_SECONDS = 15 * 60
MAX_TAGS = 20
MAX_EVENTS_PER_REQUEST = 500
TAG_PATTERN = re.compile(r"^[a-z0-9-]{1,40}$")

GENERIC_LOGIN_ERROR = "Incorrect email or password"
GENERIC_REGISTER_ERROR = "Unable to create an account with these details"
RATE_LIMITED_ERROR = "Too many attempts. Please try again later."


# ---------- passwords ----------
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: Optional[str]) -> bool:
    try:
        scheme, n, r, p, salt_hex, digest_hex = (stored or "").split("$")
        if scheme != "scrypt":
            return False
        digest = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p), dklen=len(digest_hex) // 2
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except ValueError:
        return False


# Verified against when the email is unknown, so response time does not reveal registered emails.
_DUMMY_HASH = hash_password(secrets.token_hex(16))


# ---------- rate limiting ----------
class RateLimiter:
    # shortcut: in-memory and per-process; move to the database or Redis when running multiple API instances.
    def __init__(self, attempts: int = RATE_LIMIT_ATTEMPTS, window_seconds: int = RATE_LIMIT_WINDOW_SECONDS):
        self.attempts = attempts
        self.window = window_seconds
        self.hits: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    def _recent(self, key: Tuple[str, str]) -> Deque[float]:
        hits = self.hits[key]
        cutoff = time.monotonic() - self.window
        while hits and hits[0] < cutoff:
            hits.popleft()
        return hits

    def check(self, *keys: Tuple[str, str]) -> None:
        if any(len(self._recent(key)) >= self.attempts for key in keys):
            raise HTTPException(status_code=429, detail=RATE_LIMITED_ERROR)

    def hit(self, *keys: Tuple[str, str]) -> None:
        now = time.monotonic()
        for key in keys:
            self.hits[key].append(now)


rate_limiter = RateLimiter()


# ---------- sessions ----------
def _db():
    from backend.api import main  # late import: main includes this router

    if not main.db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return main.db_manager


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _start_session(response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    _db().create_session(_token_hash(token), user_id, datetime.utcnow() + SESSION_TTL)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
        path="/api",
    )


def current_user(request: Request) -> Dict:
    token = request.cookies.get(SESSION_COOKIE)
    user = _db().get_user_by_session(_token_hash(token)) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Not signed in")
    return user


def _client_key(request: Request) -> Tuple[str, str]:
    return ("ip", request.client.host if request.client else "unknown")


# ---------- schemas ----------
class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)


class Preferences(BaseModel):
    interest_tags: List[str] = Field(default_factory=list, max_length=MAX_TAGS)


class InteractionEvent(BaseModel):
    card_id: str = Field(min_length=1, max_length=200)
    type: Literal["like", "unlike", "save", "unsave", "hide", "unhide"]


class InteractionBatch(BaseModel):
    events: List[InteractionEvent] = Field(max_length=MAX_EVENTS_PER_REQUEST)


def fold_interactions(events: List[Dict]) -> Dict[str, List[str]]:
    """Replay events oldest-first into the current liked/saved/hidden card sets."""
    state: Dict[str, Dict[str, None]] = {"liked": {}, "saved": {}, "hidden": {}}
    toggles = {
        "like": ("liked", True), "unlike": ("liked", False),
        "save": ("saved", True), "unsave": ("saved", False),
        "hide": ("hidden", True), "unhide": ("hidden", False),
    }
    for event in events:
        bucket, active = toggles[event["type"]]
        state[bucket].pop(event["card_id"], None)
        if active:
            state[bucket][event["card_id"]] = None
    return {bucket: list(ids) for bucket, ids in state.items()}


# ---------- endpoints ----------
@router.post("/auth/register", status_code=201)
async def register(credentials: Credentials, request: Request, response: Response):
    email = str(credentials.email).strip().lower()
    keys = (_client_key(request), ("email", email))
    rate_limiter.check(*keys)
    rate_limiter.hit(*keys)
    if len(credentials.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status_code=422, detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    user = _db().create_user(email, hash_password(credentials.password))
    if not user:
        raise HTTPException(status_code=400, detail=GENERIC_REGISTER_ERROR)
    _start_session(response, user["id"])
    return {"id": user["id"], "email": user["email"]}


@router.post("/auth/login")
async def login(credentials: Credentials, request: Request, response: Response):
    email = str(credentials.email).strip().lower()
    keys = (_client_key(request), ("email", email))
    rate_limiter.check(*keys)
    user = _db().get_user_by_email(email)
    password_ok = verify_password(credentials.password, user["password_hash"] if user else _DUMMY_HASH)
    if not user or not password_ok:
        rate_limiter.hit(*keys)
        raise HTTPException(status_code=401, detail=GENERIC_LOGIN_ERROR)
    _start_session(response, user["id"])
    return {"id": user["id"], "email": user["email"]}


@router.post("/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        _db().delete_session(_token_hash(token))
    response.delete_cookie(SESSION_COOKIE, path="/api")
    return {"status": "signed_out"}


@router.get("/me")
async def me(request: Request):
    user = current_user(request)
    return {"id": user["id"], "email": user["email"]}


@router.get("/me/preferences")
async def get_preferences(request: Request):
    user = current_user(request)
    return {"interest_tags": _db().get_interest_tags(user["id"])}


@router.put("/me/preferences")
async def put_preferences(preferences: Preferences, request: Request):
    user = current_user(request)
    tags = list(dict.fromkeys(tag.strip().lower() for tag in preferences.interest_tags))
    if not all(TAG_PATTERN.match(tag) for tag in tags):
        raise HTTPException(status_code=422, detail="Invalid interest tag")
    _db().set_interest_tags(user["id"], tags)
    return {"interest_tags": tags}


@router.get("/me/interactions")
async def get_interactions(request: Request):
    user = current_user(request)
    return fold_interactions(_db().get_interaction_events(user["id"]))


@router.post("/me/interactions")
async def post_interactions(batch: InteractionBatch, request: Request):
    user = current_user(request)
    events = [event.model_dump() for event in batch.events]
    _db().add_interactions(user["id"], events)
    return fold_interactions(_db().get_interaction_events(user["id"]))
