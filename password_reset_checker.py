import requests
import imaplib
import email
import re
import random
import time
import smtplib
import os
import io
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from contextlib import redirect_stdout

receiver_list = [
    "kirana@navyatech.in",
    "armugam@navyatech.in",
    "pushpa@navyatech.in"
]

# -----------------------
# EMAIL SENDER FUNCTION
# -----------------------

def send_email(email, subject, body):
    sender_email = "riddhimann@navyatech.in"
    password = os.getenv('APP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Bcc'] = ", ".join(receiver_list)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")


# -----------------------
# CAPTURE CONSOLE LOGS
# -----------------------

log_buffer = io.StringIO()

success = False

with redirect_stdout(log_buffer):

    try:

        USERNAME = "riddhimann_automation"
        EMAIL_USER = "riddhimann@navyatech.in"
        EMAIL_PASS = os.getenv('APP_PASSWORD')

        FORGOT_API = "https://alpha.bestopinions.us/alphaBackend/accounts/password/forgot/"
        RESET_API = "https://experts.bestopinions.us/napi4/webapi/passwordReset"

        HEADERS_FORGOT = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://alpha.bestopinions.us",
            "referer": "https://alpha.bestopinions.us/forgotPassword",
        }

        HEADERS_RESET = {
            "accept": "*/*",
            "origin": "https://experts.bestopinions.us",
        }

        print("Calling forgot password API...")

        resp = requests.post(
            FORGOT_API,
            headers=HEADERS_FORGOT,
            json={"username": USERNAME}
        )

        print("Forgot API status:", resp.status_code)

        if resp.status_code != 200:
            raise Exception("Forgot password API failed")

        print("Waiting for email...")

        time.sleep(10)

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)

        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN SUBJECT "Forgot Password Notification")')
        mail_ids = messages[0].split()

        if not mail_ids:
            raise Exception("Reset email not found")

        latest_email_id = mail_ids[-1]

        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)

        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()

        print("Email body received")

        url_match = re.search(r"https://experts\.bestopinions\.us/resetpassword\?[^ \n]+", body)

        if not url_match:
            raise Exception("Reset URL not found")

        reset_url = url_match.group()

        print("Reset URL:", reset_url)

        token_match = re.search(r"token=([^&]+)", reset_url)

        if not token_match:
            raise Exception("Token not found")

        alpha_token = token_match.group(1)

        # print("Extracted token:", alpha_token)

        password = f"navya{random.randint(100,999)}"

        print(f"calling passwordReset API with new password {password}")

        files = {
            "newpass": (None, password),
            "alpha_token": (None, alpha_token)
        }

        reset_resp = requests.post(
            RESET_API,
            headers=HEADERS_RESET,
            files=files
        )

        print("Reset API status:", reset_resp.status_code)

        if reset_resp.status_code == 200:
            print("Password reset SUCCESS")
            success = True
        else:
            print("Password reset FAILED")
            print(reset_resp.text)

    except Exception as e:
        print("Script failed with error:", e)


# -----------------------
# SEND RESULT EMAIL
# -----------------------

logs = log_buffer.getvalue()

local_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST")

if success:

    subject = "Password reset on Vyas dev tested succesfully"

    body = f"""password reset script ran on {local_time} and passed for user riddhimann_automation.

{logs}
"""

else:

    subject = "FAILURE! Password reset on vyas dev"

    body = f"""password reset script ran on {local_time} and failed for user riddhimann_automation.

{logs}
"""

send_email("riddhimann@navyatech.in", subject, body)
