import unittest
from flask import url_for
from flask_testing import TestCase
from website import app, db
from website.accounts.models import User, Profile
from website.accounts.forms import RegisterForm, LoginForm, ProfileForm


class TestLogin(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def test_login_route_get(self):
        response = self.client.get(url_for("accounts.login"))
        self.assert200(response)

    def test_login_route_post(self):
        data = {"email": "test@example.com", "password": "password"}
        response = self.client.post(
            url_for("accounts.login"), data=data, follow_redirects=True
        )
        self.assert200(response)
