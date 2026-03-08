import os
from pathlib import Path

import pyotp
from SmartApi import SmartConnect
from dotenv import load_dotenv

# load_dotenv(dotenv_path="config/.env")
load_dotenv(Path(__file__).resolve().parent.parent / "config" / ".env")

api_key = os.getenv("ANGELONE_API_KEY")
client_id = os.getenv("ANGELONE_CLIENT_ID")
password = os.getenv("ANGELONE_PASSWORD")
totp_secret = os.getenv("ANGELONE_TOTP_SECRET")

# Generate TOTP
totp = pyotp.TOTP(totp_secret).now()

# Connect
api = SmartConnect(api_key=api_key)
session = api.generateSession(client_id, password, totp)

if session["status"]:
    print("✅ Login successful!")
    profile = api.getProfile(session["data"]["refreshToken"])
    print(f"   Name     : {profile['data']['name']}")
    print(f"   Email    : {profile['data']['email']}")
    print(f"   Broker   : {profile['data']['exchanges']}")

    funds = api.rmsLimit()
    print(f"   Available: ₹{funds['data']['availablecash']}")
else:
    print("❌ Login failed:", session["message"])
