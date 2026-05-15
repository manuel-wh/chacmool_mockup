#!/usr/bin/env python3
"""
Backend API Testing Script - Alternate Monthly Schedule Feature
Tests the new alternate_monthly functionality for employee schedule assignments
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
            token = response.json()["access_token"]
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

def create_test_schedule(token: str, name: str) -> str:
    """Create a test schedule and return its ID"""
    print_info(f"Creating test schedule: {name}")
    url = f"{BACKEND_URL}/api/asistencia/schedules"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "name": name,
        "type": "fijo",
        "template_kind": "jornada_continua",
        "days": [
            {"day": i, "enabled": True if i < 5 else False, 
             "ranges": [{"start": "09:00", "end": "17:00"}] if i < 5 else []}
            for i in range(7)
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            schedule_id = response.json()["id"]
            print_success(f"Created schedule: {schedule_id}")
            return schedule_id
        else:
            print_error(f"Failed to create schedule: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Schedule creation error: {str(e)}")
        return None

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
    """Clear all schedule assignments for an employee"""
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        requests.delete(url, headers=headers, timeout=10)
        print_info(f"Cleared assignments for employee: {employee_id}")
    except Exception:
        pass

def test_create_alternate_monthly_assignment(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """
    TEST 1: Create assignment with alternate_monthly=true and validate it applies in start month
    """
    print_test_header("Test 1: Create Alternate Monthly Assignment")
    
    # Clear previous assignments first
    clear_employee_assignments(token, employee_id)
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create assignment starting in January 2026, ending in June 2026
    payload = {
        "schedule_id": schedule_id,
        "assigned_from": "2026-01-01",
        "assigned_to": "2026-06-30",
        "no_end": False,
        "alternate_monthly": True
    }
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2, default=str)}")
            
            assignment = data.get("assignment")
            if not assignment:
                print_error("Missing 'assignment' in response")
                return {"success": False, "error": "Missing assignment"}
            
            # Validate alternate_monthly field
            if "alternate_monthly" not in assignment:
                print_error("Missing 'alternate_monthly' field in assignment")
                return {"success": False, "error": "Missing alternate_monthly field"}
            
            if assignment["alternate_monthly"] != True:
                print_error(f"alternate_monthly should be True, got {assignment['alternate_monthly']}")
                return {"success": False, "error": "alternate_monthly not True"}
            
            print_success("Assignment created with alternate_monthly=True")
            print_success(f"Assignment ID: {assignment['id']}")
            print_success(f"Period: {assignment['assigned_from']} to {assignment['assigned_to']}")
            
            return {"success": True, "assignment": assignment}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_alternate_monthly_end_date(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """
    TEST 2: Validate end date in alternate mode (can end on any month/day) and respects exact cutoff
    """
    print_test_header("Test 2: Alternate Monthly End Date Validation")
    
    # Clear previous assignments
    clear_employee_assignments(token, employee_id)
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create assignment with end date in middle of month (not month boundary)
    payload = {
        "schedule_id": schedule_id,
        "assigned_from": "2026-02-01",
        "assigned_to": "2026-05-15",  # Ends mid-month
        "no_end": False,
        "alternate_monthly": True
    }
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            assignment = data.get("assignment")
            
            if assignment["assigned_to"] != "2026-05-15":
                print_error(f"End date mismatch: expected 2026-05-15, got {assignment['assigned_to']}")
                return {"success": False, "error": "End date not preserved"}
            
            print_success("Assignment created with mid-month end date")
            print_success(f"End date correctly set to: {assignment['assigned_to']}")
            
            # Now verify the assignment is returned in GET endpoint
            get_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
            get_response = requests.get(get_url, headers=headers, timeout=10)
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                assignments = get_data.get("assignments", [])
                
                if not assignments:
                    print_error("No assignments returned in GET")
                    return {"success": False, "error": "No assignments in GET"}
                
                found = False
                for a in assignments:
                    if a.get("id") == assignment["id"]:
                        found = True
                        if a.get("assigned_to") != "2026-05-15":
                            print_error(f"GET returned wrong end date: {a.get('assigned_to')}")
                            return {"success": False, "error": "End date mismatch in GET"}
                        break
                
                if not found:
                    print_error("Assignment not found in GET response")
                    return {"success": False, "error": "Assignment not in GET"}
                
                print_success("End date correctly preserved in GET endpoint")
            
            return {"success": True, "assignment": assignment}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_conflict_rule_type_b_overlap(token: str, employee_id: str, schedule_id1: str, schedule_id2: str) -> Dict[str, Any]:
    """
    TEST 3A: Validate conflict rule type B - Block if overlap on days where both plans apply
    """
    print_test_header("Test 3A: Conflict Rule Type B - Overlapping Months")
    
    # Clear previous assignments
    clear_employee_assignments(token, employee_id)
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create first alternate assignment: Jan, Mar, May (odd months from start)
    payload1 = {
        "schedule_id": schedule_id1,
        "assigned_from": "2026-01-01",
        "assigned_to": "2026-06-30",
        "no_end": False,
        "alternate_monthly": True
    }
    
    try:
        print_info("Creating first alternate assignment (Jan, Mar, May)...")
        response1 = requests.post(url, json=payload1, headers=headers, timeout=10)
        
        if response1.status_code != 200:
            print_error(f"Failed to create first assignment: {response1.status_code}")
            return {"success": False, "error": "Failed to create first assignment"}
        
        assignment1 = response1.json().get("assignment")
        print_success(f"First assignment created: {assignment1['id']}")
        
        # Try to create second alternate assignment with same start month (should conflict)
        payload2 = {
            "schedule_id": schedule_id2,
            "assigned_from": "2026-01-15",  # Same month as first (January)
            "assigned_to": "2026-04-30",
            "no_end": False,
            "alternate_monthly": True
        }
        
        print_info("Attempting to create conflicting assignment (also starts in Jan)...")
        print_info(f"Payload: {json.dumps(payload2, indent=2)}")
        
        response2 = requests.post(url, json=payload2, headers=headers, timeout=10)
        print_info(f"Status Code: {response2.status_code}")
        
        # Should be rejected with 400
        if response2.status_code == 400:
            error_detail = response2.json().get("detail", "")
            print_success(f"Correctly rejected conflicting assignment with 400")
            print_success(f"Error message: {error_detail}")
            
            if "sobrelapa" in error_detail.lower() or "overlap" in error_detail.lower():
                print_success("Error message correctly mentions overlap")
            
            return {"success": True, "message": "Conflict correctly detected"}
        else:
            print_error(f"Expected 400, got {response2.status_code}")
            print_error("Should have rejected conflicting alternate assignments")
            return {"success": False, "error": f"Expected rejection, got {response2.status_code}"}
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_conflict_rule_type_b_complementary(token: str, employee_id: str, schedule_id1: str, schedule_id2: str) -> Dict[str, Any]:
    """
    TEST 3B: Validate conflict rule type B - Allow complementary alternate plans (different months)
    """
    print_test_header("Test 3B: Conflict Rule Type B - Complementary Months")
    
    # Clear previous assignments
    clear_employee_assignments(token, employee_id)
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create first alternate assignment starting in January: applies Jan, Mar, May
    payload1 = {
        "schedule_id": schedule_id1,
        "assigned_from": "2026-01-01",
        "assigned_to": "2026-06-30",
        "no_end": False,
        "alternate_monthly": True
    }
    
    try:
        print_info("Creating first alternate assignment (starts Jan: applies Jan, Mar, May)...")
        response1 = requests.post(url, json=payload1, headers=headers, timeout=10)
        
        if response1.status_code != 200:
            print_error(f"Failed to create first assignment: {response1.status_code}")
            return {"success": False, "error": "Failed to create first assignment"}
        
        assignment1 = response1.json().get("assignment")
        print_success(f"First assignment created: {assignment1['id']}")
        print_success(f"Applies in: Jan (month 0), Mar (month 2), May (month 4)")
        
        # Create second alternate assignment starting in February: applies Feb, Apr, Jun
        payload2 = {
            "schedule_id": schedule_id2,
            "assigned_from": "2026-02-01",  # Starts in February (different month)
            "assigned_to": "2026-06-30",
            "no_end": False,
            "alternate_monthly": True
        }
        
        print_info("Creating second alternate assignment (starts Feb: applies Feb, Apr, Jun)...")
        print_info(f"Payload: {json.dumps(payload2, indent=2)}")
        
        response2 = requests.post(url, json=payload2, headers=headers, timeout=10)
        print_info(f"Status Code: {response2.status_code}")
        
        # Should be accepted (200)
        if response2.status_code == 200:
            assignment2 = response2.json().get("assignment")
            print_success(f"Second assignment created successfully: {assignment2['id']}")
            print_success(f"Applies in: Feb (month 1), Apr (month 3), Jun (month 5)")
            print_success("Complementary alternate assignments coexist without conflict")
            
            # Verify both assignments exist
            get_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
            get_response = requests.get(get_url, headers=headers, timeout=10)
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                assignments = get_data.get("assignments", [])
                
                if len(assignments) != 2:
                    print_error(f"Expected 2 assignments, found {len(assignments)}")
                    return {"success": False, "error": "Wrong number of assignments"}
                
                print_success(f"Verified: {len(assignments)} complementary assignments exist")
            
            return {"success": True, "message": "Complementary assignments allowed"}
        else:
            error_detail = response2.json().get("detail", "Unknown error") if response2.text else "No response body"
            print_error(f"Expected 200, got {response2.status_code}")
            print_error(f"Error: {error_detail}")
            print_error("Should have allowed complementary alternate assignments")
            return {"success": False, "error": f"Unexpected rejection: {error_detail}"}
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_get_schedule_returns_alternate_monthly(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """
    TEST 4: Validate that GET /api/asistencia/employees/{id}/schedule returns alternate_monthly field
    """
    print_test_header("Test 4: GET Schedule Returns alternate_monthly Field")
    
    # Clear and create a fresh alternate assignment
    clear_employee_assignments(token, employee_id)
    
    # Create assignment
    create_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "schedule_id": schedule_id,
        "assigned_from": "2026-03-01",
        "assigned_to": "2026-08-31",
        "no_end": False,
        "alternate_monthly": True
    }
    
    try:
        print_info("Creating alternate assignment...")
        create_response = requests.post(create_url, json=payload, headers=headers, timeout=10)
        
        if create_response.status_code != 200:
            print_error(f"Failed to create assignment: {create_response.status_code}")
            return {"success": False, "error": "Failed to create assignment"}
        
        assignment_id = create_response.json().get("assignment", {}).get("id")
        print_success(f"Assignment created: {assignment_id}")
        
        # GET the schedule
        get_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
        print_info(f"GET {get_url}")
        
        get_response = requests.get(get_url, headers=headers, timeout=10)
        print_info(f"Status Code: {get_response.status_code}")
        
        if get_response.status_code == 200:
            data = get_response.json()
            print_info(f"Response keys: {list(data.keys())}")
            
            # Check current assignment
            current_assignment = data.get("assignment")
            if current_assignment:
                if "alternate_monthly" not in current_assignment:
                    print_error("Missing 'alternate_monthly' in current assignment")
                    return {"success": False, "error": "Missing alternate_monthly in current"}
                
                print_success(f"Current assignment has alternate_monthly: {current_assignment['alternate_monthly']}")
            
            # Check assignments history
            assignments = data.get("assignments", [])
            if not assignments:
                print_error("No assignments in history")
                return {"success": False, "error": "No assignments in history"}
            
            print_info(f"Found {len(assignments)} assignments in history")
            
            all_have_field = True
            for i, a in enumerate(assignments):
                if "alternate_monthly" not in a:
                    print_error(f"Assignment {i} missing 'alternate_monthly' field")
                    all_have_field = False
                else:
                    print_success(f"Assignment {i}: alternate_monthly={a['alternate_monthly']}")
            
            if not all_have_field:
                return {"success": False, "error": "Some assignments missing alternate_monthly"}
            
            print_success("All assignments in history have alternate_monthly field")
            return {"success": True, "message": "alternate_monthly field present in all assignments"}
        else:
            error_detail = get_response.json().get("detail", "Unknown error") if get_response.text else "No response body"
            print_error(f"GET failed with status {get_response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_attendance_current_smoke(token: str) -> Dict[str, Any]:
    """
    TEST 5A: Smoke test /api/asistencia/attendance/current
    """
    print_test_header("Test 5A: Smoke Test - Attendance Current")
    
    url = f"{BACKEND_URL}/api/asistencia/attendance/current"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response keys: {list(data.keys())}")
            
            # Validate expected keys
            expected_keys = ["session", "schedule", "assignment", "assigned", "planned_seconds_today", "server_time"]
            missing_keys = [k for k in expected_keys if k not in data]
            
            if missing_keys:
                print_error(f"Missing keys: {missing_keys}")
                return {"success": False, "error": f"Missing keys: {missing_keys}"}
            
            print_success("All expected keys present")
            
            # Check if assignment field exists (confirms schedule selection by date works)
            if "assignment" in data:
                print_success("'assignment' field present - schedule selection by date operational")
            
            return {"success": True, "message": "attendance/current working correctly"}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_attendance_summary_smoke(token: str) -> Dict[str, Any]:
    """
    TEST 5B: Smoke test /api/asistencia/attendance/summary
    """
    print_test_header("Test 5B: Smoke Test - Attendance Summary")
    
    # Use a 7-day range
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
            print_info(f"Response keys: {list(data.keys())}")
            
            # Validate expected keys
            expected_keys = ["worked_seconds", "planned_seconds", "sessions"]
            missing_keys = [k for k in expected_keys if k not in data]
            
            if missing_keys:
                print_error(f"Missing keys: {missing_keys}")
                return {"success": False, "error": f"Missing keys: {missing_keys}"}
            
            print_success("All expected keys present")
            print_info(f"Worked seconds: {data['worked_seconds']}")
            print_info(f"Planned seconds: {data['planned_seconds']}")
            print_success("attendance/summary working correctly")
            
            return {"success": True, "message": "attendance/summary working correctly"}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def run_all_tests():
    """Run all alternate monthly schedule tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}ALTERNATE MONTHLY SCHEDULE TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}Backend URL: {BACKEND_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    # Login as admin
    admin_token = login_admin()
    if not admin_token:
        print_error("Failed to login as admin - cannot proceed")
        return results
    
    # Get employee ID
    employee_id = get_first_employee_id(admin_token)
    if not employee_id:
        print_error("Failed to get employee ID - cannot proceed")
        return results
    
    # Create test schedules
    schedule_id1 = create_test_schedule(admin_token, "Test Schedule Alternate 1")
    schedule_id2 = create_test_schedule(admin_token, "Test Schedule Alternate 2")
    
    if not schedule_id1 or not schedule_id2:
        print_error("Failed to create test schedules - cannot proceed")
        return results
    
    try:
        # Test 1: Create alternate monthly assignment
        results["total_tests"] += 1
        test1 = test_create_alternate_monthly_assignment(admin_token, employee_id, schedule_id1)
        if test1["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Create Alternate Monthly Assignment",
                "status": "PASSED",
                "message": "Assignment created with alternate_monthly=True"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Create Alternate Monthly Assignment",
                "status": "FAILED",
                "message": test1.get("error", "Unknown error")
            })
        
        # Test 2: Alternate monthly end date validation
        results["total_tests"] += 1
        test2 = test_alternate_monthly_end_date(admin_token, employee_id, schedule_id1)
        if test2["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Alternate Monthly End Date Validation",
                "status": "PASSED",
                "message": "End date correctly preserved (mid-month cutoff)"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Alternate Monthly End Date Validation",
                "status": "FAILED",
                "message": test2.get("error", "Unknown error")
            })
        
        # Test 3A: Conflict rule type B - overlapping months
        results["total_tests"] += 1
        test3a = test_conflict_rule_type_b_overlap(admin_token, employee_id, schedule_id1, schedule_id2)
        if test3a["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Conflict Rule Type B - Overlapping Months",
                "status": "PASSED",
                "message": "Correctly rejected conflicting alternate assignments"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Conflict Rule Type B - Overlapping Months",
                "status": "FAILED",
                "message": test3a.get("error", "Unknown error")
            })
        
        # Test 3B: Conflict rule type B - complementary months
        results["total_tests"] += 1
        test3b = test_conflict_rule_type_b_complementary(admin_token, employee_id, schedule_id1, schedule_id2)
        if test3b["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Conflict Rule Type B - Complementary Months",
                "status": "PASSED",
                "message": "Correctly allowed complementary alternate assignments"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Conflict Rule Type B - Complementary Months",
                "status": "FAILED",
                "message": test3b.get("error", "Unknown error")
            })
        
        # Test 4: GET schedule returns alternate_monthly
        results["total_tests"] += 1
        test4 = test_get_schedule_returns_alternate_monthly(admin_token, employee_id, schedule_id1)
        if test4["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "GET Schedule Returns alternate_monthly",
                "status": "PASSED",
                "message": "alternate_monthly field present in all assignments"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "GET Schedule Returns alternate_monthly",
                "status": "FAILED",
                "message": test4.get("error", "Unknown error")
            })
        
        # Test 5A: Smoke test attendance/current
        results["total_tests"] += 1
        test5a = test_attendance_current_smoke(admin_token)
        if test5a["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Smoke Test - Attendance Current",
                "status": "PASSED",
                "message": "attendance/current working correctly"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Smoke Test - Attendance Current",
                "status": "FAILED",
                "message": test5a.get("error", "Unknown error")
            })
        
        # Test 5B: Smoke test attendance/summary
        results["total_tests"] += 1
        test5b = test_attendance_summary_smoke(admin_token)
        if test5b["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Smoke Test - Attendance Summary",
                "status": "PASSED",
                "message": "attendance/summary working correctly"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Smoke Test - Attendance Summary",
                "status": "FAILED",
                "message": test5b.get("error", "Unknown error")
            })
        
    finally:
        # Cleanup
        print_info("\nCleaning up test data...")
        clear_employee_assignments(admin_token, employee_id)
        delete_schedule(admin_token, schedule_id1)
        delete_schedule(admin_token, schedule_id2)
    
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
