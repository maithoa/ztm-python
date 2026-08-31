import smtplib
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

SMTP_SENDER = os.getenv('SMTP_SENDER')
SMTP_SENDER_NAME = os.getenv('SMTP_SENDER_NAME')
SMTP_APP_PASSWORD = os.getenv('SMTP_APP_PASSWORD')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT')

def send_an_email(recipient_email, subject, content, is_html=False):
    email = EmailMessage()
    email['from'] = SMTP_SENDER_NAME + " <" + SMTP_SENDER+ ">"
    email['to'] = recipient_email
    email['subject'] = subject
    
    # Set content type based on is_html flag
    if is_html:
        email.set_content(content, subtype='html')
    else:
        email.set_content(content)

    with smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SMTP_SENDER, SMTP_APP_PASSWORD)
        smtp.send_message(email)
        print("Email sent successfully.")


