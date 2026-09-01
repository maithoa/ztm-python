import smtplib
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
import os

from logger_config import get_logger

logger = get_logger(__name__)

def load_smtp_config():
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

    SMTP_SENDER = os.getenv('SMTP_SENDER')
    SMTP_SENDER_NAME = os.getenv('SMTP_SENDER_NAME')
    SMTP_APP_PASSWORD = os.getenv('SMTP_APP_PASSWORD')
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = os.getenv('SMTP_PORT')

    if not SMTP_SENDER or not SMTP_APP_PASSWORD or not SMTP_HOST or not SMTP_PORT:
        logger.error("SMTP configuration is incomplete.")
        raise ValueError("SMTP configuration is incomplete.")

    SMTP_PORT = int(SMTP_PORT)  # Ensure the port is an integer

    return SMTP_SENDER, SMTP_SENDER_NAME, SMTP_APP_PASSWORD, SMTP_HOST, SMTP_PORT


def send_an_email(recipient_email, subject, content, is_html=False):
    """
    Send an email using the SMTP server configured in the environment variables.

    Parameters:
    recipient_email (str): The recipient's email address.
    subject (str): The subject of the email.
    content (str): The content of the email.
    is_html (bool): Flag indicating if the content is HTML. Defaults to False.
    """

    if not recipient_email or not subject or not content:
        logger.error("Recipient email, subject, and content must all be provided.")
        raise ValueError("Recipient email, subject, and content must all be provided.")

    SMTP_SENDER, SMTP_SENDER_NAME, SMTP_APP_PASSWORD, SMTP_HOST, SMTP_PORT = load_smtp_config()

    email = EmailMessage()
    email['from'] = SMTP_SENDER_NAME + " <" + SMTP_SENDER+ ">"
    email['to'] = recipient_email
    email['subject'] = subject
    
    # Set content type based on is_html flag
    if is_html:
        email.set_content(content, subtype='html')
    else:
        email.set_content(content)

    try:
        with smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_SENDER, SMTP_APP_PASSWORD)
            smtp.send_message(email)
            logger.info("Email sent successfully to %s", recipient_email)
    except smtplib.SMTPException:
        logger.exception("SMTP error while sending email to %s", recipient_email)
        raise
    except Exception:
        logger.exception("Unexpected error while sending email to %s", recipient_email)
        raise


