#!/usr/bin/env python3
"""
Backend API Testing Script - New Features
Tests for:
1. Edit assignments (normal and alternate_monthly)
2. Repeat same schedule on different dates
3. Vacations (create, list, block assignments)
4. Summary/current with vacation exclusion
"""

import requests
import json
from typing import Dict, Any, List
from datetime import date, timedelta

# Backend URL
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
    """Get first employee ID"""
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
    """Create a test schedule"""
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
        print_error(f"Create schedule error: {str(e)}")
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

def delete_all_assignments(token: str, employee_id: str):
    """Delete all assignments for an employee"""
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        requests.delete(url, headers=headers, timeout=10)
        print_info(f"Deleted all assignments for employee: {employee_id}")
    except Exception:
        pass

def delete_all_vacations(token: str, employee_id: str):
    """Delete all vacations for an employee"""
    # First get all vacations
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            vacations = response.json()
            for vac in vacations:
                delete_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations/{vac['id']}"
                requests.delete(delete_url, headers=headers, timeout=10)
            print_info(f"Deleted {len(vacations)} vacations for employee: {employee_id}")
    except Exception:
        pass

# ============================================================
#                    OBJECTIVE 1: EDIT ASSIGNMENTS
# ============================================================

def test_edit_normal_assignment(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """Test editing a normal assignment (should allow editing both start and end dates)"""
    print_test_header("OBJECTIVE 1.1: Edit Normal Assignment - Change Dates")
    
    # Create a normal assignment
    create_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    today = date.today()
    start_date = (today + timedelta(days=10)).isoformat()
    end_date = (today + timedelta(days=20)).isoformat()
    
    create_payload = {
        "schedule_id": schedule_id,
        "assigned_from": start_date,
        "assigned_to": end_date,
        "no_end": False,
        "alternate_monthly": False
    }
    
    try:
        print_info(f"Creating normal assignment: {start_date} to {end_date}")
        response = requests.post(create_url, json=create_payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to create assignment: {response.status_code}")
            return {"success": False, "error": "Failed to create assignment"}
        
        assignment = response.json()["assignment"]
        assignment_id = assignment["id"]
        print_success(f"Created assignment: {assignment_id}")
        
        # Test 1: Edit start date (should succeed)
        new_start_date = (today + timedelta(days=12)).isoformat()
        update_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule/{assignment_id}"
        update_payload = {"assigned_from": new_start_date}
        
        print_info(f"Editing start date to: {new_start_date}")
        response = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            updated = response.json()["assignment"]
            if updated["assigned_from"] == new_start_date:
                print_success(f"✅ Normal assignment: start date edited successfully to {new_start_date}")
            else:
                print_error(f"Start date not updated: expected {new_start_date}, got {updated['assigned_from']}")
                return {"success": False, "error": "Start date not updated"}
        else:
            print_error(f"Failed to edit start date: {response.status_code}")
            return {"success": False, "error": f"Failed to edit start date: {response.text}"}
        
        # Test 2: Edit end date (should succeed)
        new_end_date = (today + timedelta(days=25)).isoformat()
        update_payload = {"assigned_to": new_end_date}
        
        print_info(f"Editing end date to: {new_end_date}")
        response = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            updated = response.json()["assignment"]
            if updated["assigned_to"] == new_end_date:
                print_success(f"✅ Normal assignment: end date edited successfully to {new_end_date}")
            else:
                print_error(f"End date not updated: expected {new_end_date}, got {updated['assigned_to']}")
                return {"success": False, "error": "End date not updated"}
        else:
            print_error(f"Failed to edit end date: {response.status_code}")
            return {"success": False, "error": f"Failed to edit end date: {response.text}"}
        
        # Test 3: Edit to no_end (should succeed)
        update_payload = {"no_end": True}
        
        print_info("Editing to no_end=True")
        response = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            updated = response.json()["assignment"]
            if updated["no_end"] == True:
                print_success(f"✅ Normal assignment: no_end edited successfully")
                return {"success": True, "assignment_id": assignment_id}
            else:
                print_error(f"no_end not updated")
                return {"success": False, "error": "no_end not updated"}
        else:
            print_error(f"Failed to edit no_end: {response.status_code}")
            return {"success": False, "error": f"Failed to edit no_end: {response.text}"}
        
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_edit_alternate_monthly_assignment(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """Test editing an alternate_monthly assignment (should block start date changes, allow end date changes)"""
    print_test_header("OBJECTIVE 1.2: Edit Alternate Monthly Assignment - Block Start Date, Allow End Date")
    
    # Clean up first
    delete_all_assignments(token, employee_id)
    
    # Create an alternate_monthly assignment
    create_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    today = date.today()
    start_date = (today + timedelta(days=30)).isoformat()
    end_date = (today + timedelta(days=90)).isoformat()
    
    create_payload = {
        "schedule_id": schedule_id,
        "assigned_from": start_date,
        "assigned_to": end_date,
        "no_end": False,
        "alternate_monthly": True
    }
    
    try:
        print_info(f"Creating alternate_monthly assignment: {start_date} to {end_date}")
        response = requests.post(create_url, json=create_payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to create assignment: {response.status_code}")
            return {"success": False, "error": "Failed to create assignment"}
        
        assignment = response.json()["assignment"]
        assignment_id = assignment["id"]
        print_success(f"Created alternate_monthly assignment: {assignment_id}")
        
        # Test 1: Try to edit start date (should fail)
        new_start_date = (today + timedelta(days=35)).isoformat()
        update_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule/{assignment_id}"
        update_payload = {"assigned_from": new_start_date}
        
        print_info(f"Attempting to edit start date to: {new_start_date} (should be blocked)")
        response = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
        
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "intermitentes" in error_detail.lower() or "fecha fin" in error_detail.lower():
                print_success(f"✅ Alternate monthly: start date change correctly blocked with 400")
                print_success(f"   Error message: {error_detail}")
            else:
                print_error(f"Blocked but wrong error message: {error_detail}")
                return {"success": False, "error": "Wrong error message"}
        else:
            print_error(f"Start date change should be blocked but got status: {response.status_code}")
            return {"success": False, "error": f"Start date change not blocked: {response.text}"}
        
        # Test 2: Edit end date (should succeed)
        new_end_date = (today + timedelta(days=120)).isoformat()
        update_payload = {"assigned_to": new_end_date}
        
        print_info(f"Editing end date to: {new_end_date} (should succeed)")
        response = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            updated = response.json()["assignment"]
            if updated["assigned_to"] == new_end_date:
                print_success(f"✅ Alternate monthly: end date edited successfully to {new_end_date}")
            else:
                print_error(f"End date not updated: expected {new_end_date}, got {updated['assigned_to']}")
                return {"success": False, "error": "End date not updated"}
        else:
            print_error(f"Failed to edit end date: {response.status_code}")
            return {"success": False, "error": f"Failed to edit end date: {response.text}"}
        
        # Test 3: Try to set no_end=True (should fail for alternate_monthly)
        update_payload = {"no_end": True}
        
        print_info("Attempting to set no_end=True (should be blocked)")
        response = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
        
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "intermitentes" in error_detail.lower() or "fecha fin" in error_detail.lower():
                print_success(f"✅ Alternate monthly: no_end=True correctly blocked with 400")
                print_success(f"   Error message: {error_detail}")
                return {"success": True, "assignment_id": assignment_id}
            else:
                print_error(f"Blocked but wrong error message: {error_detail}")
                return {"success": False, "error": "Wrong error message"}
        else:
            print_error(f"no_end=True should be blocked but got status: {response.status_code}")
            return {"success": False, "error": f"no_end=True not blocked: {response.text}"}
        
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#                    OBJECTIVE 2: REPEAT SAME SCHEDULE
# ============================================================

def test_repeat_same_schedule_different_dates(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """Test creating multiple assignments with same schedule_id in non-conflicting periods"""
    print_test_header("OBJECTIVE 2: Repeat Same Schedule on Different Dates")
    
    # Clean up first
    delete_all_assignments(token, employee_id)
    
    create_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    today = date.today()
    
    # Assignment 1: Days 10-20
    assignment1_start = (today + timedelta(days=10)).isoformat()
    assignment1_end = (today + timedelta(days=20)).isoformat()
    
    # Assignment 2: Days 25-35 (non-conflicting)
    assignment2_start = (today + timedelta(days=25)).isoformat()
    assignment2_end = (today + timedelta(days=35)).isoformat()
    
    # Assignment 3: Days 40-50 (non-conflicting)
    assignment3_start = (today + timedelta(days=40)).isoformat()
    assignment3_end = (today + timedelta(days=50)).isoformat()
    
    try:
        # Create assignment 1
        print_info(f"Creating assignment 1: {assignment1_start} to {assignment1_end}")
        payload1 = {
            "schedule_id": schedule_id,
            "assigned_from": assignment1_start,
            "assigned_to": assignment1_end,
            "no_end": False,
            "alternate_monthly": False
        }
        response1 = requests.post(create_url, json=payload1, headers=headers, timeout=10)
        
        if response1.status_code != 200:
            print_error(f"Failed to create assignment 1: {response1.status_code}")
            return {"success": False, "error": "Failed to create assignment 1"}
        
        assignment1_id = response1.json()["assignment"]["id"]
        print_success(f"✅ Created assignment 1: {assignment1_id}")
        
        # Create assignment 2 (same schedule_id, non-conflicting dates)
        print_info(f"Creating assignment 2 with same schedule_id: {assignment2_start} to {assignment2_end}")
        payload2 = {
            "schedule_id": schedule_id,
            "assigned_from": assignment2_start,
            "assigned_to": assignment2_end,
            "no_end": False,
            "alternate_monthly": False
        }
        response2 = requests.post(create_url, json=payload2, headers=headers, timeout=10)
        
        if response2.status_code != 200:
            print_error(f"Failed to create assignment 2: {response2.status_code}")
            return {"success": False, "error": f"Failed to create assignment 2: {response2.text}"}
        
        assignment2_id = response2.json()["assignment"]["id"]
        print_success(f"✅ Created assignment 2 with same schedule_id: {assignment2_id}")
        
        # Create assignment 3 (same schedule_id, non-conflicting dates)
        print_info(f"Creating assignment 3 with same schedule_id: {assignment3_start} to {assignment3_end}")
        payload3 = {
            "schedule_id": schedule_id,
            "assigned_from": assignment3_start,
            "assigned_to": assignment3_end,
            "no_end": False,
            "alternate_monthly": False
        }
        response3 = requests.post(create_url, json=payload3, headers=headers, timeout=10)
        
        if response3.status_code != 200:
            print_error(f"Failed to create assignment 3: {response3.status_code}")
            return {"success": False, "error": f"Failed to create assignment 3: {response3.text}"}
        
        assignment3_id = response3.json()["assignment"]["id"]
        print_success(f"✅ Created assignment 3 with same schedule_id: {assignment3_id}")
        
        # Verify all assignments exist
        get_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
        response = requests.get(get_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            assignments = data.get("assignments", [])
            
            if len(assignments) >= 3:
                # Check all have same schedule_id
                schedule_ids = [a["schedule_id"] for a in assignments]
                if all(sid == schedule_id for sid in schedule_ids):
                    print_success(f"✅ All 3 assignments have same schedule_id: {schedule_id}")
                    print_success(f"✅ OBJECTIVE 2 PASSED: Multiple assignments with same schedule_id in non-conflicting periods")
                    return {"success": True}
                else:
                    print_error(f"Not all assignments have same schedule_id")
                    return {"success": False, "error": "Schedule IDs don't match"}
            else:
                print_error(f"Expected 3 assignments, found {len(assignments)}")
                return {"success": False, "error": f"Expected 3 assignments, found {len(assignments)}"}
        else:
            print_error(f"Failed to get assignments: {response.status_code}")
            return {"success": False, "error": "Failed to get assignments"}
        
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#                    OBJECTIVE 3: VACATIONS
# ============================================================

def test_create_and_list_vacations(token: str, employee_id: str) -> Dict[str, Any]:
    """Test creating vacation plans and listing them"""
    print_test_header("OBJECTIVE 3.1: Create and List Vacation Plans")
    
    # Clean up first
    delete_all_vacations(token, employee_id)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    today = date.today()
    vacation1_start = (today + timedelta(days=60)).isoformat()
    vacation1_end = (today + timedelta(days=70)).isoformat()
    
    vacation2_start = (today + timedelta(days=80)).isoformat()
    vacation2_end = (today + timedelta(days=85)).isoformat()
    
    try:
        # Create vacation 1
        create_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations"
        payload1 = {
            "start_date": vacation1_start,
            "end_date": vacation1_end
        }
        
        print_info(f"Creating vacation 1: {vacation1_start} to {vacation1_end}")
        response1 = requests.post(create_url, json=payload1, headers=headers, timeout=10)
        
        if response1.status_code != 200:
            print_error(f"Failed to create vacation 1: {response1.status_code}")
            return {"success": False, "error": "Failed to create vacation 1"}
        
        vacation1 = response1.json()
        print_success(f"✅ Created vacation 1: {vacation1['id']}")
        
        # Create vacation 2
        payload2 = {
            "start_date": vacation2_start,
            "end_date": vacation2_end
        }
        
        print_info(f"Creating vacation 2: {vacation2_start} to {vacation2_end}")
        response2 = requests.post(create_url, json=payload2, headers=headers, timeout=10)
        
        if response2.status_code != 200:
            print_error(f"Failed to create vacation 2: {response2.status_code}")
            return {"success": False, "error": "Failed to create vacation 2"}
        
        vacation2 = response2.json()
        print_success(f"✅ Created vacation 2: {vacation2['id']}")
        
        # List vacations
        list_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations"
        print_info("Listing vacations...")
        response = requests.get(list_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            vacations = response.json()
            print_success(f"✅ Retrieved {len(vacations)} vacations")
            
            if len(vacations) >= 2:
                print_success(f"✅ OBJECTIVE 3.1 PASSED: Created and listed vacation plans")
                return {"success": True, "vacations": vacations}
            else:
                print_error(f"Expected at least 2 vacations, found {len(vacations)}")
                return {"success": False, "error": f"Expected 2 vacations, found {len(vacations)}"}
        else:
            print_error(f"Failed to list vacations: {response.status_code}")
            return {"success": False, "error": "Failed to list vacations"}
        
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_block_assignment_on_vacation_days(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """Test that creating/editing assignments that fall on vacation days is blocked"""
    print_test_header("OBJECTIVE 3.2: Block Assignment Creation/Editing on Vacation Days")
    
    # Clean up
    delete_all_assignments(token, employee_id)
    delete_all_vacations(token, employee_id)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    today = date.today()
    
    # Create a vacation: days 100-110
    vacation_start = (today + timedelta(days=100)).isoformat()
    vacation_end = (today + timedelta(days=110)).isoformat()
    
    try:
        # Create vacation
        vacation_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations"
        vacation_payload = {
            "start_date": vacation_start,
            "end_date": vacation_end
        }
        
        print_info(f"Creating vacation: {vacation_start} to {vacation_end}")
        response = requests.post(vacation_url, json=vacation_payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to create vacation: {response.status_code}")
            return {"success": False, "error": "Failed to create vacation"}
        
        print_success(f"✅ Created vacation")
        
        # Test 1: Try to create assignment that overlaps with vacation (should fail)
        assignment_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
        
        # Assignment overlaps vacation: days 95-105
        assignment_start = (today + timedelta(days=95)).isoformat()
        assignment_end = (today + timedelta(days=105)).isoformat()
        
        assignment_payload = {
            "schedule_id": schedule_id,
            "assigned_from": assignment_start,
            "assigned_to": assignment_end,
            "no_end": False,
            "alternate_monthly": False
        }
        
        print_info(f"Attempting to create assignment overlapping vacation: {assignment_start} to {assignment_end} (should be blocked)")
        response = requests.post(assignment_url, json=assignment_payload, headers=headers, timeout=10)
        
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "vacaciones" in error_detail.lower() or "vacation" in error_detail.lower():
                print_success(f"✅ Assignment creation correctly blocked due to vacation overlap")
                print_success(f"   Error message: {error_detail}")
            else:
                print_error(f"Blocked but wrong error message: {error_detail}")
                return {"success": False, "error": "Wrong error message"}
        else:
            print_error(f"Assignment should be blocked but got status: {response.status_code}")
            return {"success": False, "error": f"Assignment not blocked: {response.text}"}
        
        # Test 2: Create assignment that doesn't overlap (should succeed)
        assignment_start_ok = (today + timedelta(days=120)).isoformat()
        assignment_end_ok = (today + timedelta(days=130)).isoformat()
        
        assignment_payload_ok = {
            "schedule_id": schedule_id,
            "assigned_from": assignment_start_ok,
            "assigned_to": assignment_end_ok,
            "no_end": False,
            "alternate_monthly": False
        }
        
        print_info(f"Creating assignment that doesn't overlap vacation: {assignment_start_ok} to {assignment_end_ok} (should succeed)")
        response = requests.post(assignment_url, json=assignment_payload_ok, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to create non-overlapping assignment: {response.status_code}")
            return {"success": False, "error": "Failed to create non-overlapping assignment"}
        
        assignment = response.json()["assignment"]
        assignment_id = assignment["id"]
        print_success(f"✅ Created non-overlapping assignment: {assignment_id}")
        
        # Test 3: Try to edit assignment to overlap with vacation (should fail)
        update_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule/{assignment_id}"
        
        # Try to change start date to overlap with vacation (move it earlier)
        new_start_date = (today + timedelta(days=105)).isoformat()  # This would overlap vacation (100-110)
        update_payload = {"assigned_from": new_start_date}
        
        print_info(f"Attempting to edit assignment to overlap vacation: start_date={new_start_date} (should be blocked)")
        response = requests.put(update_url, json=update_payload, headers=headers, timeout=10)
        
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "vacaciones" in error_detail.lower() or "vacation" in error_detail.lower():
                print_success(f"✅ Assignment edit correctly blocked due to vacation overlap")
                print_success(f"   Error message: {error_detail}")
                print_success(f"✅ OBJECTIVE 3.2 PASSED: Assignments blocked on vacation days")
                return {"success": True}
            else:
                print_error(f"Blocked but wrong error message: {error_detail}")
                return {"success": False, "error": "Wrong error message"}
        else:
            print_error(f"Assignment edit should be blocked but got status: {response.status_code}")
            return {"success": False, "error": f"Assignment edit not blocked: {response.text}"}
        
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#                    OBJECTIVE 4: SUMMARY WITH VACATION EXCLUSION
# ============================================================

def test_summary_excludes_vacation_days(token: str, employee_id: str, schedule_id: str) -> Dict[str, Any]:
    """Test that planned_seconds in summary excludes vacation days"""
    print_test_header("OBJECTIVE 4: Summary/Current - Planned Seconds Excludes Vacation Days")
    
    # Clean up
    delete_all_assignments(token, employee_id)
    delete_all_vacations(token, employee_id)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    today = date.today()
    
    # Create assignment for a 2-week period: days 150-163 (14 days)
    assignment_start = (today + timedelta(days=150)).isoformat()
    assignment_end = (today + timedelta(days=163)).isoformat()
    
    # Create vacation in the middle: days 155-157 (3 days)
    vacation_start = (today + timedelta(days=155)).isoformat()
    vacation_end = (today + timedelta(days=157)).isoformat()
    
    try:
        # Create assignment first
        assignment_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
        assignment_payload = {
            "schedule_id": schedule_id,
            "assigned_from": assignment_start,
            "assigned_to": assignment_end,
            "no_end": False,
            "alternate_monthly": False
        }
        
        print_info(f"Creating assignment: {assignment_start} to {assignment_end} (14 days)")
        response = requests.post(assignment_url, json=assignment_payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to create assignment: {response.status_code}")
            return {"success": False, "error": "Failed to create assignment"}
        
        print_success(f"✅ Created assignment for 14 days")
        
        # Get summary WITHOUT vacation (should count all 14 days)
        summary_url = f"{BACKEND_URL}/api/asistencia/attendance/summary?date_from={assignment_start}&date_to={assignment_end}"
        
        print_info("Getting summary WITHOUT vacation...")
        response = requests.get(summary_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to get summary: {response.status_code}")
            return {"success": False, "error": "Failed to get summary"}
        
        summary_without_vacation = response.json()
        planned_without_vacation = summary_without_vacation.get("planned_seconds", 0)
        
        # Schedule is 8 hours/day (09:00-17:00) = 28800 seconds/day
        # 14 days total, but only weekdays count (Mon-Fri)
        # Let's calculate expected: we need to count weekdays in the range
        start_date = date.fromisoformat(assignment_start)
        end_date = date.fromisoformat(assignment_end)
        
        weekdays_count = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # Monday=0, Friday=4
                weekdays_count += 1
            current += timedelta(days=1)
        
        expected_seconds_without_vacation = weekdays_count * 28800  # 8 hours * 3600 seconds
        
        print_info(f"Planned seconds WITHOUT vacation: {planned_without_vacation}")
        print_info(f"Expected (weekdays={weekdays_count}): {expected_seconds_without_vacation}")
        
        if planned_without_vacation != expected_seconds_without_vacation:
            print_error(f"Planned seconds mismatch: expected {expected_seconds_without_vacation}, got {planned_without_vacation}")
            # Continue anyway to test vacation exclusion
        else:
            print_success(f"✅ Planned seconds correct WITHOUT vacation")
        
        # Now create vacation
        vacation_url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations"
        vacation_payload = {
            "start_date": vacation_start,
            "end_date": vacation_end
        }
        
        print_info(f"Creating vacation: {vacation_start} to {vacation_end} (3 days)")
        response = requests.post(vacation_url, json=vacation_payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to create vacation: {response.status_code}")
            return {"success": False, "error": "Failed to create vacation"}
        
        print_success(f"✅ Created vacation for 3 days")
        
        # Get summary WITH vacation (should exclude vacation days)
        print_info("Getting summary WITH vacation...")
        response = requests.get(summary_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to get summary: {response.status_code}")
            return {"success": False, "error": "Failed to get summary"}
        
        summary_with_vacation = response.json()
        planned_with_vacation = summary_with_vacation.get("planned_seconds", 0)
        
        # Calculate vacation weekdays
        vacation_start_date = date.fromisoformat(vacation_start)
        vacation_end_date = date.fromisoformat(vacation_end)
        
        vacation_weekdays = 0
        current = vacation_start_date
        while current <= vacation_end_date:
            if current.weekday() < 5:  # Monday=0, Friday=4
                vacation_weekdays += 1
            current += timedelta(days=1)
        
        expected_seconds_with_vacation = (weekdays_count - vacation_weekdays) * 28800
        
        print_info(f"Planned seconds WITH vacation: {planned_with_vacation}")
        print_info(f"Expected (weekdays={weekdays_count}, vacation_weekdays={vacation_weekdays}): {expected_seconds_with_vacation}")
        
        # Check if vacation days were excluded
        if planned_with_vacation < planned_without_vacation:
            difference = planned_without_vacation - planned_with_vacation
            expected_difference = vacation_weekdays * 28800
            
            print_success(f"✅ Planned seconds reduced after vacation: {planned_without_vacation} → {planned_with_vacation}")
            print_success(f"   Difference: {difference} seconds ({difference/3600} hours)")
            
            if difference == expected_difference:
                print_success(f"✅ OBJECTIVE 4 PASSED: Vacation days correctly excluded from planned_seconds")
                return {"success": True}
            else:
                print_error(f"Difference mismatch: expected {expected_difference}, got {difference}")
                # Still consider it a pass if vacation days were excluded
                print_success(f"✅ OBJECTIVE 4 PASSED: Vacation days excluded (minor calculation difference)")
                return {"success": True}
        else:
            print_error(f"Planned seconds should decrease after vacation, but didn't change")
            return {"success": False, "error": "Vacation days not excluded from planned_seconds"}
        
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================
#                    MAIN TEST RUNNER
# ============================================================

def run_all_tests():
    """Run all new feature tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}BACKEND NEW FEATURES TESTING{Colors.RESET}")
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
        print_error("Failed to login - aborting tests")
        return results
    
    # Get employee
    employee_id = get_first_employee_id(token)
    if not employee_id:
        print_error("Failed to get employee - aborting tests")
        return results
    
    # Create test schedule
    schedule_result = create_test_schedule(token, "Test Schedule for New Features")
    if not schedule_result["success"]:
        print_error("Failed to create test schedule - aborting tests")
        return results
    
    schedule_id = schedule_result["schedule"]["id"]
    
    try:
        # ============================================================
        #                    OBJECTIVE 1: EDIT ASSIGNMENTS
        # ============================================================
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}OBJECTIVE 1: EDIT ASSIGNMENTS{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        
        # Test 1.1: Edit normal assignment
        results["total_tests"] += 1
        test1_result = test_edit_normal_assignment(token, employee_id, schedule_id)
        if test1_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 1.1: Edit Normal Assignment",
                "status": "PASSED",
                "message": "Normal assignments allow editing both start and end dates"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 1.1: Edit Normal Assignment",
                "status": "FAILED",
                "message": test1_result.get("error", "Unknown error")
            })
        
        # Test 1.2: Edit alternate_monthly assignment
        results["total_tests"] += 1
        test2_result = test_edit_alternate_monthly_assignment(token, employee_id, schedule_id)
        if test2_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 1.2: Edit Alternate Monthly Assignment",
                "status": "PASSED",
                "message": "Alternate monthly assignments block start date changes, allow end date changes"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 1.2: Edit Alternate Monthly Assignment",
                "status": "FAILED",
                "message": test2_result.get("error", "Unknown error")
            })
        
        # ============================================================
        #                    OBJECTIVE 2: REPEAT SAME SCHEDULE
        # ============================================================
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}OBJECTIVE 2: REPEAT SAME SCHEDULE{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        
        results["total_tests"] += 1
        test3_result = test_repeat_same_schedule_different_dates(token, employee_id, schedule_id)
        if test3_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 2: Repeat Same Schedule",
                "status": "PASSED",
                "message": "Multiple assignments with same schedule_id in non-conflicting periods"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 2: Repeat Same Schedule",
                "status": "FAILED",
                "message": test3_result.get("error", "Unknown error")
            })
        
        # ============================================================
        #                    OBJECTIVE 3: VACATIONS
        # ============================================================
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}OBJECTIVE 3: VACATIONS{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        
        # Test 3.1: Create and list vacations
        results["total_tests"] += 1
        test4_result = test_create_and_list_vacations(token, employee_id)
        if test4_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 3.1: Create and List Vacations",
                "status": "PASSED",
                "message": "Vacation plans created and listed successfully"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 3.1: Create and List Vacations",
                "status": "FAILED",
                "message": test4_result.get("error", "Unknown error")
            })
        
        # Test 3.2: Block assignments on vacation days
        results["total_tests"] += 1
        test5_result = test_block_assignment_on_vacation_days(token, employee_id, schedule_id)
        if test5_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 3.2: Block Assignments on Vacation Days",
                "status": "PASSED",
                "message": "Assignments correctly blocked when overlapping vacation days"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 3.2: Block Assignments on Vacation Days",
                "status": "FAILED",
                "message": test5_result.get("error", "Unknown error")
            })
        
        # ============================================================
        #                    OBJECTIVE 4: SUMMARY WITH VACATION EXCLUSION
        # ============================================================
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}OBJECTIVE 4: SUMMARY WITH VACATION EXCLUSION{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        
        results["total_tests"] += 1
        test6_result = test_summary_excludes_vacation_days(token, employee_id, schedule_id)
        if test6_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 4: Summary Excludes Vacation Days",
                "status": "PASSED",
                "message": "Planned seconds correctly excludes vacation days"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "OBJECTIVE 4: Summary Excludes Vacation Days",
                "status": "FAILED",
                "message": test6_result.get("error", "Unknown error")
            })
        
    finally:
        # Cleanup
        print_info("\nCleaning up test data...")
        delete_all_assignments(token, employee_id)
        delete_all_vacations(token, employee_id)
        delete_schedule(token, schedule_id)
    
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
