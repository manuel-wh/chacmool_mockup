#!/usr/bin/env python3
"""
Backend API Testing Script
Tests authentication and schedule endpoints for the EvalPro system
"""

import requests
import json
from typing import Dict, Any, List

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

# ============================================================
#                    SCHEDULE TESTS
# ============================================================

def test_create_schedule(token: str, template_kind: str, should_succeed: bool = True) -> Dict[str, Any]:
    """
    Test creating a schedule with specific template_kind
    Returns: dict with 'success', 'schedule', 'error' keys
    """
    print_test_header(f"Create Schedule Test - template_kind={template_kind}")
    
    url = f"{BACKEND_URL}/api/asistencia/schedules"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a sample schedule payload
    payload = {
        "name": f"Test Schedule {template_kind}",
        "type": "fijo",
        "template_kind": template_kind,
        "days": [
            {
                "day": 0,  # Monday
                "enabled": True,
                "ranges": [
                    {"start": "09:00", "end": "13:00"},
                    {"start": "14:00", "end": "18:00"}
                ] if template_kind == "jornada_partida" else [
                    {"start": "09:00", "end": "17:00"}
                ]
            },
            {
                "day": 1,  # Tuesday
                "enabled": True,
                "ranges": [
                    {"start": "09:00", "end": "13:00"},
                    {"start": "14:00", "end": "18:00"}
                ] if template_kind == "jornada_partida" else [
                    {"start": "09:00", "end": "17:00"}
                ]
            },
            {
                "day": 2,  # Wednesday
                "enabled": True,
                "ranges": [
                    {"start": "09:00", "end": "13:00"},
                    {"start": "14:00", "end": "18:00"}
                ] if template_kind == "jornada_partida" else [
                    {"start": "09:00", "end": "17:00"}
                ]
            },
            {
                "day": 3,  # Thursday
                "enabled": True,
                "ranges": [
                    {"start": "09:00", "end": "13:00"},
                    {"start": "14:00", "end": "18:00"}
                ] if template_kind == "jornada_partida" else [
                    {"start": "09:00", "end": "17:00"}
                ]
            },
            {
                "day": 4,  # Friday
                "enabled": True,
                "ranges": [
                    {"start": "09:00", "end": "13:00"},
                    {"start": "14:00", "end": "18:00"}
                ] if template_kind == "jornada_partida" else [
                    {"start": "09:00", "end": "17:00"}
                ]
            },
            {
                "day": 5,  # Saturday
                "enabled": False,
                "ranges": []
            },
            {
                "day": 6,  # Sunday
                "enabled": False,
                "ranges": []
            }
        ]
    }
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                print_info(f"Response: {json.dumps(data, indent=2, default=str)}")
                
                # Validate response structure
                required_fields = ["id", "name", "type", "days", "template_kind"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print_error(f"Missing fields in response: {missing_fields}")
                    return {"success": False, "error": f"Missing fields: {missing_fields}"}
                
                if data["template_kind"] != template_kind:
                    print_error(f"template_kind mismatch: expected {template_kind}, got {data['template_kind']}")
                    return {"success": False, "error": "template_kind mismatch"}
                
                print_success(f"Schedule created successfully with template_kind={template_kind}")
                print_success(f"Schedule ID: {data['id']}")
                
                return {"success": True, "schedule": data}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
                print_error(f"Schedule creation failed with status {response.status_code}")
                print_error(f"Error: {error_detail}")
                return {"success": False, "error": error_detail}
        else:
            # Should fail - expecting 422 or 400
            if response.status_code in [422, 400]:
                error_detail = response.json().get("detail", "Validation error") if response.text else "Validation error"
                print_success(f"Schedule creation correctly rejected with status {response.status_code}")
                print_success(f"Error detail: {error_detail}")
                return {"success": True, "error": error_detail}
            else:
                print_error(f"Expected validation error (422/400), got {response.status_code}")
                return {"success": False, "error": f"Unexpected status code: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

def test_list_schedules(token: str) -> Dict[str, Any]:
    """
    Test listing all schedules
    Returns: dict with 'success', 'schedules', 'error' keys
    """
    print_test_header("List Schedules Test")
    
    url = f"{BACKEND_URL}/api/asistencia/schedules"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            schedules = response.json()
            print_info(f"Found {len(schedules)} schedules")
            
            if schedules:
                print_info(f"Sample schedule: {json.dumps(schedules[0], indent=2, default=str)}")
            
            print_success(f"Successfully retrieved {len(schedules)} schedules")
            
            return {"success": True, "schedules": schedules}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"List schedules failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

def test_get_schedule(token: str, schedule_id: str) -> Dict[str, Any]:
    """
    Test getting a specific schedule
    Returns: dict with 'success', 'schedule', 'error' keys
    """
    print_test_header(f"Get Schedule Test - ID: {schedule_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/schedules/{schedule_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            schedule = response.json()
            print_info(f"Response: {json.dumps(schedule, indent=2, default=str)}")
            
            print_success(f"Successfully retrieved schedule: {schedule.get('name')}")
            
            return {"success": True, "schedule": schedule}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get schedule failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

def test_update_schedule(token: str, schedule_id: str, template_kind: str = None, should_succeed: bool = True) -> Dict[str, Any]:
    """
    Test updating a schedule
    Returns: dict with 'success', 'schedule', 'error' keys
    """
    print_test_header(f"Update Schedule Test - ID: {schedule_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/schedules/{schedule_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {"name": f"Updated Schedule {schedule_id[:8]}"}
    if template_kind:
        payload["template_kind"] = template_kind
    
    try:
        print_info(f"PUT {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.put(url, json=payload, headers=headers, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if should_succeed:
            if response.status_code == 200:
                schedule = response.json()
                print_info(f"Response: {json.dumps(schedule, indent=2, default=str)}")
                
                print_success(f"Successfully updated schedule: {schedule.get('name')}")
                
                return {"success": True, "schedule": schedule}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
                print_error(f"Update schedule failed with status {response.status_code}")
                print_error(f"Error: {error_detail}")
                return {"success": False, "error": error_detail}
        else:
            # Should fail - expecting 422 or 400
            if response.status_code in [422, 400]:
                error_detail = response.json().get("detail", "Validation error") if response.text else "Validation error"
                print_success(f"Schedule update correctly rejected with status {response.status_code}")
                print_success(f"Error detail: {error_detail}")
                return {"success": True, "error": error_detail}
            else:
                print_error(f"Expected validation error (422/400), got {response.status_code}")
                return {"success": False, "error": f"Unexpected status code: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

def test_delete_schedule(token: str, schedule_id: str) -> Dict[str, Any]:
    """
    Test deleting a schedule
    Returns: dict with 'success', 'error' keys
    """
    print_test_header(f"Delete Schedule Test - ID: {schedule_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/schedules/{schedule_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"DELETE {url}")
        
        response = requests.delete(url, headers=headers, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            
            print_success(f"Successfully deleted schedule")
            
            return {"success": True}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Delete schedule failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {str(e)}")
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

def run_all_tests():
    """Run all backend tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}BACKEND COMPREHENSIVE TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}Backend URL: {BACKEND_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    admin_token = None
    
    # ============================================================
    #                    AUTHENTICATION TESTS
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}SECTION 1: AUTHENTICATION TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
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
            
            # Save admin token for schedule tests
            if user["role"] == "admin":
                admin_token = login_result["token"]
            
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
    
    # ============================================================
    #                    SCHEDULE TESTS
    # ============================================================
    
    if not admin_token:
        print_error("No admin token available - skipping schedule tests")
        return results
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}SECTION 2: SCHEDULE TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    created_schedule_ids = []
    
    # Test 3: Create schedule with jornada_continua
    results["total_tests"] += 1
    create_continua = test_create_schedule(admin_token, "jornada_continua", should_succeed=True)
    if create_continua["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Create Schedule - jornada_continua",
            "status": "PASSED",
            "message": "Successfully created schedule with jornada_continua"
        })
        created_schedule_ids.append(create_continua["schedule"]["id"])
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Create Schedule - jornada_continua",
            "status": "FAILED",
            "message": create_continua.get("error", "Unknown error")
        })
    
    # Test 4: Create schedule with jornada_partida
    results["total_tests"] += 1
    create_partida = test_create_schedule(admin_token, "jornada_partida", should_succeed=True)
    if create_partida["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Create Schedule - jornada_partida",
            "status": "PASSED",
            "message": "Successfully created schedule with jornada_partida"
        })
        created_schedule_ids.append(create_partida["schedule"]["id"])
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Create Schedule - jornada_partida",
            "status": "FAILED",
            "message": create_partida.get("error", "Unknown error")
        })
    
    # Test 5: Create schedule with personalizado (should fail)
    results["total_tests"] += 1
    create_personalizado = test_create_schedule(admin_token, "personalizado", should_succeed=False)
    if create_personalizado["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Create Schedule - personalizado (should fail)",
            "status": "PASSED",
            "message": "Correctly rejected personalizado template_kind"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Create Schedule - personalizado (should fail)",
            "status": "FAILED",
            "message": create_personalizado.get("error", "Should have rejected personalizado")
        })
    
    # Test 6: List schedules
    results["total_tests"] += 1
    list_result = test_list_schedules(admin_token)
    if list_result["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "List Schedules",
            "status": "PASSED",
            "message": f"Successfully listed {len(list_result['schedules'])} schedules"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "List Schedules",
            "status": "FAILED",
            "message": list_result.get("error", "Unknown error")
        })
    
    # Test 7: Get specific schedule
    if created_schedule_ids:
        results["total_tests"] += 1
        get_result = test_get_schedule(admin_token, created_schedule_ids[0])
        if get_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Get Schedule",
                "status": "PASSED",
                "message": f"Successfully retrieved schedule {created_schedule_ids[0][:8]}"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Get Schedule",
                "status": "FAILED",
                "message": get_result.get("error", "Unknown error")
            })
    
    # Test 8: Update schedule (valid update)
    if created_schedule_ids:
        results["total_tests"] += 1
        update_result = test_update_schedule(admin_token, created_schedule_ids[0], should_succeed=True)
        if update_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Update Schedule - valid",
                "status": "PASSED",
                "message": f"Successfully updated schedule {created_schedule_ids[0][:8]}"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Update Schedule - valid",
                "status": "FAILED",
                "message": update_result.get("error", "Unknown error")
            })
    
    # Test 9: Update schedule with personalizado (should fail)
    if len(created_schedule_ids) > 1:
        results["total_tests"] += 1
        update_personalizado = test_update_schedule(admin_token, created_schedule_ids[1], template_kind="personalizado", should_succeed=False)
        if update_personalizado["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Update Schedule - personalizado (should fail)",
                "status": "PASSED",
                "message": "Correctly rejected personalizado template_kind in update"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Update Schedule - personalizado (should fail)",
                "status": "FAILED",
                "message": update_personalizado.get("error", "Should have rejected personalizado")
            })
    
    # Test 10: Delete schedules (cleanup)
    for schedule_id in created_schedule_ids:
        results["total_tests"] += 1
        delete_result = test_delete_schedule(admin_token, schedule_id)
        if delete_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": f"Delete Schedule - {schedule_id[:8]}",
                "status": "PASSED",
                "message": f"Successfully deleted schedule {schedule_id[:8]}"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": f"Delete Schedule - {schedule_id[:8]}",
                "status": "FAILED",
                "message": delete_result.get("error", "Unknown error")
            })
    
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
