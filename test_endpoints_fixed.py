#!/usr/bin/env python3
"""
Test script to verify calendar and statistics endpoints work after database fix
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoints():
    print("=== Testing Calendar and Statistics Endpoints ===")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        print("1. Testing login...")
        # Get login page to get CSRF token
        login_page = session.get(f"{BASE_URL}/login")
        if login_page.status_code != 200:
            print(f"   ✗ Failed to get login page: {login_page.status_code}")
            return
        
        # Extract CSRF token (simple approach)
        csrf_token = None
        if 'csrf_token' in login_page.text:
            # Find the CSRF token in the HTML
            import re
            match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
            if match:
                csrf_token = match.group(1)
        
        if not csrf_token:
            print("   ✗ Could not extract CSRF token")
            return
        
        # Login with admin credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        if login_response.status_code == 200 and 'login' not in login_response.url:
            print("   ✓ Login successful")
        else:
            print(f"   ✗ Login failed: {login_response.status_code}")
            return
        
        print("2. Testing calendar API endpoint...")
        calendar_response = session.get(f"{BASE_URL}/calendario/api/ordenes?year=2025&month=10")
        print(f"   Status: {calendar_response.status_code}")
        
        if calendar_response.status_code == 200:
            try:
                calendar_data = calendar_response.json()
                print(f"   ✓ Calendar endpoint working - returned {len(calendar_data)} items")
            except json.JSONDecodeError:
                print("   ✗ Calendar endpoint returned non-JSON response")
        else:
            print(f"   ✗ Calendar endpoint failed: {calendar_response.status_code}")
        
        print("3. Testing statistics API endpoint...")
        stats_response = session.get(f"{BASE_URL}/calendario/api/estadisticas-mes?year=2025&month=10")
        print(f"   Status: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            try:
                stats_data = stats_response.json()
                print(f"   ✓ Statistics endpoint working - returned data: {stats_data}")
            except json.JSONDecodeError:
                print("   ✗ Statistics endpoint returned non-JSON response")
        else:
            print(f"   ✗ Statistics endpoint failed: {stats_response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_endpoints()