import secrets
from datetime import datetime, timedelta, timezone

from models import db, OTPCode
from email_service import send_otp_email

OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
RESEND_WAIT_SECONDS = 60


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def create_and_send_otp(email, purpose):

    if purpose not in ("verification", "password_reset", "login"):
        raise ValueError("Invalid OTP purpose.")

    email = email.strip().lower()

    now = datetime.now(timezone.utc)

    existing = (
        OTPCode.query.filter_by(
            email=email,
            purpose=purpose,
            is_used=False,
        )
        .order_by(OTPCode.created_at.desc())
        .first()
    )

    if existing:
        created_at = existing.created_at

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        elapsed = (now - created_at).total_seconds()

        if elapsed < RESEND_WAIT_SECONDS:
            raise ValueError("Please wait before requesting another code.")

    otp = generate_otp()

    record = OTPCode(
        email=email,
        purpose=purpose,
        expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )

    record.set_code(otp)

    try:
        db.session.add(record)
        db.session.commit()

        send_otp_email(email, otp, purpose)

    except Exception:
        db.session.rollback()

        # Invalidate a code if email delivery fails.
        if "record" in locals() and record.id is not None:
            record = db.session.get(OTPCode, record.id)

            if record:
                record.is_used = True
                db.session.commit()

        raise RuntimeError("Could not send verification code.")

    return True


def verify_otp(email, otp, purpose):

    email = email.strip().lower()
    otp = otp.strip()

    record = (
        OTPCode.query.filter_by(
            email=email,
            purpose=purpose,
            is_used=False,
        )
        .order_by(OTPCode.created_at.desc())
        .first()
    )

    if record is None:
        return False

    if record.expires_at.tzinfo is None:
        expires_at = record.expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = record.expires_at

    if datetime.now(timezone.utc) >= expires_at:
        record.is_used = True
        db.session.commit()
        return False

    if record.attempts >= MAX_OTP_ATTEMPTS:
        record.is_used = True
        db.session.commit()
        return False

    record.attempts += 1

    if not record.check_code(otp):
        if record.attempts >= MAX_OTP_ATTEMPTS:
            record.is_used = True

        db.session.commit()
        return False

    record.is_used = True
    db.session.commit()

    return True
