from datetime import datetime
import unittest

from base_test import BaseTestCase
from flask_login import current_user
from website.accounts.models import User
from website import db

from website.accounts.token import confirm_token, generate_token


class TestPublic(BaseTestCase):
    def test_main_route_requires_login(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertIn(b"Please log in to access this page", response.data)

    def test_logout_route_requires_login(self):
        response = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Please log in to access this page", response.data)


class TestLoggingInOut(BaseTestCase):
    def test_correct_login(self):
        with self.client:
            response = self.client.post(
                "/login",
                data=dict(
                    email="unconfirmeduser@gmail.com", password="unconfirmeduser"
                ),
                follow_redirects=True,
            )
            self.assertTrue(current_user.email == "unconfirmeduser@gmail.com")
            self.assertTrue(current_user.is_active)
            self.assertTrue(response.status_code == 200)

    def test_incorrect_login(self):
        with self.client:
            response = self.client.post(
                "/login",
                data=dict(email="not@correct.com", password="incorrect"),
                follow_redirects=True,
            )
            self.assertTrue(response.status_code == 200)
            self.assertIn(b"Invalid email and/or password.", response.data)

    def test_logout_behaves_correctly(self):
        with self.client:
            self.client.post(
                "/login",
                data=dict(
                    email="unconfirmeduser@gmail.com", password="unconfirmeduser"
                ),
                follow_redirects=True,
            )
            response = self.client.get("/logout", follow_redirects=True)
            self.assertIn(b"You were logged out.", response.data)
            self.assertFalse(current_user.is_active)

    def test_home_route_requires_login(self):
        self.client.get("/logout", follow_redirects=True)
        self.client.get("/", follow_redirects=True)
        self.assertTemplateUsed("accounts/login.html")


class TestEmailConfirmationToken(BaseTestCase):
    def test_confirm_token_route_requires_login(self):
        self.client.get("/logout", follow_redirects=True)
        self.client.get("/confirm/some-unique-id", follow_redirects=True)
        self.assertTemplateUsed("accounts/login.html")

    def test_confirm_token_route_valid_token(self):
        with self.client:
            self.client.get("/logout", follow_redirects=True)
            self.client.post(
                "/login",
                data=dict(
                    email="unconfirmeduser@gmail.com", password="unconfirmeduser"
                ),
                follow_redirects=True,
            )
            token = generate_token("unconfirmeduser@gmail.com")
            response = self.client.get("/confirm/" + token, follow_redirects=True)
            self.assertIn(b"You have confirmed your account. Thanks!", response.data)
            self.assertTemplateUsed("core/index.html")
            user = User.query.filter_by(
                email="unconfirmeduser@gmail.com"
            ).first_or_404()
            self.assertIsInstance(user.confirmed_on, datetime)
            self.assertTrue(user.is_confirmed)

    def test_confirm_token_route_invalid_token(self):
        token = generate_token("test@test1.com")
        with self.client:
            self.client.get("/logout", follow_redirects=True)
            self.client.post(
                "/login",
                data=dict(
                    email="unconfirmeduser@gmail.com", password="unconfirmeduser"
                ),
                follow_redirects=True,
            )
            response = self.client.get("/confirm/" + token, follow_redirects=True)
            self.assertIn(
                b"The confirmation link is invalid or has expired.", response.data
            )

    def test_confirm_token_route_expired_token(self):
        user = User(email="test@test1.com", password="test1")
        db.session.add(user)
        db.session.commit()
        token = generate_token("test@test1.com")
        self.assertFalse(confirm_token(token, -1))


if __name__ == "__main__":
    unittest.main()
