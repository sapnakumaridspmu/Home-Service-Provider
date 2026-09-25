import smtplib
from email.message import EmailMessage
from flask import current_app


def send_mail(to, subject, body):
    """Send via SMTP if configured; otherwise print to the server console (development)."""
    c = current_app.config
    if not c["SMTP_HOST"]:
        current_app.logger.warning("[mail not configured] To: %s | %s\n%s", to, subject, body)
        return False
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = c["MAIL_FROM"], to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(c["SMTP_HOST"], c["SMTP_PORT"], timeout=15) as s:
            s.starttls()
            if c["SMTP_USER"]:
                s.login(c["SMTP_USER"], c["SMTP_PASSWORD"])
            s.send_message(msg)
        return True
    except Exception as e:  # never break the request because email failed
        current_app.logger.error("Mail send failed: %s", e)
        return False
