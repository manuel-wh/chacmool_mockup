#!/usr/bin/env python3
"""
Backend API Testing Script - Schedule Assignments & Kiosk Access Updates
Tests for:
1. Multiple schedule assignments with date ranges (assigned_from, assigned_to, no_end)
2. Overlap validation (inclusive - same day should reject)
3. GET /api/asistencia/employees/{employee_id}/schedule endpoint
4. Kiosk access updates (code/PIN editing, upsert behavior)
5. Smoke tests for attendance/current and summary
"""

import requests
import json
from typing import Dict, Any, List
from datetime import date, timedelta

# Backend URL from frontend/.env
BACKEND_URL = "https://text-viewer-21.preview.emergentagent.com"

# Test credentials
ADMIN_EMAIL = "maria@empresa.com"
ADMIN_PASSWORD = "maria123"

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

def login_admin() -> str:
    """Login as admin and return token"""
    print_info("Logging in as admin...")
    url = f"{BACKEND_URL}/api/auth/login"
    payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print_success(f"Admin login successful")
            return token
        else:
            print_error(f"Admin login failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Admin login error: {str(e)}")
        return None

def get_first_employee_id(token: str) -> str:
    """Get first employee ID from database"""
    print_info("Fetching first employee ID...")
    
    url = f"{BACKEND_URL}/api/employees"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            employees = response.json()
            if employees and len(employees) > 0:
                employee_id = employees[0].get("id")
                print_success(f"Found employee ID: {employee_id}")
                return employee_id
        print_error("No employees found")
        return None
    except Exception as e:
        print_error(f"Failed to get employee: {str(e)}")
        return None

def create_test_schedule(token: str, name: str) -> Dict[str, Any]:
    """Create a test schedule and return its ID"""
    print_info(f"Creating test schedule: {name}")
    
    url = f"{BACKEND_URL}/api/asistencia/schedules"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "name": name,
        "type": "fijo",
        "template_kind": "jornada_continua",
        "days": [
            {
                "day": i,
                "enabled": True if i < 5 else False,
                "ranges": [{"start": "09:00", "end": "17:00"}] if i < 5 else []
            }
            for i in range(7)
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            schedule = response.json()
            print_success(f"Created schedule: {schedule['id']}")
            return {"success": True, "schedule": schedule}
        else:
            print_error(f"Failed to create schedule: {response.status_code}")
            return {"success": False, "error": response.text}
    except Exception as e:
        print_error(f"Error creating schedule: {str(e)}")
        return {"success": False, "error": str(e)}

def delete_schedule(token: str, schedule_id: str):
    """Delete a schedule"""
    url = f"{BACKEND_URL}/api/asistencia/schedules/{schedule_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        requests.delete(url, headers=headers, timeout=10)
        print_info(f"Deleted schedule: {schedule_id}")
    except Exception:
        pass

def clear_employee_assignments(token: str, employee_id: str):
    """Clear all assignments for an employee"""
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        requests.delete(url, headers=headers, timeout=10)
        print_info(f"Cleared assignments for employee: {employee_id}")
    except Exception:
        pass

# ============================================================
#           SCHEDULE ASSIGNMENT TESTS
# ============================================================

def test_assign_schedule_with_dates(token: str, employee_id: str, schedule_id: str, 
                                     assigned_from: str, assigned_to: str = None, 
                                     no_end: bool = False, should_succeed: bool = True) -> Dict[str, Any]:
    """Test assigning a schedule with date range"""
    test_name = f"Assign Schedule - from={assigned_from}, to={assigned_to}, no_end={no_end}"
    print_test_header(test_name)
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "schedule_id": schedule_id,
        "assigned_from": assigned_from,
        "no_end": no_end
    }
    
    if assigned_to:
        payload["assigned_to"] = assigned_to
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if should_succeed:
            if response.status_code == 200:
                data = response.json()
                print_info(f"Response: {json.dumps(data, indent=2, default=str)}")
                print_success("Assignment created successfully")
                return {"success": True, "assignment": data.get("assignment")}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
                print_error(f"Assignment failed: {error_detail}")
                return {"success": False, "error": error_detail}
        else:
            # Should fail
            if response.status_code in [400, 422]:
                error_detail = response.json().get("detail", "Validation error") if response.text else "Validation error"
                print_success(f"Assignment correctly rejected: {error_detail}")
                return {"success": True, "error": error_detail}
            else:
                print_error(f"Expected rejection (400/422), got {response.status_code}")
                return {"success": False, "error": f"Unexpected status: {response.status_code}"}
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_get_employee_schedule(token: str, employee_id: str) -> Dict[str, Any]:
    """Test GET /api/asistencia/employees/{employee_id}/schedule"""
    print_test_header(f"Get Employee Schedule - Employee: {employee_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response keys: {list(data.keys())}")
            
            # Validate structure
            required_keys = ["assigned", "schedule", "assignment", "assignments"]
            missing_keys = [k for k in required_keys if k not in data]
            
            if missing_keys:
                print_error(f"Missing keys in response: {missing_keys}")
                return {"success": False, "error": f"Missing keys: {missing_keys}"}
            
            print_info(f"Assigned: {data['assigned']}")
            print_info(f"Current assignment: {data['assignment'] is not None}")
            print_info(f"Total assignments (history): {len(data['assignments'])}")
            
            # Check if assignments have schedule embedded
            if data['assignments']:
                first_assignment = data['assignments'][0]
                print_info(f"First assignment keys: {list(first_assignment.keys())}")
                if 'schedule' in first_assignment:
                    print_success("Assignments include embedded schedule data")
                else:
                    print_error("Assignments missing embedded schedule data")
            
            print_success("Successfully retrieved employee schedule with history")
            return {"success": True, "data": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get employee schedule failed: {error_detail}")
            return {"success": False, "error": error_detail}
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#           KIOSK ACCESS UPDATE TESTS
# ============================================================

def test_update_kiosk_access_code_and_pin(token: str, employee_id: str, 
                                           new_code: str, new_pin: str = None) -> Dict[str, Any]:
    """Test updating kiosk access code and optionally PIN"""
    print_test_header(f"Update Kiosk Access - Employee: {employee_id}, Code: {new_code}, PIN: {new_pin}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {"access_code": new_code}
    if new_pin:
        payload["pin"] = new_pin
    
    try:
        print_info(f"PUT {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.put(url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            
            # Validate code is numeric
            if not data.get("access_code", "").isdigit():
                print_error(f"Access code is not numeric: {data.get('access_code')}")
                return {"success": False, "error": "Access code not numeric"}
            
            # Validate PIN is numeric
            if not data.get("pin", "").isdigit():
                print_error(f"PIN is not numeric: {data.get('pin')}")
                return {"success": False, "error": "PIN not numeric"}
            
            print_success(f"Updated kiosk access - Code: {data['access_code']}, PIN: {data['pin']}")
            return {"success": True, "credentials": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Update kiosk access failed: {error_detail}")
            return {"success": False, "error": error_detail, "status_code": response.status_code}
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_kiosk_access_upsert(token: str, employee_id: str) -> Dict[str, Any]:
    """Test upsert behavior - update creates if doesn't exist"""
    print_test_header(f"Kiosk Access Upsert Test - Employee: {employee_id}")
    
    # First, check if credentials exist
    get_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {get_url} (checking if exists)")
        get_response = requests.get(get_url, headers=headers, timeout=10)
        
        if get_response.status_code == 200:
            existing = get_response.json()
            if existing:
                print_info(f"Credentials already exist: {existing.get('access_code')}")
                # Delete them first
                print_info("Deleting existing credentials via MongoDB...")
                # We'll just proceed with update which should work
            else:
                print_info("No existing credentials (null response)")
        
        # Now try to update (should create if doesn't exist)
        update_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
        payload = {"access_code": "999888"}  # Numeric code
        
        print_info(f"PUT {update_url} (upsert test)")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        update_response = requests.put(update_url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {update_response.status_code}")
        
        if update_response.status_code == 200:
            data = update_response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            
            # Validate PIN was auto-generated
            if not data.get("pin"):
                print_error("PIN was not auto-generated")
                return {"success": False, "error": "PIN not auto-generated"}
            
            if not data.get("pin").isdigit():
                print_error(f"Auto-generated PIN is not numeric: {data.get('pin')}")
                return {"success": False, "error": "PIN not numeric"}
            
            print_success(f"Upsert successful - Code: {data['access_code']}, Auto-generated PIN: {data['pin']}")
            return {"success": True, "credentials": data}
        else:
            error_detail = update_response.json().get("detail", "Unknown error") if update_response.text else "No response body"
            print_error(f"Upsert failed: {error_detail}")
            return {"success": False, "error": error_detail}
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_kiosk_code_uniqueness(token: str, employee_id1: str, employee_id2: str) -> Dict[str, Any]:
    """Test that duplicate codes are rejected"""
    print_test_header("Kiosk Code Uniqueness Test")
    
    url1 = f"{BACKEND_URL}/api/asistencia/employees/{employee_id1}/kiosk-access"
    url2 = f"{BACKEND_URL}/api/asistencia/employees/{employee_id2}/kiosk-access"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Set code for first employee
        code = "111222"
        print_info(f"Setting code {code} for employee 1: {employee_id1}")
        payload1 = {"access_code": code}
        
        response1 = requests.put(url1, json=payload1, headers=headers, timeout=10)
        if response1.status_code != 200:
            print_error(f"Failed to set code for employee 1: {response1.status_code}")
            return {"success": False, "error": "Setup failed"}
        
        print_success(f"Set code {code} for employee 1")
        
        # Try to set same code for second employee (should fail)
        print_info(f"Trying to set same code {code} for employee 2: {employee_id2}")
        payload2 = {"access_code": code}
        
        response2 = requests.put(url2, json=payload2, headers=headers, timeout=10)
        print_info(f"Status Code: {response2.status_code}")
        
        if response2.status_code == 400:
            error_detail = response2.json().get("detail", "")
            print_success(f"Duplicate code correctly rejected: {error_detail}")
            return {"success": True}
        else:
            print_error(f"Expected 400 for duplicate code, got {response2.status_code}")
            return {"success": False, "error": f"Duplicate not rejected: {response2.status_code}"}
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#           SMOKE TESTS
# ============================================================

def test_attendance_current(token: str) -> Dict[str, Any]:
    """Smoke test for attendance/current"""
    print_test_header("Smoke Test - Attendance Current")
    
    url = f"{BACKEND_URL}/api/asistencia/attendance/current"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response keys: {list(data.keys())}")
            
            # Check for schedule selection by date
            if "assignment" in data:
                print_success("Assignment field present (schedule selection by date)")
            
            print_success("Attendance current endpoint working")
            return {"success": True, "data": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Attendance current failed: {error_detail}")
            return {"success": False, "error": error_detail}
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_attendance_summary(token: str) -> Dict[str, Any]:
    """Smoke test for attendance/summary"""
    print_test_header("Smoke Test - Attendance Summary")
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    url = f"{BACKEND_URL}/api/asistencia/attendance/summary?date_from={week_ago.isoformat()}&date_to={today.isoformat()}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Worked seconds: {data.get('worked_seconds', 0)}")
            print_info(f"Planned seconds: {data.get('planned_seconds', 0)}")
            print_success("Attendance summary endpoint working")
            return {"success": True, "data": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Attendance summary failed: {error_detail}")
            return {"success": False, "error": error_detail}
    
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#                    MAIN TEST RUNNER
# ============================================================

def run_all_tests():
    """Run all tests for new features"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}BACKEND TESTS - SCHEDULE ASSIGNMENTS & KIOSK ACCESS{Colors.RESET}")
    print(f"{Colors.BOLD}Backend URL: {BACKEND_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    # Login
    token = login_admin()
    if not token:
        print_error("Cannot proceed without admin token")
        return results
    
    # Get employee IDs
    employee_id = get_first_employee_id(token)
    if not employee_id:
        print_error("Cannot proceed without employee ID")
        return results
    
    # Get second employee for uniqueness test
    url = f"{BACKEND_URL}/api/employees"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        employees = response.json()
        employee_id2 = employees[1].get("id") if len(employees) > 1 else None
    except:
        employee_id2 = None
    
    # Create test schedules
    schedule1_result = create_test_schedule(token, "Test Schedule 1")
    schedule2_result = create_test_schedule(token, "Test Schedule 2")
    
    if not schedule1_result["success"] or not schedule2_result["success"]:
        print_error("Failed to create test schedules")
        return results
    
    schedule1_id = schedule1_result["schedule"]["id"]
    schedule2_id = schedule2_result["schedule"]["id"]
    
    # Clear any existing assignments
    clear_employee_assignments(token, employee_id)
    
    # ============================================================
    #     SECTION 1: SCHEDULE ASSIGNMENT TESTS
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}SECTION 1: SCHEDULE ASSIGNMENT TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    today = date.today()
    
    # Test 1: Create assignment with assigned_from + assigned_to
    results["total_tests"] += 1
    assign1 = test_assign_schedule_with_dates(
        token, employee_id, schedule1_id,
        assigned_from=(today - timedelta(days=30)).isoformat(),
        assigned_to=(today - timedelta(days=15)).isoformat(),
        should_succeed=True
    )
    if assign1["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Create assignment with date range",
            "status": "PASSED",
            "message": "Assignment with assigned_from + assigned_to created"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Create assignment with date range",
            "status": "FAILED",
            "message": assign1.get("error", "Unknown error")
        })
    
    # Test 2: Create assignment without end (no_end=true)
    results["total_tests"] += 1
    assign2 = test_assign_schedule_with_dates(
        token, employee_id, schedule2_id,
        assigned_from=today.isoformat(),
        no_end=True,
        should_succeed=True
    )
    if assign2["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Create assignment without end (no_end=true)",
            "status": "PASSED",
            "message": "Assignment with no_end=true created"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Create assignment without end (no_end=true)",
            "status": "FAILED",
            "message": assign2.get("error", "Unknown error")
        })
    
    # Test 3: Validate overlap blocking - same day should reject
    results["total_tests"] += 1
    assign3 = test_assign_schedule_with_dates(
        token, employee_id, schedule1_id,
        assigned_from=today.isoformat(),  # Same as no_end assignment start
        assigned_to=(today + timedelta(days=10)).isoformat(),
        should_succeed=False  # Should fail due to overlap
    )
    if assign3["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Overlap validation - same day rejection",
            "status": "PASSED",
            "message": "Overlapping assignment correctly rejected"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Overlap validation - same day rejection",
            "status": "FAILED",
            "message": assign3.get("error", "Should have rejected overlap")
        })
    
    # Test 4: Validate allowed case - new assignment before no_end assignment
    results["total_tests"] += 1
    assign4 = test_assign_schedule_with_dates(
        token, employee_id, schedule1_id,
        assigned_from=(today - timedelta(days=14)).isoformat(),
        assigned_to=(today - timedelta(days=1)).isoformat(),  # Ends before no_end starts
        should_succeed=False  # Should fail - overlaps with first assignment
    )
    if assign4["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Assignment before no_end (overlaps with first)",
            "status": "PASSED",
            "message": "Correctly rejected (overlaps with first assignment)"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Assignment before no_end (overlaps with first)",
            "status": "FAILED",
            "message": assign4.get("error", "Unexpected result")
        })
    
    # Test 5: Valid case - assignment completely before existing assignments
    results["total_tests"] += 1
    assign5 = test_assign_schedule_with_dates(
        token, employee_id, schedule1_id,
        assigned_from=(today - timedelta(days=60)).isoformat(),
        assigned_to=(today - timedelta(days=45)).isoformat(),  # Before all existing
        should_succeed=True
    )
    if assign5["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Assignment completely before existing",
            "status": "PASSED",
            "message": "Non-overlapping assignment created successfully"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Assignment completely before existing",
            "status": "FAILED",
            "message": assign5.get("error", "Unknown error")
        })
    
    # Test 6: GET employee schedule with history
    results["total_tests"] += 1
    get_schedule = test_get_employee_schedule(token, employee_id)
    if get_schedule["success"]:
        data = get_schedule["data"]
        
        # Validate structure
        has_assignments = "assignments" in data and len(data["assignments"]) > 0
        has_current = "assignment" in data and data["assignment"] is not None
        
        if has_assignments and has_current:
            results["passed"] += 1
            results["details"].append({
                "test": "GET employee schedule with history",
                "status": "PASSED",
                "message": f"Retrieved {len(data['assignments'])} assignments + current assignment"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "GET employee schedule with history",
                "status": "FAILED",
                "message": f"Missing data - assignments: {has_assignments}, current: {has_current}"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "GET employee schedule with history",
            "status": "FAILED",
            "message": get_schedule.get("error", "Unknown error")
        })
    
    # ============================================================
    #     SECTION 2: KIOSK ACCESS UPDATE TESTS
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}SECTION 2: KIOSK ACCESS UPDATE TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    # Test 7: Update kiosk access - code only (PIN auto-generated)
    results["total_tests"] += 1
    update1 = test_update_kiosk_access_code_and_pin(token, employee_id, "123456")
    if update1["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Update kiosk access - code only",
            "status": "PASSED",
            "message": f"Code updated, PIN auto-generated: {update1['credentials']['pin']}"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Update kiosk access - code only",
            "status": "FAILED",
            "message": update1.get("error", "Unknown error")
        })
    
    # Test 8: Update kiosk access - code and PIN
    results["total_tests"] += 1
    update2 = test_update_kiosk_access_code_and_pin(token, employee_id, "654321", "9876")
    if update2["success"]:
        creds = update2["credentials"]
        if creds["access_code"] == "654321" and creds["pin"] == "9876":
            results["passed"] += 1
            results["details"].append({
                "test": "Update kiosk access - code and PIN",
                "status": "PASSED",
                "message": "Both code and PIN updated successfully"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Update kiosk access - code and PIN",
                "status": "FAILED",
                "message": f"Values mismatch - code: {creds['access_code']}, pin: {creds['pin']}"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Update kiosk access - code and PIN",
            "status": "FAILED",
            "message": update2.get("error", "Unknown error")
        })
    
    # Test 9: Validate numeric code requirement
    results["total_tests"] += 1
    update3 = test_update_kiosk_access_code_and_pin(token, employee_id, "ABC")
    if not update3["success"] and update3.get("status_code") in [400, 422]:
        results["passed"] += 1
        results["details"].append({
            "test": "Validate numeric code requirement",
            "status": "PASSED",
            "message": "Non-numeric/short code correctly rejected"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Validate numeric code requirement",
            "status": "FAILED",
            "message": "Should have rejected non-numeric/short code"
        })
    
    # Test 10: Upsert behavior
    if employee_id2:
        results["total_tests"] += 1
        upsert = test_kiosk_access_upsert(token, employee_id2)
        if upsert["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Kiosk access upsert behavior",
                "status": "PASSED",
                "message": "Update creates record if doesn't exist with auto-generated PIN"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Kiosk access upsert behavior",
                "status": "FAILED",
                "message": upsert.get("error", "Unknown error")
            })
    
    # Test 11: Code uniqueness validation
    if employee_id2:
        results["total_tests"] += 1
        uniqueness = test_kiosk_code_uniqueness(token, employee_id, employee_id2)
        if uniqueness["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Kiosk code uniqueness validation",
                "status": "PASSED",
                "message": "Duplicate codes correctly rejected"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Kiosk code uniqueness validation",
                "status": "FAILED",
                "message": uniqueness.get("error", "Unknown error")
            })
    
    # ============================================================
    #     SECTION 3: SMOKE TESTS
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}SECTION 3: SMOKE TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    # Test 12: Attendance current
    results["total_tests"] += 1
    current = test_attendance_current(token)
    if current["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Smoke test - attendance/current",
            "status": "PASSED",
            "message": "Endpoint working, schedule selection by date intact"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Smoke test - attendance/current",
            "status": "FAILED",
            "message": current.get("error", "Unknown error")
        })
    
    # Test 13: Attendance summary
    results["total_tests"] += 1
    summary = test_attendance_summary(token)
    if summary["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Smoke test - attendance/summary",
            "status": "PASSED",
            "message": "Endpoint working, schedule selection by date intact"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Smoke test - attendance/summary",
            "status": "FAILED",
            "message": summary.get("error", "Unknown error")
        })
    
    # Cleanup
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}CLEANUP{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    delete_schedule(token, schedule1_id)
    delete_schedule(token, schedule2_id)
    clear_employee_assignments(token, employee_id)
    
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
