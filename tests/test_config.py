import os
import unittest

from website import app


class TestConfig(unittest.TestCase):
    def test_config(self):
        self.assertTrue(app.config["DEBUG"])
        self.assertTrue(app.config["SECRET_KEY"] is not None)


if __name__ == "__main__":
    unittest.main()
