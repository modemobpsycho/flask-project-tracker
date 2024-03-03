import os

from flask_testing import TestCase

from website import app, db
from website.accounts.models import User


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def setUp(self):
        db.create_all()
        unconfirmed_user = User(
            email="unconfirmeduser@gmail.com", password="unconfirmeduser"
        )
        db.session.add(unconfirmed_user)
        confirmed_user = User(
            email="confirmeduser@gmail.com", password="confirmeduser", is_confirmed=True
        )
        db.session.add(confirmed_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        testdb_path = os.path.join("website", "testdb.sqlite")
        os.remove(testdb_path)
