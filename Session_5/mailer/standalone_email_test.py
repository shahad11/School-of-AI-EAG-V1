import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")

to_email = "shahadmohammed111111@gmail.com"
subject = "SMTP Standalone Test"
body = "This is a test email sent directly from a Python script using your .env SMTP settings."

print(f"SMTP_SERVER: {smtp_server}")
print(f"SMTP_PORT: {smtp_port}")
print(f"SMTP_USER: {smtp_user}")
print(f"SMTP_PASSWORD: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")

if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
    print("❌ One or more SMTP settings are missing. Please check your .env file.")
    exit(1)

msg = MIMEMultipart()
msg['From'] = smtp_user
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Failed to send email: {e}") 