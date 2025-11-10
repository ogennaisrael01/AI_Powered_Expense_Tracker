import httpx
from expence_tracker import settings
from .retry_on_failures import retry_on_failures

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_URI = settings.PAYSTACK_URI

def initialize_payment(payload: dict):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{PAYSTACK_URI}initialize"
    response = retry_on_failures(httpx.post(url=url, json=payload, headers=headers))
    if not response.get("success"):
        return response.get("message")
    response_data = response.get("request").json()
    if response_data.get("status"):
        return {"success": True, "data": response_data.get("data").get("authorization_url")}

    else:
        return {"success": False, "message": "unable to reach the paystack sservice"}

    
def verify_payments(refrence: str):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{PAYSTACK_URI}verify/{refrence}"
    response = retry_on_failures(httpx.get(url, headers=headers))
    return response.get("request").json()