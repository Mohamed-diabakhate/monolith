#!/usr/bin/env python3
"""
Check Helius API status and provide recommendations.
"""
import requests
import time

def check_helius_status():
    """Check Helius API status and provide recommendations."""
    
    print("🔍 Checking Helius API Status...")
    print("=" * 50)
    
    # Test basic connectivity
    try:
        response = requests.get("https://api.helius.xyz/v0/addresses/test/nfts", timeout=10)
        print(f"✅ Basic connectivity: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic connectivity failed: {e}")
        return False
    
    # Test with a simple wallet
    try:
        response = requests.get("https://api.helius.xyz/v0/addresses/11111111111111111111111111111112/nfts", timeout=10)
        print(f"📊 API Response: {response.status_code}")
        if response.status_code == 500:
            print("⚠️  Helius API is experiencing internal errors")
            print("   This is likely a temporary service issue")
        elif response.status_code == 200:
            print("✅ Helius API is working normally")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    print("\n📋 Recommendations:")
    print("1. Check Helius status: https://status.helius.dev/")
    print("2. Join Helius Discord: https://discord.gg/helius")
    print("3. Verify your API key has DAS API permissions")
    print("4. Try again in a few minutes")
    print("5. Consider using a different API key")
    
    return True

if __name__ == "__main__":
    check_helius_status() 