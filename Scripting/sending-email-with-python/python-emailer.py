from string import Template

from emailer_utils import send_an_email

recipient_email =  'nguyen.m.thoa@gmail.com'
subject = 'Test Email From Python Emailer 4'
content = 'This is a simple test email sent from Python.' 

# Send a simple email using the emailer util function
send_an_email(recipient_email, subject, content)

# Load content from html template and then send an email

html_content = ''
with open('email_template.html', 'r') as file:
    html_template_file = file.read()
    html_template = Template(html_template_file)

    html_content = html_template.substitute({ 'name': 'Mai' })

send_an_email(recipient_email, subject, html_content, is_html=True)
