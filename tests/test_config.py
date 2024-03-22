import unittest
from website import app
from flask_testing import TestCase
from config import Config, TestingConfig


class TestConfig(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def test_config(self):
        self.assertFalse(Config.DEBUG)
        self.assertTrue(Config.CSRF_ENABLED)
        self.assertIsNotNone(Config.SECRET_KEY)
        self.assertFalse(Config.SQLALCHEMY_TRACK_MODIFICATIONS)
        self.assertEqual(Config.BCRYPT_LOG_ROUNDS, 10)
        self.assertTrue(Config.WTF_CSRF_ENABLED)
        self.assertFalse(Config.DEBUG_TB_ENABLED)
        self.assertFalse(Config.DEBUG_TB_INTERCEPT_REDIRECTS)
        self.assertEqual(Config.SECURITY_PASSWORD_SALT, "very-important")

    def test_development_config(self):
        with app.app_context():
            self.assertTrue(app.config["DEBUG"])
            self.assertFalse(app.config["WTF_CSRF_ENABLED"])

    def test_production_config(self):
        pass


if __name__ == "__main__":
    unittest.main()
