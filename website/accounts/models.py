from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import false

from website import bcrypt, db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    profile = db.relationship(
        "Profile", uselist=False, backref="user", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        email,
        password,
        is_admin=False,
        is_confirmed=False,
        confirmed_on=None,
    ):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, rounds=10).decode(
            "utf-8"
        )
        self.created_on = datetime.now()
        self.is_admin = is_admin
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on

    def __repr__(self):
        return f"<email {self.email}>"


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String)
    age = db.Column(db.Integer)
    bio = db.Column(db.Text)
    photo = db.Column(db.String)

    def __init__(self, user_id, full_name, age, bio, photo):
        self.user_id = user_id
        self.full_name = full_name
        self.age = age
        self.bio = bio
        self.photo = photo
