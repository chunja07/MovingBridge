#!/usr/bin/env python3
"""
Test script to verify admin login functionality
"""

import requests

def test_admin_login():
    base_url = "https://moving-bridge-nakknock.replit.app"
    
    # Create a session
    session = requests.Session()
    
    # Get login page first to get any cookies/csrf tokens
    login_page = session.get(f"{base_url}/admin/login")
    print(f"Login page status: {login_page.status_code}")
    
    # Attempt login
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }
    
    response = session.post(f"{base_url}/admin/login", data=login_data, allow_redirects=False)
    print(f"Login response status: {response.status_code}")
    print(f"Login response headers: {response.headers}")
    
    if response.status_code == 302:
        print(f"Redirect location: {response.headers.get('Location')}")
        
        # Follow redirect
        redirect_response = session.get(response.headers.get('Location', f"{base_url}/admin"))
        print(f"Final page status: {redirect_response.status_code}")
        print(f"Final page content length: {len(redirect_response.text)}")
        
        if "관리자 대시보드" in redirect_response.text or "Admin Dashboard" in redirect_response.text:
            print("SUCCESS: Admin login working!")
        else:
            print("FAILED: Admin login not working")
            print("Page content preview:", redirect_response.text[:500])
    else:
        print("FAILED: No redirect after login")
        print("Response content:", response.text[:500])

if __name__ == "__main__":
    test_admin_login()