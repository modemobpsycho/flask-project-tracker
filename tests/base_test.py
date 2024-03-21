import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import TestingConfig
from website.accounts.models import User


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(TestingConfig)

        self.db = SQLAlchemy(self.app)

        self.db.create_all()

        unconfirmed_user = User(
            email="unconfirmeduser@gmail.com", password="unconfirmeduser"
        )
        confirmed_user = User(
            email="confirmeduser@gmail.com", password="confirmeduser", is_confirmed=True
        )

        self.db.session.add(unconfirmed_user)
        self.db.session.add(confirmed_user)
        self.db.session.commit()

    def tearDown(self):
        # self.db.session.remove()

        # self.db.drop_all()

        # testdb_path = os.path.join("website", "test.db")
        # if os.path.exists(testdb_path):
        #     os.remove(testdb_path)


if __name__ == "__main__":
    unittest.main()
