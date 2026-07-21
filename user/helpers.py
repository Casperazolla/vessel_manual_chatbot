import hashlib
import os
import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER  = "smtp.office365.com"
SMTP_PORT    = 587
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
DISPLAY_NAME = "Azolla Support"

def hash_password(password):
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password, stored):
    salt, hashed = stored.split(':')
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed


def send_otp_email(email, otp_code, purpose):
    subject = 'OTP for Signup' if purpose == 'signup' else 'OTP for Password Reset'
    plain   = f'Your OTP is {otp_code}. It expires in 5 minutes. Do not share it.'
    html    = f'''
        <p style="font-family:Arial,sans-serif;font-size:14px;color:#374151;">
            Your OTP is <strong>{otp_code}</strong>.<br>
            It expires in <strong>5 minutes</strong>. Do not share it with anyone.
        </p>
    '''
    _send_email(subject, html, plain, [email])


def _send_email(subject, html_body, plain_body, recipients):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        raise EnvironmentError("EMAIL_SENDER or EMAIL_PASSWORD not configured")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        for recipient in recipients:
            try:
                msg            = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"]    = f"{DISPLAY_NAME} <{EMAIL_SENDER}>"
                msg["To"]      = recipient
                msg.attach(MIMEText(plain_body, "plain"))
                msg.attach(MIMEText(html_body,  "html"))
                server.sendmail(EMAIL_SENDER, recipient, msg.as_string())
            except Exception as e:
                print(f"Failed to send to {recipient}: {e}")


def generate_otp():
    return str(random.randint(100000, 999999))


def store_otp_in_session(request, purpose, otp, extra_data={}):
    expires_at = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    request.session[purpose] = {
        'otp':        otp,
        'expires_at': expires_at,
        'is_used':    False,
        **extra_data
    }


def verify_otp_from_session(request, purpose, otp_input):
    session_data = request.session.get(purpose)

    if not session_data:
        return 'OTP not found. Please try again'

    if session_data['is_used']:
        return 'OTP already used'

    if datetime.utcnow() > datetime.fromisoformat(session_data['expires_at']):
        del request.session[purpose]
        return 'OTP expired'

    if session_data['otp'] != otp_input:
        # invalidate after 1 wrong attempt
        session_data['is_used'] = True
        request.session[purpose] = session_data
        return 'Invalid OTP'

    # mark used
    session_data['is_used'] = True
    request.session[purpose] = session_data
    return None  # None means success


def get_tokens(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    class TokenUser:
        def __init__(self, id):
            self.id        = id
            self.pk        = id
            self.is_active = True

    token          = RefreshToken.for_user(TokenUser(user.id))
    token['email'] = user.email
    token['role']  = user.role
    return {
        'access':  str(token.access_token),
        'refresh': str(token),
    }


def get_user_from_token(request):
    from rest_framework_simplejwt.tokens import AccessToken
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    raw_token = auth_header.replace('Bearer ', '')
    try:
        decoded = AccessToken(raw_token)
        user_id = decoded['user_id']
        return User.objects.get(id=user_id)
    except Exception:
        return None


def validate_required_fields(data, fields):
    missing = [f for f in fields if not str(data.get(f, '')).strip()]
    if missing:
        return f"Missing fields: {', '.join(missing)}"
    return None