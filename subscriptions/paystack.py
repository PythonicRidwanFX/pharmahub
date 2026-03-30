import requests
from django.conf import settings


class PaystackError(Exception):
    pass


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(email, amount_kobo, reference, callback_url, metadata=None):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
    payload = {
        "email": email,
        "amount": int(amount_kobo),
        "reference": reference,
        "callback_url": callback_url,
        "currency": "NGN",
    }

    if metadata:
        payload["metadata"] = metadata

    response = requests.post(url, json=payload, headers=_headers(), timeout=30)
    data = response.json()

    if response.status_code != 200 or not data.get("status"):
        raise PaystackError(data.get("message", "Failed to initialize transaction"))

    return data["data"]


def verify_transaction(reference):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    response = requests.get(url, headers=_headers(), timeout=30)
    data = response.json()

    if response.status_code != 200 or not data.get("status"):
        raise PaystackError(data.get("message", "Failed to verify transaction"))

    return data["data"]