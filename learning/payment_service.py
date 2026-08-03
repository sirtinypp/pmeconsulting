import base64
import hashlib
import hmac
import requests
from django.conf import settings


def get_paymongo_headers():
    """Returns headers required for PayMongo API authorization."""
    secret_key = getattr(settings, 'PAYMONGO_SECRET_KEY', '')
    encoded_key = base64.b64encode(f"{secret_key}:".encode('utf-8')).decode('utf-8')
    return {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_key}"
    }


def create_paymongo_checkout_session(user, course_title, tier_name, price_php, success_url, cancel_url):
    """
    Creates a PayMongo Checkout Session for a course enrollment fee.
    Enables QR Ph, GCash, Maya, Cards, and Direct Online Banking.
    """
    url = "https://api.paymongo.com/v1/checkout_sessions"
    
    # Amount in PayMongo is represented in cents (e.g. 12000 PHP = 1200000 cents)
    amount_in_cents = int(float(price_php) * 100)

    payload = {
        "data": {
            "attributes": {
                "billing": {
                    "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                    "email": user.email,
                },
                "line_items": [
                    {
                        "amount": amount_in_cents,
                        "currency": "PHP",
                        "name": f"German Course Enrollment: {course_title}",
                        "quantity": 1,
                        "description": f"{tier_name} Tier Enrollment Fee"
                    }
                ],
                "payment_method_types": [
                    "qrph",
                    "gcash",
                    "paymaya",
                    "card",
                    "dob"
                ],
                "success_url": success_url,
                "cancel_url": cancel_url,
                "description": f"Enrollment for {course_title} ({tier_name})"
            }
        }
    }

    try:
        response = requests.post(url, json=payload, headers=get_paymongo_headers(), timeout=15)
        response.raise_for_status()
        data = response.json().get('data', {})
        attributes = data.get('attributes', {})
        
        return {
            "success": True,
            "checkout_session_id": data.get('id'),
            "checkout_url": attributes.get('checkout_url')
        }
    except requests.RequestException as e:
        error_msg = f"PayMongo API error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_json = e.response.json()
                errors = error_json.get('errors', [])
                if errors:
                    error_msg = errors[0].get('detail', error_msg)
            except Exception:
                pass
        return {
            "success": False,
            "error": error_msg
        }


def verify_paymongo_webhook(raw_payload, signature_header):
    """
    Verifies PayMongo webhook signature header.
    Signature header format: t=timestamp,te=test_signature,li=live_signature
    """
    webhook_secret = getattr(settings, 'PAYMONGO_WEBHOOK_SECRET', '')
    if not webhook_secret or not signature_header:
        return False

    try:
        signature_parts = {}
        for item in signature_header.split(','):
            key_val = item.split('=', 1)
            if len(key_val) == 2:
                signature_parts[key_val[0].strip()] = key_val[1].strip()

        timestamp = signature_parts.get('t')
        test_signature = signature_parts.get('te')
        live_signature = signature_parts.get('li')
        
        target_signature = live_signature or test_signature
        if not timestamp or not target_signature:
            return False

        to_sign = f"{timestamp}.{raw_payload.decode('utf-8')}".encode('utf-8')
        computed_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            to_sign,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_signature, target_signature)
    except Exception:
        return False
