import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME")

def send_otp_email(to_email, otp):
    subject = f"Your OTP Verification Code: {otp}"
    body = f"Hello,\n\nYour OTP for verification is: {otp}\n\nThis code will expire in 10 minutes.\n\nRegards,\n{EMAIL_FROM_NAME}"

    msg = MIMEMultipart()
    msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_ADDRESS}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        print(f"OTP sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        print(f"CONSOLE FALLBACK: OTP for {to_email} is {otp}")
        return False
