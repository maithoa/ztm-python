from pathlib import Path
from string import Template

from emailer_utils import send_an_email

recipient_email =  'nguyen.m.thoa@gmail.com'
subject = 'Test Email From Python Emailer 5'
content = 'This is a simple test email sent from Python.' 

# Send a simple email using the emailer util function
send_an_email(recipient_email, subject, content)

# Load content from html template and then send an email

html_content = ''

html_template = Template(Path('email_template.html').read_text())

html_content = html_template.substitute({ 'name': 'Mai' })

send_an_email(recipient_email, subject, html_content, is_html=True)
