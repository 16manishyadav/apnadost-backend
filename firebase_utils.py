import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Request
import os
import json

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
        service_account_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        cred = credentials.Certificate(service_account_info)
    else:
        cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)

def verify_firebase_token(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    id_token = auth_header.split("Bearer ")[1]
    print(f"Received Firebase ID token: {id_token}")  # Debug print
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token") 