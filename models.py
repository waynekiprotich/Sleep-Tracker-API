from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    sleep_entries = db.relationship("SleepEntry", backref="user", cascade="all, delete")

    @property
    def password(self):
        raise AttributeError("Password not readable")

    @password.setter
    def password(self, plain_password):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password_hash, plain_password)


class SleepEntry(db.Model):
    __tablename__ = "sleep_entries"

    id = db.Column(db.Integer, primary_key=True)
    sleep_time = db.Column(db.DateTime, nullable=False)
    wake_time = db.Column(db.DateTime, nullable=False)
    quality = db.Column(db.Integer)
    notes = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))