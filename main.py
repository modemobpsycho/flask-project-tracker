from flask.cli import FlaskGroup

from website import app, db
from website.accounts.models import User

import unittest
import getpass
from datetime import datetime


cli = FlaskGroup(app)


@cli.command("test")
def test():
    tests = unittest.TestLoader().discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


@cli.command("create_admin")
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
        except Exception:
            print("Couldn't create admin user.")


if __name__ == "__main__":
    cli()
