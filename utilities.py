import qrcode
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')

def create_signed_token(roll_number):
    signature = hmac.new(
        SECRET_KEY.encode(),
        roll_number.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    return f"TICKET:{roll_number}.{signature}"

def verify_signed_token(token):
    if not token.startswith('TICKET:'):
        return None
    token = token.replace('TICKET:', '')
    parts = token.split('.')
    if len(parts) != 2:
        return None
    roll_number, received_signature = parts
    expected_signature = hmac.new(
        SECRET_KEY.encode(),
        roll_number.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    if hmac.compare_digest(received_signature, expected_signature):
        return roll_number
    return None

def generate_qr(roll_number):
    token = create_signed_token(roll_number)
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    os.makedirs('qrcodes', exist_ok=True)
    img.save(f'qrcodes/{roll_number}.png')
    return token