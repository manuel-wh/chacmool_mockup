#!/usr/bin/env python3
"""
Backend API Testing Script
Tests authentication endpoints for the EvalPro system
"""

import requests
import json
from typing import Dict, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://text-viewer-21.preview.emergentagent.com"

# Test credentials from /app/memory/test_credentials.md
TEST_USERS = [
    {"email": "maria@empresa.com", "password": "maria123", "name": "María", "role": "admin"},
    {"email": "juan@empresa.com", "password": "juan123", "name": "Juan", "role": "employee"}
]

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name: str):
    """Print formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def test_login(email: str, password: str, user_name: str) -> Dict[str, Any]:
    """
    Test login endpoint
    Returns: dict with 'success', 'token', 'user', 'error' keys
    """
    print_test_header(f"Login Test - {user_name} ({email})")
    
    url = f"{BACKEND_URL}/api/auth/login"
    payload = {"email": email, "password": password}
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2, default=str)}")
            
            # Validate response structure
            if "access_token" not in data:
                print_error("Missing 'access_token' in response")
                return {"success": False, "error": "Missing access_token"}
            
            if "user" not in data:
                print_error("Missing 'user' in response")
                return {"success": False, "error": "Missing user object"}
            
            user = data["user"]
            required_user_fields = ["id", "email", "name", "role"]
            missing_fields = [field for field in required_user_fields if field not in user]
            
            if missing_fields:
                print_error(f"Missing user fields: {missing_fields}")
                return {"success": False, "error": f"Missing user fields: {missing_fields}"}
            
            print_success(f"Login successful for {user_name}")
            print_success(f"Access token received: {data['access_token'][:20]}...")
            print_success(f"User data: {user['name']} ({user['email']}) - Role: {user['role']}")
            
            return {
                "success": True,
                "token": data["access_token"],
                "user": user
            }
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Login failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

def test_get_me(token: str, user_name: str) -> Dict[str, Any]:
    """
    Test /api/auth/me endpoint with token
    Returns: dict with 'success', 'user', 'error' keys
    """
    print_test_header(f"Get Current User Test - {user_name}")
    
    url = f"{BACKEND_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        print_info(f"Authorization: Bearer {token[:20]}...")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print_info(f"Response: {json.dumps(user, indent=2, default=str)}")
            
            required_fields = ["id", "email", "name", "role"]
            missing_fields = [field for field in required_fields if field not in user]
            
            if missing_fields:
                print_error(f"Missing user fields: {missing_fields}")
                return {"success": False, "error": f"Missing fields: {missing_fields}"}
            
            print_success(f"Get current user successful for {user_name}")
            print_success(f"User data: {user['name']} ({user['email']}) - Role: {user['role']}")
            
            return {"success": True, "user": user}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get current user failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

def run_all_tests():
    """Run all backend authentication tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}BACKEND AUTHENTICATION TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}Backend URL: {BACKEND_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    # Test each user
    for user in TEST_USERS:
        email = user["email"]
        password = user["password"]
        name = user["name"]
        
        # Test 1: Login
        results["total_tests"] += 1
        login_result = test_login(email, password, name)
        
        if login_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": f"Login - {name}",
                "status": "PASSED",
                "message": f"Successfully logged in as {name}"
            })
            
            # Test 2: Get current user with token
            results["total_tests"] += 1
            me_result = test_get_me(login_result["token"], name)
            
            if me_result["success"]:
                results["passed"] += 1
                results["details"].append({
                    "test": f"Get Me - {name}",
                    "status": "PASSED",
                    "message": f"Successfully retrieved user data for {name}"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": f"Get Me - {name}",
                    "status": "FAILED",
                    "message": me_result.get("error", "Unknown error")
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": f"Login - {name}",
                "status": "FAILED",
                "message": login_result.get("error", "Unknown error")
            })
            # Skip /me test if login failed
            print_info(f"Skipping /api/auth/me test for {name} due to login failure")
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.RESET}")
    print()
    
    for detail in results["details"]:
        status_color = Colors.GREEN if detail["status"] == "PASSED" else Colors.RED
        print(f"{status_color}{detail['status']}{Colors.RESET} - {detail['test']}: {detail['message']}")
    
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    
    # Exit with appropriate code
    exit(0 if results["failed"] == 0 else 1)
