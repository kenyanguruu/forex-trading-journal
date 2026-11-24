from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Database connection
db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    google_id = db.Column(
        db.String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Trade(db.Model):

    __tablename__ = "trades"

    id = db.Column(db.String(32), primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    trade_data = db.Column(db.JSON, nullable=False)


class OTPCode(db.Model):

    __tablename__ = "otp_codes"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), nullable=False, index=True)

    purpose = db.Column(db.String(30), nullable=False, index=True)

    code_hash = db.Column(db.String(256), nullable=False)

    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
    )

    attempts = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    is_used = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def set_code(self, code):
        self.code_hash = generate_password_hash(code)

    def check_code(self, code):
        return check_password_hash(self.code_hash, code)
