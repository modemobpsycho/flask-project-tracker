import unittest
from website import create_app, db
from website.accounts.models import User, Profile
from datetime import datetime


class TestModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_creation(self):
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)

    def test_profile_creation(self):
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()
        profile = Profile(
            user_id=user.id, full_name="Test User", age=25, bio="Some bio"
        )
        db.session.add(profile)
        db.session.commit()
        self.assertIsNotNone(profile.id)


if __name__ == "__main__":
    unittest.main()
