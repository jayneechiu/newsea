"""Account, session, and personalization API tests (no database or network needed)."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api import auth, main


class FakeDatabase:
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.tags = {}
        self.events = {}

    def create_user(self, email, password_hash):
        if email in self.users:
            return None
        user = {"id": len(self.users) + 1, "email": email, "password_hash": password_hash}
        self.users[email] = user
        return {"id": user["id"], "email": email}

    def get_user_by_email(self, email):
        return self.users.get(email)

    def create_session(self, token_hash, user_id, expires_at):
        self.sessions[token_hash] = user_id

    def get_user_by_session(self, token_hash):
        user_id = self.sessions.get(token_hash)
        user = next((u for u in self.users.values() if u["id"] == user_id), None)
        return {"id": user["id"], "email": user["email"]} if user else None

    def delete_session(self, token_hash):
        self.sessions.pop(token_hash, None)

    def get_interest_tags(self, user_id):
        return self.tags.get(user_id, [])

    def set_interest_tags(self, user_id, tags):
        self.tags[user_id] = tags

    def add_interactions(self, user_id, events):
        self.events.setdefault(user_id, []).extend(events)

    def get_interaction_events(self, user_id):
        return self.events.get(user_id, [])


class AuthApiTests(unittest.TestCase):
    def setUp(self):
        self.database = FakeDatabase()
        for patcher in (
            patch.object(main, "db_manager", self.database),
            patch.object(auth, "rate_limiter", auth.RateLimiter()),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.client = TestClient(main.app)

    def register(self, email="Reader@Example.com", password="correct horse"):
        return self.client.post("/api/auth/register", json={"email": email, "password": password})

    def test_password_hash_round_trip(self):
        stored = auth.hash_password("s3cret-pass")
        self.assertNotIn("s3cret-pass", stored)
        self.assertTrue(auth.verify_password("s3cret-pass", stored))
        self.assertFalse(auth.verify_password("wrong", stored))
        self.assertFalse(auth.verify_password("anything", None))

    def test_register_signs_in_with_httponly_cookie(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "reader@example.com")
        self.assertIn("httponly", response.headers["set-cookie"].lower())
        self.assertEqual(self.client.get("/api/me").json()["email"], "reader@example.com")

    def test_duplicate_register_and_short_password_are_rejected(self):
        self.register()
        self.assertEqual(self.register().json()["detail"], auth.GENERIC_REGISTER_ERROR)
        self.assertEqual(self.register("new@example.com", "short").status_code, 422)

    def test_login_errors_do_not_reveal_whether_email_exists(self):
        self.register()
        self.client.cookies.clear()
        wrong_password = self.client.post("/api/auth/login", json={"email": "reader@example.com", "password": "nope-nope"})
        unknown_email = self.client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "nope-nope"})
        self.assertEqual(wrong_password.status_code, 401)
        self.assertEqual(wrong_password.json(), unknown_email.json())
        self.assertEqual(self.client.get("/api/me").status_code, 401)

    def test_login_then_logout_invalidates_session(self):
        self.register()
        self.client.cookies.clear()
        sessions_before_login = dict(self.database.sessions)
        login = self.client.post("/api/auth/login", json={"email": "READER@example.com", "password": "correct horse"})
        self.assertEqual(login.status_code, 200)
        self.assertEqual(self.client.get("/api/me").status_code, 200)
        self.client.post("/api/auth/logout")
        self.assertEqual(self.database.sessions, sessions_before_login)
        self.assertEqual(self.client.get("/api/me").status_code, 401)

    def test_unknown_session_cookie_is_rejected(self):
        self.client.cookies.set(auth.SESSION_COOKIE, "forged-token", path="/api")
        self.assertEqual(self.client.get("/api/me").status_code, 401)

    def test_repeated_failed_logins_are_rate_limited(self):
        for _ in range(auth.RATE_LIMIT_ATTEMPTS):
            self.client.post("/api/auth/login", json={"email": "a@example.com", "password": "bad-pass"})
        response = self.client.post("/api/auth/login", json={"email": "a@example.com", "password": "bad-pass"})
        self.assertEqual(response.status_code, 429)

    def test_preferences_require_login_and_valid_tags(self):
        self.assertEqual(self.client.get("/api/me/preferences").status_code, 401)
        self.register()
        saved = self.client.put("/api/me/preferences", json={"interest_tags": ["Food", "money", "food"]})
        self.assertEqual(saved.json()["interest_tags"], ["food", "money"])
        self.assertEqual(self.client.get("/api/me/preferences").json()["interest_tags"], ["food", "money"])
        bad = self.client.put("/api/me/preferences", json={"interest_tags": ["<script>"]})
        self.assertEqual(bad.status_code, 422)

    def test_interactions_fold_to_latest_state(self):
        self.register()
        events = [
            {"card_id": "a", "type": "like"},
            {"card_id": "b", "type": "save"},
            {"card_id": "a", "type": "unlike"},
            {"card_id": "c", "type": "hide"},
            {"card_id": "c", "type": "unhide"},
            {"card_id": "d", "type": "hide"},
        ]
        state = self.client.post("/api/me/interactions", json={"events": events}).json()
        self.assertEqual(state, {"liked": [], "saved": ["b"], "hidden": ["d"]})
        self.assertEqual(self.client.get("/api/me/interactions").json(), state)
        bad = self.client.post("/api/me/interactions", json={"events": [{"card_id": "x", "type": "dwell"}]})
        self.assertEqual(bad.status_code, 422)


if __name__ == "__main__":
    unittest.main()
