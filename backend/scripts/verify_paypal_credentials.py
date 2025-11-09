#!/usr/bin/env python
"""
Verify and troubleshoot PayPal credentials.
This script helps diagnose PayPal API authentication issues.
"""

import os
import sys
import json
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env_path = os.path.join(base_dir, "infra", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Get credentials
mode = os.getenv("PAYPAL_MODE", "sandbox")
client_id = os.getenv("PAYPAL_CLIENT_ID")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

print("🔍 PayPal Credential Verification Tool")
print("="*50)

# Check environment variables
print("\n📋 Environment Check:")
print(f"   Mode: {mode}")
print(f"   Client ID: {client_id[:20]}..." if client_id else "   ❌ Client ID: NOT SET")
print(f"   Secret: {'*' * 10}" if client_secret else "   ❌ Secret: NOT SET")

if not client_id or not client_secret:
    print("\n❌ Missing credentials!")
    print("\n📝 Next Steps:")
    print("1. Go to https://developer.paypal.com/")
    print("2. Log in with your PayPal business account")
    print("3. Go to 'My Apps & Credentials'")
    print("4. Select 'Sandbox' tab")
    print("5. Create a new app or use existing one")
    print("6. Copy the Client ID and Secret")
    print("7. Update your infra/.env file")
    sys.exit(1)

# Set API endpoint based on mode
if mode == "sandbox":
    base_url = "https://api-m.sandbox.paypal.com"
else:
    base_url = "https://api-m.paypal.com"

print(f"\n🌐 API Endpoint: {base_url}")

# Test authentication
print("\n🔐 Testing Authentication...")

# Create Basic Auth header
auth_string = f"{client_id}:{client_secret}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "client_credentials"
}

try:
    # Request access token
    response = requests.post(
        f"{base_url}/v1/oauth2/token",
        headers=headers,
        data=data
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        print("✅ Authentication successful!")
        print(f"   Access token: {access_token[:20]}...")
        print(f"   Token type: {token_data.get('token_type')}")
        print(f"   Expires in: {token_data.get('expires_in')} seconds")

        # Test API access
        print("\n🔍 Testing API Access...")
        api_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Try to list billing plans
        plans_response = requests.get(
            f"{base_url}/v1/billing/plans",
            headers=api_headers
        )

        if plans_response.status_code == 200:
            plans_data = plans_response.json()
            print("✅ API access working!")

            if plans_data.get('plans'):
                print(f"\n📋 Found {len(plans_data['plans'])} existing plans:")
                for plan in plans_data['plans']:
                    print(f"   - {plan.get('name', 'Unnamed')}: {plan.get('id')}")
            else:
                print("\n📝 No billing plans found (this is normal for new accounts)")
                print("   Run setup_paypal_plans.py to create plans")
        else:
            print(f"⚠️ API access issue: {plans_response.status_code}")
            print(f"   Response: {plans_response.text}")

        print("\n✅ PayPal integration is properly configured!")

    else:
        print(f"❌ Authentication failed! Status: {response.status_code}")
        error_data = response.json() if response.text else {}
        print(f"   Error: {error_data.get('error', 'Unknown')}")
        print(f"   Description: {error_data.get('error_description', 'No description')}")

        print("\n🔧 Troubleshooting:")
        print("1. Verify credentials are from the correct mode (Sandbox vs Live)")
        print("2. Check if the app is approved in PayPal Developer Dashboard")
        print("3. Ensure credentials are not expired or revoked")
        print("4. Try regenerating the secret in PayPal Developer Dashboard")

except Exception as e:
    print(f"❌ Connection error: {str(e)}")
    print("\n🔧 Troubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify firewall/proxy settings")
    print("3. Try using a VPN if PayPal is restricted in your region")

print("\n" + "="*50)
print("📚 PayPal Developer Resources:")
print("   Dashboard: https://developer.paypal.com/")
print("   API Docs: https://developer.paypal.com/docs/api/")
print("   Sandbox Testing: https://developer.paypal.com/developer/accounts/")
print("="*50)