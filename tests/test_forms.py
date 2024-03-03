import unittest

from base_test import BaseTestCase

from website.accounts.forms import LoginForm, RegisterForm


class TestRegisterForm(BaseTestCase):
    def test_validate_success_register_form(self):
        form = RegisterForm(email="new@test.com", password="example", confirm="example")
        self.assertTrue(form.validate())

    def test_validate_invalid_password_format(self):
        form = RegisterForm(email="new@test.com", password="example", confirm="")
        self.assertFalse(form.validate())

    def test_validate_email_already_registered(self):
        form = RegisterForm(
            email="unconfirmeduser@gmail.com",
            password="unconfirmeduser",
            confirm="unconfirmeduser",
        )
        self.assertFalse(form.validate())


class TestLoginForm(BaseTestCase):
    def test_validate_success_login_form(self):
        form = LoginForm(email="unconfirmeduser@gmail.com", password="unconfirmeduser")
        self.assertTrue(form.validate())

    def test_validate_invalid_email_format(self):
        form = LoginForm(email="unknown", password="example")
        self.assertFalse(form.validate())


if __name__ == "__main__":
    unittest.main()
