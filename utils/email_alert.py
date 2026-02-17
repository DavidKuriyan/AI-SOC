import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_alert_email(to_email, subject, body, config):
    """
    Send an email alert using SMTP.
    Requires Gmail App Password in config.
    """
    smtp_server = config.get('MAIL_SERVER')
    smtp_port = config.get('MAIL_PORT')
    smtp_user = config.get('MAIL_USERNAME')
    smtp_password = config.get('MAIL_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("⚠️ Email credentials not set. Skipping email alert.")
        return

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
        print(f"📧 Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
