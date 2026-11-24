import os
import smtplib
import ssl
import logging

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_otp_email(recipient_email, otp, purpose="verification"):

    mail_server = os.getenv("MAIL_SERVER")
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    use_tls = os.getenv("MAIL_USE_TLS", "True").lower() == "true"

    if not all([mail_server, mail_username, mail_password]):
        raise RuntimeError("Email configuration is incomplete.")

    if purpose == "password_reset":
        subject = "Password Reset - Forex Trading Journal"
        message = (
            "You requested to reset your password.\n\n"
            f"Your password reset OTP is: {otp}\n\n"
        )

    elif purpose == "login":
        subject = "Login Verification - Forex Trading Journal"
        message = (
            "A login attempt was made on your Forex Trading Journal account.\n\n"
            f"Your login verification OTP is: {otp}\n\n"
        )

    else:
        subject = "Email Verification - Forex Trading Journal"
        message = (
            "Welcome to Forex Trading Journal!\n\n"
            f"Your email verification OTP is: {otp}\n\n"
        )

    message += (
        "This code is valid for 10 minutes.\n"
        "Do not share this code with anyone.\n\n"
        "If you did not request this code, please ignore this email."
    )

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = f"Forex Trading Journal <{mail_username}>"
    email["To"] = recipient_email
    email.set_content(message)

    server = None

    try:
        server = smtplib.SMTP(
            mail_server,
            mail_port,
            timeout=20,
        )

        server.ehlo()

        if use_tls:
            server.starttls(context=ssl.create_default_context())
            server.ehlo()

        server.login(mail_username, mail_password)

        server.send_message(email)

        logger.info(
            "OTP email successfully sent to %s for purpose %s",
            recipient_email,
            purpose,
        )

        return True

    except Exception as error:

        logger.exception("OTP email delivery failed.")

        raise RuntimeError("Unable to send the OTP email.") from error

    finally:

        if server is not None:

            try:
                server.close()

            except Exception:
                logger.warning(
                    "Could not cleanly close the SMTP connection.",
                    exc_info=True,
                )
