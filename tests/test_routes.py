import unittest
from website import app, db
from website.accounts.models import User
from website.accounts.forms import RegisterForm, LoginForm, ProfileForm


class TestRoutes(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_route(self):
        response = self.client.post(
            "/register",
            data={
                "email": "test@example.com",
                "password": "password",
                "confirm": "password",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        user = User.query.filter_by(email="test@example.com").first()
        self.assertIsNotNone(user)

    def test_login_route(self):
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_logout_route(self):
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess["user_id"] = user.id

        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
