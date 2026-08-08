"""Approval and recipient-safety tests for the newsletter API."""

import asyncio
import os
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from fastapi import BackgroundTasks, HTTPException

from backend.api import main


class FakeDatabase:
    def __init__(self):
        self.requests = []
        self.recipients = []

    def request_newsletter_subscription(self, email, subreddits, name=None):
        record = {
            "id": len(self.requests) + 1,
            "email": email.lower(),
            "subreddits": subreddits,
            "name": name,
            "status": "pending",
            "is_active": False,
        }
        self.requests.append(record)
        return record

    def get_approved_newsletter_recipients(self):
        return self.recipients


class NewsletterApprovalTests(unittest.TestCase):
    def test_public_application_is_pending_and_inactive(self):
        database = FakeDatabase()
        request = main.SubscribeRequest(email="Reader@Example.com", subreddits=["technology"])
        with patch.object(main, "db_manager", database):
            response = asyncio.run(main.subscribe(request))

        self.assertEqual(response["status"], "pending")
        self.assertEqual(database.requests[0]["email"], "reader@example.com")
        self.assertFalse(database.requests[0]["is_active"])

    def test_admin_key_is_required(self):
        with patch.dict(os.environ, {"NEWSLETTER_ADMIN_KEY": "expected-secret"}):
            with self.assertRaises(HTTPException) as error:
                main.require_admin("wrong-secret")

        self.assertEqual(error.exception.status_code, 401)

    def test_campaign_refuses_to_send_without_approved_recipients(self):
        database = FakeDatabase()
        with ExitStack() as stack:
            stack.enter_context(patch.object(main, "db_manager", database))
            stack.enter_context(patch.object(main, "reddit_scraper", object()))
            stack.enter_context(patch.object(main, "chatgpt_client", object()))
            stack.enter_context(patch.object(main, "newsletter_sender", object()))
            stack.enter_context(patch.object(main, "newsletter_composer", object()))
            stack.enter_context(patch.dict(os.environ, {"NEWSLETTER_ADMIN_KEY": "expected-secret"}))
            with self.assertRaises(HTTPException) as error:
                asyncio.run(
                    main.send_newsletter(
                        BackgroundTasks(),
                        main.NewsletterRequest(subreddit="technology"),
                        "expected-secret",
                    )
                )

        self.assertEqual(error.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
