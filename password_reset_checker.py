import requests
import imaplib
import email
import re
import random
import time

# -----------------------
# CONFIG
# -----------------------

USERNAME = "riddhimann_automation"

EMAIL_USER = "riddhimann@navyatech.in"
EMAIL_PASS = "mmmi bizm bmqh vlfe"
IMAP_SERVER = "imap.gmail.com"

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
    "origin": "https://experts.bestopinions.us"
}

# -----------------------
# STEP 1 - CALL FORGOT API
# -----------------------

print("Calling forgot password API...")

resp = requests.post(
    FORGOT_API,
    headers=HEADERS_FORGOT,
    json={"username": USERNAME}
)

print("Forgot API status:", resp.status_code)

if resp.status_code != 200:
    raise Exception("Forgot password API failed")


# -----------------------
# STEP 2 - READ EMAIL
# -----------------------

print("Waiting for email...")
time.sleep(15)

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)

mail.select("inbox")

status, messages = mail.search(None, '(SUBJECT "Forgot Password Notification")')

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


# -----------------------
# STEP 3 - EXTRACT URL
# -----------------------

url_match = re.search(r"https://experts\.bestopinions\.us/resetpassword\?[^ \n]+", body)

if not url_match:
    raise Exception("Reset URL not found")

reset_url = url_match.group()

print("Reset URL:", reset_url)


# -----------------------
# STEP 4 - EXTRACT TOKEN
# -----------------------

token_match = re.search(r"token=([^&]+)", reset_url)

if not token_match:
    raise Exception("Token not found")

alpha_token = token_match.group(1)

print("Extracted token:", alpha_token)


# -----------------------
# STEP 5 - GENERATE PASSWORD
# -----------------------

password = f"navya{random.randint(100,999)}"

print(f"calling passwordReset API with new password {password}")


# -----------------------
# STEP 6 - CALL RESET API
# -----------------------

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
else:
    print("Password reset FAILED")
    print(reset_resp.text)
