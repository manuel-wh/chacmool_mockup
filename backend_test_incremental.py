#!/usr/bin/env python3
"""
Incremental Backend Testing - Kiosk Numeric Code Validation & Permissions
Tests for recent changes:
1. Kiosk access code must be numeric (generation & update validation)
2. GET kiosk-access permissions (admin vs employee)
3. Kiosk punch still works with numeric code + PIN
"""

import requests
import json
from typing import Dict, Any

# Backend URL
BACKEND_URL = "https://text-viewer-21.preview.emergentagent.com"

# Test credentials
ADMIN_USER = {"email": "maria@empresa.com", "password": "maria123", "name": "María"}
EMPLOYEE_USER = {"email": "juan@empresa.com", "password": "juan123", "name": "Juan"}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.RESET}")

def login(email: str, password: str) -> Dict[str, Any]:
    """Login and return token + user data"""
    url = f"{BACKEND_URL}/api/auth/login"
    try:
        resp = requests.post(url, json={"email": email, "password": password}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {"success": True, "token": data["access_token"], "user": data["user"]}
        return {"success": False, "error": resp.json().get("detail", "Login failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_employees(token: str) -> list:
    """Get list of employees"""
    url = f"{BACKEND_URL}/api/employees"
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []

def enable_kiosk(token: str, enabled: bool = True) -> bool:
    """Enable/disable kiosk"""
    url = f"{BACKEND_URL}/api/asistencia/devices"
    try:
        resp = requests.put(
            url,
            json={"kiosco_enabled": enabled},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False

def create_schedule(token: str) -> str:
    """Create a test schedule and return its ID"""
    url = f"{BACKEND_URL}/api/asistencia/schedules"
    payload = {
        "name": "Test Schedule for Kiosk",
        "type": "fijo",
        "template_kind": "jornada_continua",
        "days": [
            {"day": i, "enabled": True if i < 5 else False,
             "ranges": [{"start": "09:00", "end": "17:00"}] if i < 5 else []}
            for i in range(7)
        ]
    }
    try:
        resp = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if resp.status_code == 200:
            return resp.json()["id"]
        return None
    except Exception:
        return None

def assign_schedule(token: str, employee_id: str, schedule_id: str) -> bool:
    """Assign schedule to employee"""
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    try:
        resp = requests.post(
            url,
            json={"schedule_id": schedule_id},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False

# ============================================================
#                    TEST FUNCTIONS
# ============================================================

def test_numeric_code_generation(token: str, employee_id: str) -> Dict[str, Any]:
    """Test 1: Verify that generated access code is numeric"""
    print_header("TEST 1: Numeric Code Generation")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access/generate"
    
    try:
        print_info(f"POST {url}")
        print_info("Payload: {} (auto-generate code)")
        
        resp = requests.post(url, json={}, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("access_code", "")
            pin = data.get("pin", "")
            
            print_info(f"Generated code: {code}")
            print_info(f"Generated PIN: {pin}")
            
            # Validate code is numeric
            if not code.isdigit():
                print_error(f"FAIL: Generated code '{code}' is not numeric")
                return {"success": False, "error": "Code not numeric"}
            
            # Validate PIN is numeric
            if not pin.isdigit():
                print_error(f"FAIL: Generated PIN '{pin}' is not numeric")
                return {"success": False, "error": "PIN not numeric"}
            
            # Validate code length (should be at least 4 digits)
            if len(code) < 4:
                print_error(f"FAIL: Generated code '{code}' is less than 4 digits")
                return {"success": False, "error": "Code too short"}
            
            print_success(f"PASS: Generated code '{code}' is numeric with {len(code)} digits")
            print_success(f"PASS: Generated PIN '{pin}' is numeric with {len(pin)} digits")
            return {"success": True, "credentials": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_numeric_code_custom_valid(token: str, employee_id: str) -> Dict[str, Any]:
    """Test 2: Verify that custom numeric code is accepted"""
    print_header("TEST 2: Custom Numeric Code (Valid)")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access/generate"
    custom_code = "123456"
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {{\"access_code\": \"{custom_code}\"}}")
        
        resp = requests.post(
            url,
            json={"access_code": custom_code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("access_code", "")
            
            print_info(f"Returned code: {code}")
            
            if code != custom_code:
                print_error(f"FAIL: Expected code '{custom_code}', got '{code}'")
                return {"success": False, "error": "Code mismatch"}
            
            print_success(f"PASS: Custom numeric code '{custom_code}' accepted")
            return {"success": True, "credentials": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_numeric_code_custom_non_numeric(token: str, employee_id: str) -> Dict[str, Any]:
    """Test 3: Verify that non-numeric code is normalized (letters removed)"""
    print_header("TEST 3: Custom Non-Numeric Code (Should be normalized)")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access/generate"
    custom_code = "ABC123XYZ"
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {{\"access_code\": \"{custom_code}\"}}")
        
        resp = requests.post(
            url,
            json={"access_code": custom_code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("access_code", "")
            
            print_info(f"Returned code: {code}")
            
            # Should be normalized to "123" (only digits)
            if not code.isdigit():
                print_error(f"FAIL: Returned code '{code}' is not numeric")
                return {"success": False, "error": "Code not normalized"}
            
            if code != "123":
                print_error(f"FAIL: Expected normalized code '123', got '{code}'")
                return {"success": False, "error": "Unexpected normalization"}
            
            print_success(f"PASS: Non-numeric code '{custom_code}' normalized to '{code}'")
            return {"success": True, "credentials": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_numeric_code_too_short(token: str, employee_id: str) -> Dict[str, Any]:
    """Test 4: Verify that code with less than 4 digits is rejected"""
    print_header("TEST 4: Code Too Short (Should Reject)")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access/generate"
    custom_code = "123"  # Only 3 digits
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {{\"access_code\": \"{custom_code}\"}}")
        
        resp = requests.post(
            url,
            json={"access_code": custom_code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 400:
            error = resp.json().get("detail", "")
            print_info(f"Error message: {error}")
            
            if "4 dígitos" in error or "4 digits" in error.lower():
                print_success(f"PASS: Code with 3 digits correctly rejected with 400")
                return {"success": True}
            else:
                print_error(f"FAIL: Rejected but with unexpected error: {error}")
                return {"success": False, "error": "Unexpected error message"}
        else:
            print_error(f"FAIL: Expected 400, got {resp.status_code}")
            return {"success": False, "error": f"Expected 400, got {resp.status_code}"}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_update_numeric_code_valid(token: str, employee_id: str) -> Dict[str, Any]:
    """Test 5: Verify that update with valid numeric code works"""
    print_header("TEST 5: Update with Valid Numeric Code")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    new_code = "789012"
    
    try:
        print_info(f"PUT {url}")
        print_info(f"Payload: {{\"access_code\": \"{new_code}\"}}")
        
        resp = requests.put(
            url,
            json={"access_code": new_code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("access_code", "")
            
            print_info(f"Updated code: {code}")
            
            if code != new_code:
                print_error(f"FAIL: Expected code '{new_code}', got '{code}'")
                return {"success": False, "error": "Code mismatch"}
            
            print_success(f"PASS: Code updated to '{new_code}'")
            return {"success": True, "credentials": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_update_numeric_code_non_numeric(token: str, employee_id: str) -> Dict[str, Any]:
    """Test 6: Verify that update with non-numeric code is normalized"""
    print_header("TEST 6: Update with Non-Numeric Code (Should normalize)")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    new_code = "XYZ456ABC"
    
    try:
        print_info(f"PUT {url}")
        print_info(f"Payload: {{\"access_code\": \"{new_code}\"}}")
        
        resp = requests.put(
            url,
            json={"access_code": new_code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("access_code", "")
            
            print_info(f"Updated code: {code}")
            
            # Should be normalized to "456"
            if not code.isdigit():
                print_error(f"FAIL: Code '{code}' is not numeric")
                return {"success": False, "error": "Code not normalized"}
            
            if code != "456":
                print_error(f"FAIL: Expected normalized code '456', got '{code}'")
                return {"success": False, "error": "Unexpected normalization"}
            
            print_success(f"PASS: Non-numeric code '{new_code}' normalized to '{code}'")
            return {"success": True, "credentials": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_update_code_too_short(token: str, employee_id: str) -> Dict[str, Any]:
    """Test 7: Verify that update with code < 4 digits is rejected"""
    print_header("TEST 7: Update with Code Too Short (Should Reject)")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    new_code = "12"  # Only 2 digits
    
    try:
        print_info(f"PUT {url}")
        print_info(f"Payload: {{\"access_code\": \"{new_code}\"}}")
        
        resp = requests.put(
            url,
            json={"access_code": new_code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 400:
            error = resp.json().get("detail", "")
            print_info(f"Error message: {error}")
            
            if "4 dígitos" in error or "4 digits" in error.lower():
                print_success(f"PASS: Code with 2 digits correctly rejected with 400")
                return {"success": True}
            else:
                print_error(f"FAIL: Rejected but with unexpected error: {error}")
                return {"success": False, "error": "Unexpected error message"}
        else:
            print_error(f"FAIL: Expected 400, got {resp.status_code}")
            return {"success": False, "error": f"Expected 400, got {resp.status_code}"}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_get_kiosk_access_admin_any_employee(admin_token: str, employee_id: str) -> Dict[str, Any]:
    """Test 8: Admin can query any employee's kiosk access"""
    print_header("TEST 8: Admin Can Query Any Employee")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    
    try:
        print_info(f"GET {url}")
        print_info("User: Admin (María)")
        
        resp = requests.get(url, headers={"Authorization": f"Bearer {admin_token}"}, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            print_success(f"PASS: Admin can query employee {employee_id}")
            return {"success": True, "credentials": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_get_kiosk_access_employee_own(employee_token: str, employee_id: str) -> Dict[str, Any]:
    """Test 9: Employee can query their own kiosk access"""
    print_header("TEST 9: Employee Can Query Own Access")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    
    try:
        print_info(f"GET {url}")
        print_info(f"User: Employee (Juan) querying own ID: {employee_id}")
        
        resp = requests.get(url, headers={"Authorization": f"Bearer {employee_token}"}, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            print_success(f"PASS: Employee can query own access")
            return {"success": True, "credentials": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_get_kiosk_access_employee_other(employee_token: str, other_employee_id: str) -> Dict[str, Any]:
    """Test 10: Employee cannot query another employee's kiosk access"""
    print_header("TEST 10: Employee Cannot Query Other Employee (Should 403)")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{other_employee_id}/kiosk-access"
    
    try:
        print_info(f"GET {url}")
        print_info(f"User: Employee (Juan) querying other employee: {other_employee_id}")
        
        resp = requests.get(url, headers={"Authorization": f"Bearer {employee_token}"}, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 403:
            error = resp.json().get("detail", "")
            print_info(f"Error message: {error}")
            print_success(f"PASS: Employee correctly blocked from querying other employee (403)")
            return {"success": True}
        else:
            print_error(f"FAIL: Expected 403, got {resp.status_code}")
            return {"success": False, "error": f"Expected 403, got {resp.status_code}"}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

def test_kiosk_punch_with_numeric_code(access_code: str, pin: str, expected_action: str) -> Dict[str, Any]:
    """Test 11 & 12: Kiosk punch works with numeric code + PIN"""
    print_header(f"TEST: Kiosk Punch with Numeric Code (Expected: {expected_action})")
    
    url = f"{BACKEND_URL}/api/asistencia/kiosco/punch"
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {{\"access_code\": \"{access_code}\", \"pin\": \"{pin}\"}}")
        
        resp = requests.post(url, json={"access_code": access_code, "pin": pin}, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            action = data.get("action", "")
            message = data.get("message", "")
            
            print_info(f"Action: {action}")
            print_info(f"Message: {message}")
            
            if action != expected_action:
                print_error(f"FAIL: Expected action '{expected_action}', got '{action}'")
                return {"success": False, "error": f"Action mismatch"}
            
            print_success(f"PASS: Kiosk punch successful - Action: {action}")
            return {"success": True, "punch": data}
        else:
            error = resp.json().get("detail", "Unknown error")
            print_error(f"FAIL: Request failed with {resp.status_code}: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"FAIL: Exception - {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#                    MAIN TEST RUNNER
# ============================================================

def main():
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}INCREMENTAL BACKEND TESTS - KIOSK NUMERIC CODE & PERMISSIONS{Colors.RESET}")
    print(f"{Colors.BOLD}Backend URL: {BACKEND_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    results = {"total": 0, "passed": 0, "failed": 0, "details": []}
    
    # Login as admin
    print_header("SETUP: Login as Admin")
    admin_login = login(ADMIN_USER["email"], ADMIN_USER["password"])
    if not admin_login["success"]:
        print_error(f"Admin login failed: {admin_login['error']}")
        return results
    admin_token = admin_login["token"]
    print_success(f"Admin logged in: {ADMIN_USER['name']}")
    
    # Login as employee
    print_header("SETUP: Login as Employee")
    employee_login = login(EMPLOYEE_USER["email"], EMPLOYEE_USER["password"])
    if not employee_login["success"]:
        print_error(f"Employee login failed: {employee_login['error']}")
        return results
    employee_token = employee_login["token"]
    employee_user = employee_login["user"]
    employee_id = employee_user.get("employee_id") or employee_user.get("id")
    print_success(f"Employee logged in: {EMPLOYEE_USER['name']} (ID: {employee_id})")
    
    # Get employees list
    print_header("SETUP: Get Employees")
    employees = get_employees(admin_token)
    if len(employees) < 2:
        print_error("Need at least 2 employees for testing")
        return results
    
    # Find two different employees
    test_employee_1 = employees[0]["id"]
    test_employee_2 = employees[1]["id"] if len(employees) > 1 else employees[0]["id"]
    print_success(f"Test Employee 1: {test_employee_1}")
    print_success(f"Test Employee 2: {test_employee_2}")
    
    # Enable kiosk
    print_header("SETUP: Enable Kiosk")
    if enable_kiosk(admin_token, True):
        print_success("Kiosk enabled")
    else:
        print_error("Failed to enable kiosk")
        return results
    
    # Create and assign schedule
    print_header("SETUP: Create and Assign Schedule")
    schedule_id = create_schedule(admin_token)
    if not schedule_id:
        print_error("Failed to create schedule")
        return results
    print_success(f"Schedule created: {schedule_id}")
    
    if assign_schedule(admin_token, test_employee_1, schedule_id):
        print_success(f"Schedule assigned to employee {test_employee_1}")
    else:
        print_error("Failed to assign schedule")
    
    # ============================================================
    #                    RUN TESTS
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}OBJECTIVE 1: NUMERIC CODE VALIDATION{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    # Test 1: Auto-generate numeric code
    results["total"] += 1
    test1 = test_numeric_code_generation(admin_token, test_employee_1)
    if test1["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Auto-generate numeric code", "status": "PASS"})
        credentials = test1["credentials"]
    else:
        results["failed"] += 1
        results["details"].append({"test": "Auto-generate numeric code", "status": "FAIL", "error": test1.get("error")})
        credentials = None
    
    # Test 2: Custom numeric code (valid)
    results["total"] += 1
    test2 = test_numeric_code_custom_valid(admin_token, test_employee_1)
    if test2["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Custom numeric code (valid)", "status": "PASS"})
    else:
        results["failed"] += 1
        results["details"].append({"test": "Custom numeric code (valid)", "status": "FAIL", "error": test2.get("error")})
    
    # Test 3: Custom non-numeric code (should normalize)
    results["total"] += 1
    test3 = test_numeric_code_custom_non_numeric(admin_token, test_employee_1)
    if test3["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Non-numeric code normalization", "status": "PASS"})
    else:
        results["failed"] += 1
        results["details"].append({"test": "Non-numeric code normalization", "status": "FAIL", "error": test3.get("error")})
    
    # Test 4: Code too short (should reject)
    results["total"] += 1
    test4 = test_numeric_code_too_short(admin_token, test_employee_1)
    if test4["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Reject code < 4 digits (generate)", "status": "PASS"})
    else:
        results["failed"] += 1
        results["details"].append({"test": "Reject code < 4 digits (generate)", "status": "FAIL", "error": test4.get("error")})
    
    # Re-generate valid credentials for update tests
    regen = test_numeric_code_custom_valid(admin_token, test_employee_1)
    if regen["success"]:
        credentials = regen["credentials"]
    
    # Test 5: Update with valid numeric code
    results["total"] += 1
    test5 = test_update_numeric_code_valid(admin_token, test_employee_1)
    if test5["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Update with valid numeric code", "status": "PASS"})
        credentials = test5["credentials"]
    else:
        results["failed"] += 1
        results["details"].append({"test": "Update with valid numeric code", "status": "FAIL", "error": test5.get("error")})
    
    # Test 6: Update with non-numeric code (should normalize)
    results["total"] += 1
    test6 = test_update_numeric_code_non_numeric(admin_token, test_employee_1)
    if test6["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Update non-numeric code normalization", "status": "PASS"})
        credentials = test6["credentials"]
    else:
        results["failed"] += 1
        results["details"].append({"test": "Update non-numeric code normalization", "status": "FAIL", "error": test6.get("error")})
    
    # Test 7: Update with code too short (should reject)
    results["total"] += 1
    test7 = test_update_code_too_short(admin_token, test_employee_1)
    if test7["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Reject code < 4 digits (update)", "status": "PASS"})
    else:
        results["failed"] += 1
        results["details"].append({"test": "Reject code < 4 digits (update)", "status": "FAIL", "error": test7.get("error")})
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}OBJECTIVE 2: GET KIOSK-ACCESS PERMISSIONS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    # Setup: Generate credentials for test_employee_2
    gen_result = test_numeric_code_generation(admin_token, test_employee_2)
    if gen_result["success"]:
        print_success(f"Generated credentials for employee {test_employee_2}")
    
    # Test 8: Admin can query any employee
    results["total"] += 1
    test8 = test_get_kiosk_access_admin_any_employee(admin_token, test_employee_2)
    if test8["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Admin can query any employee", "status": "PASS"})
    else:
        results["failed"] += 1
        results["details"].append({"test": "Admin can query any employee", "status": "FAIL", "error": test8.get("error")})
    
    # Test 9: Employee can query own access
    results["total"] += 1
    test9 = test_get_kiosk_access_employee_own(employee_token, employee_id)
    if test9["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Employee can query own access", "status": "PASS"})
    else:
        results["failed"] += 1
        results["details"].append({"test": "Employee can query own access", "status": "FAIL", "error": test9.get("error")})
    
    # Test 10: Employee cannot query other employee
    # Find an employee ID that is NOT the current employee
    other_employee_id = test_employee_1 if test_employee_1 != employee_id else test_employee_2
    results["total"] += 1
    test10 = test_get_kiosk_access_employee_other(employee_token, other_employee_id)
    if test10["success"]:
        results["passed"] += 1
        results["details"].append({"test": "Employee blocked from other employee (403)", "status": "PASS"})
    else:
        results["failed"] += 1
        results["details"].append({"test": "Employee blocked from other employee (403)", "status": "FAIL", "error": test10.get("error")})
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}OBJECTIVE 3: KIOSK PUNCH WITH NUMERIC CODE{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    # Use credentials from test_employee_1
    if credentials:
        access_code = credentials["access_code"]
        pin = credentials["pin"]
        
        # Test 11: First punch (clock_in)
        results["total"] += 1
        test11 = test_kiosk_punch_with_numeric_code(access_code, pin, "clock_in")
        if test11["success"]:
            results["passed"] += 1
            results["details"].append({"test": "Kiosk punch #1 (clock_in)", "status": "PASS"})
        else:
            results["failed"] += 1
            results["details"].append({"test": "Kiosk punch #1 (clock_in)", "status": "FAIL", "error": test11.get("error")})
        
        # Test 12: Second punch (clock_out)
        results["total"] += 1
        test12 = test_kiosk_punch_with_numeric_code(access_code, pin, "clock_out")
        if test12["success"]:
            results["passed"] += 1
            results["details"].append({"test": "Kiosk punch #2 (clock_out)", "status": "PASS"})
        else:
            results["failed"] += 1
            results["details"].append({"test": "Kiosk punch #2 (clock_out)", "status": "FAIL", "error": test12.get("error")})
    else:
        print_error("No credentials available for punch testing")
        results["total"] += 2
        results["failed"] += 2
        results["details"].append({"test": "Kiosk punch #1 (clock_in)", "status": "FAIL", "error": "No credentials"})
        results["details"].append({"test": "Kiosk punch #2 (clock_out)", "status": "FAIL", "error": "No credentials"})
    
    # ============================================================
    #                    CLEANUP
    # ============================================================
    
    print_header("CLEANUP")
    try:
        # Delete schedule
        requests.delete(
            f"{BACKEND_URL}/api/asistencia/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10
        )
        print_info(f"Deleted test schedule {schedule_id}")
    except Exception:
        pass
    
    # ============================================================
    #                    SUMMARY
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"Total Tests: {results['total']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.RESET}")
    print()
    
    for detail in results["details"]:
        status_color = Colors.GREEN if detail["status"] == "PASS" else Colors.RED
        error_msg = f" - {detail.get('error', '')}" if detail["status"] == "FAIL" else ""
        print(f"{status_color}{detail['status']}{Colors.RESET} - {detail['test']}{error_msg}")
    
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    return results

if __name__ == "__main__":
    results = main()
    exit(0 if results["failed"] == 0 else 1)
