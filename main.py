from flask.cli import FlaskGroup

from website import app, db
from website.accounts.models import User

import unittest
import getpass
from datetime import datetime


app = FlaskGroup(app)


@app.command("test")
def test():
    tests = unittest.TestLoader().discover("tests")
    with open("other/log_test.txt", "w") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


@app.command("create_admin")
def create_admin():
    email = input("Enter email address: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")
    if password != confirm_password:
        print("Passwords don't match")
    else:
        try:
            user = User(
                email=email,
                password=password,
                is_admin=True,
                is_confirmed=True,
                confirmed_on=datetime.now(),
            )
            db.session.add(user)
            db.session.commit()
            print(f"Admin with email {email} created successfully!")
        except Exception as e:
            print("Couldn't create admin user.")
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    app()
