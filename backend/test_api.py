import requests
import json

# Test script for HydroFlow Tracker Backend API
BASE_URL = "http://localhost:5000"

def test_api():
    """Test basic API functionality"""
    
    print("Testing HydroFlow Tracker Backend API...")
    
    # Test 1: Health check (if we add one)
    print("\n1. Testing API availability...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports")
        if response.status_code == 401:  # Expected without auth
            print("✓ API is running (401 Unauthorized is expected)")
        else:
            print(f"✓ API is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("✗ API is not running. Please start the Flask application.")
        return False
    
    # Test 2: User Registration
    print("\n2. Testing user registration...")
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 201:
            print("✓ User registration successful")
            user_data = response.json()
            access_token = user_data.get('access_token')
        else:
            print(f"✗ User registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ User registration error: {e}")
        return False
    
    # Test 3: Create Report
    print("\n3. Testing report creation...")
    test_report = {
        "title": "Test Report",
        "description": "This is a test report for API testing",
        "priority": "medium",
        "category": "testing"
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/reports", json=test_report, headers=headers)
        if response.status_code == 201:
            print("✓ Report creation successful")
            report_data = response.json()
            report_id = report_data['report']['id']
        else:
            print(f"✗ Report creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Report creation error: {e}")
        return False
    
    # Test 4: Get Reports
    print("\n4. Testing get reports...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports", headers=headers)
        if response.status_code == 200:
            print("✓ Get reports successful")
            reports_data = response.json()
            print(f"  Found {len(reports_data['reports'])} report(s)")
        else:
            print(f"✗ Get reports failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Get reports error: {e}")
        return False
    
    # Test 5: Add Comment
    print("\n5. Testing comment creation...")
    test_comment = {
        "content": "This is a test comment"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/reports/{report_id}/comments", 
                               json=test_comment, headers=headers)
        if response.status_code == 201:
            print("✓ Comment creation successful")
        else:
            print(f"✗ Comment creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Comment creation error: {e}")
        return False
    
    print("\n🎉 All tests passed! The API is working correctly.")
    return True

if __name__ == "__main__":
    test_api()
