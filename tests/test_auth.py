import pytest

from models import User, db


@pytest.fixture
def verified_user(client):
    with client.application.app_context():
        user = User(
            name="Samuel Mutisya",
            email="samuel@example.com",
            is_verified=True,
        )
        user.set_password("StrongPass123")
        db.session.add(user)
        db.session.commit()

        return user.id


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/login" in response.location


def test_login_rejects_wrong_password(client, verified_user):
    response = client.post(
        "/login",
        data={
            "email": "samuel@example.com",
            "password": "WrongPassword123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/login",
        data={
            "email": "unknown@example.com",
            "password": "StrongPass123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_registration_success(client, monkeypatch):
    import app as app_module

    otp_calls = []

    def fake_send_otp(email, purpose):
        otp_calls.append((email, purpose))

    monkeypatch.setattr(
        app_module,
        "create_and_send_otp",
        fake_send_otp,
    )

    response = client.post(
        "/register",
        data={
            "name": "Samuel Mutisya",
            "email": "SAMUEL@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )

    assert response.status_code == 302
    assert response.location.endswith("/verify-email")
    assert otp_calls == [("samuel@example.com", "verification")]

    with app_module.app.app_context():
        user = db.session.execute(
            db.select(User).filter_by(email="samuel@example.com")
        ).scalar_one()

        assert user.name == "Samuel Mutisya"
        assert user.is_verified is False
        assert user.check_password("StrongPass123")


def test_registration_rejects_short_password(client):
    response = client.post(
        "/register",
        data={
            "name": "Samuel Mutisya",
            "email": "samuel@example.com",
            "password": "short",
            "confirm_password": "short",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Password must contain at least 8 characters." in response.data


def test_registration_rejects_password_mismatch(client):
    response = client.post(
        "/register",
        data={
            "name": "Samuel Mutisya",
            "email": "samuel@example.com",
            "password": "StrongPass123",
            "confirm_password": "DifferentPass123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Passwords do not match." in response.data


def test_email_verification_success(client, monkeypatch):
    import app as app_module

    with app_module.app.app_context():
        user = User(
            name="Samuel Mutisya",
            email="samuel@example.com",
            is_verified=False,
        )
        user.set_password("StrongPass123")
        db.session.add(user)
        db.session.commit()

    monkeypatch.setattr(
        app_module,
        "verify_otp",
        lambda email, otp, purpose: (
            email == "samuel@example.com"
            and otp == "123456"
            and purpose == "verification"
        ),
    )

    with client.session_transaction() as session:
        session["pending_verification_email"] = "samuel@example.com"

    response = client.post(
        "/verify-email",
        data={"otp": "123456"},
    )

    assert response.status_code == 302
    assert response.location.endswith("/login")

    with app_module.app.app_context():
        user = db.session.execute(
            db.select(User).filter_by(email="samuel@example.com")
        ).scalar_one()

        assert user.is_verified is True

    with client.session_transaction() as session:
        assert "pending_verification_email" not in session


def test_unverified_user_cannot_login(client):
    import app as app_module

    with app_module.app.app_context():
        user = User(
            name="Samuel Mutisya",
            email="unverified@example.com",
            is_verified=False,
        )
        user.set_password("StrongPass123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={
            "email": "unverified@example.com",
            "password": "StrongPass123",
        },
    )

    assert response.status_code == 302
    assert response.location.endswith("/verify-email")

    with client.session_transaction() as session:
        assert session["pending_verification_email"] == "unverified@example.com"


def test_successful_login_with_otp(client, verified_user, monkeypatch):
    import app as app_module

    otp_calls = []

    monkeypatch.setattr(
        app_module,
        "create_and_send_otp",
        lambda email, purpose: otp_calls.append((email, purpose)),
    )

    response = client.post(
        "/login",
        data={
            "email": "samuel@example.com",
            "password": "StrongPass123",
        },
    )

    assert response.status_code == 302
    assert response.location.endswith("/verify-login")
    assert otp_calls == [("samuel@example.com", "login")]

    monkeypatch.setattr(
        app_module,
        "verify_otp",
        lambda email, otp, purpose: (
            email == "samuel@example.com" and otp == "123456" and purpose == "login"
        ),
    )

    response = client.post(
        "/verify-login",
        data={"otp": "123456"},
    )

    assert response.status_code == 302
    assert response.location.endswith("/")

    # Confirm the user can now access the protected dashboard.
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_logout_ends_user_session(client, verified_user, monkeypatch):
    import app as app_module

    monkeypatch.setattr(
        app_module,
        "create_and_send_otp",
        lambda email, purpose: None,
    )

    monkeypatch.setattr(
        app_module,
        "verify_otp",
        lambda email, otp, purpose: True,
    )

    client.post(
        "/login",
        data={
            "email": "samuel@example.com",
            "password": "StrongPass123",
        },
    )

    client.post(
        "/verify-login",
        data={"otp": "123456"},
    )

    # Confirm the user is logged in.
    response = client.get("/dashboard")
    assert response.status_code == 200

    # Logout requires POST.
    response = client.post("/logout")

    assert response.status_code == 302

    # Confirm the session has ended.
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_verify_login_rejects_invalid_otp(client, verified_user, monkeypatch):
    import app as app_module

    monkeypatch.setattr(
        app_module,
        "verify_otp",
        lambda email, otp, purpose: False,
    )

    with client.session_transaction() as session:
        session["pending_login_email"] = "samuel@example.com"

    response = client.post(
        "/verify-login",
        data={"otp": "999999"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid or expired login verification code." in response.data


def test_google_creates_new_verified_user(client, monkeypatch):
    import app as app_module

    monkeypatch.setattr(
        app_module.google,
        "authorize_access_token",
        lambda: {
            "userinfo": {
                "sub": "google-user-123",
                "email": "google@example.com",
                "email_verified": True,
                "name": "Google User",
            }
        },
    )

    response = client.get("/google/callback")

    assert response.status_code == 302

    with app_module.app.app_context():
        user = User.query.filter_by(email="google@example.com").first()

        assert user is not None
        assert user.name == "Google User"
        assert user.google_id == "google-user-123"
        assert user.is_verified is True

    assert client.get("/dashboard").status_code == 200


def test_google_links_existing_verified_user(client, verified_user, monkeypatch):
    import app as app_module

    monkeypatch.setattr(
        app_module.google,
        "authorize_access_token",
        lambda: {
            "userinfo": {
                "sub": "google-link-123",
                "email": "samuel@example.com",
                "email_verified": True,
                "name": "Samuel Mutisya",
            }
        },
    )

    response = client.get("/google/callback")

    assert response.status_code == 302

    with app_module.app.app_context():
        user = db.session.get(User, verified_user)

        assert user.google_id == "google-link-123"
        assert user.is_verified is True

    assert client.get("/dashboard").status_code == 200


def test_google_rejects_unverified_existing_user(client, monkeypatch):
    import app as app_module

    with app_module.app.app_context():
        user = User(
            name="Samuel Mutisya",
            email="samuel@example.com",
            is_verified=False,
        )
        user.set_password("StrongPass123")
        db.session.add(user)
        db.session.commit()

    monkeypatch.setattr(
        app_module.google,
        "authorize_access_token",
        lambda: {
            "userinfo": {
                "sub": "google-user-456",
                "email": "samuel@example.com",
                "email_verified": True,
                "name": "Samuel Mutisya",
            }
        },
    )

    response = client.get("/google/callback")

    assert response.status_code == 302
    assert response.location.endswith("/login")

    with app_module.app.app_context():
        user = User.query.filter_by(email="samuel@example.com").first()

        assert user.google_id is None
        assert user.is_verified is False


def test_google_rejects_unverified_google_email(client, monkeypatch):
    import app as app_module

    monkeypatch.setattr(
        app_module.google,
        "authorize_access_token",
        lambda: {
            "userinfo": {
                "sub": "google-user-789",
                "email": "google@example.com",
                "email_verified": False,
                "name": "Google User",
            }
        },
    )

    response = client.get(
        "/google/callback",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Your Google account could not be verified." in response.data

    with app_module.app.app_context():
        user = User.query.filter_by(email="google@example.com").first()

        assert user is None
