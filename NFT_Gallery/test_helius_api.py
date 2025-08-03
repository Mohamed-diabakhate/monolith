#!/usr/bin/env python3
"""
Simple test script to verify Helius API connectivity and permissions.
"""
import os
import requests
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def test_helius_api():
    """Test Helius API connectivity and permissions."""
    
    # Load environment variables
    load_env_file()
    
    api_key = os.getenv("HELIUS_API_KEY")
    if not api_key:
        print("❌ HELIUS_API_KEY not found in environment variables")
        return False
    
    print(f"🔑 Using API key: {api_key[:8]}...{api_key[-4:]}")
    
    base_url = "https://api.helius.xyz/v0"
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/addresses/test/nfts?api-key={api_key}", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Try with a known wallet
    print("\n2️⃣ Testing with known wallet...")
    test_wallet = "11111111111111111111111111111112"  # System Program
    try:
        response = requests.get(f"{base_url}/addresses/{test_wallet}/nfts?api-key={api_key}", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Try RPC endpoint
    print("\n3️⃣ Testing RPC endpoint...")
    try:
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSlot"
        }
        response = requests.post(f"{base_url}/rpc?api-key={api_key}", json=data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check API key info
    print("\n4️⃣ Checking API key information...")
    try:
        # Try to get some basic info about the API key
        response = requests.get(f"{base_url}/addresses/test/nfts?api-key={api_key}", timeout=10)
        headers = response.headers
        print(f"   Rate limit headers: {dict(headers)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📋 Summary:")
    print("   - If you see 401 errors: API key is invalid or expired")
    print("   - If you see 403 errors: API key lacks permissions")
    print("   - If you see 500 errors: Helius API service issues")
    print("   - If you see 200 responses: API key is working")
    
    return True

if __name__ == "__main__":
    print("🧪 Helius API Test Script")
    print("=" * 50)
    test_helius_api() 