import os
from pathlib import Path

import pytest

# Get the absolute path of the test database.
TEST_DATABASE_PATH = Path(__file__).resolve().parent / "test_database.db"

# Configure an isolated SQLite database before importing the app.
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-automated-tests")

from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_PROTECTION"] = None

    with app.app_context():
        db.drop_all()
        db.create_all()

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()
