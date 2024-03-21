import unittest
from website import create_app, db
from website.accounts.forms import RegisterForm, LoginForm, ProfileForm


class TestForms(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_form(self):
        form = RegisterForm(
            email="test@example.com", password="password", confirm="password"
        )
        self.assertTrue(form.validate(), "Register form validation failed.")

    def test_login_form(self):
        form = LoginForm(email="test@example.com", password="password")
        self.assertTrue(form.validate(), "Login form validation failed.")

    def test_profile_form(self):
        form = ProfileForm(full_name="Test User", age=25, bio="Some bio")
        self.assertTrue(form.validate(), "Profile form validation failed.")


if __name__ == "__main__":
    unittest.main()
