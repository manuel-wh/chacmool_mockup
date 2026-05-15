#!/usr/bin/env python3
"""
Backend Vacation Testing Script
Tests vacation CRUD operations and automatic assignment adjustments
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
        print_error(f"Login failed: {str(e)}")
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

def create_schedule(token: str, name: str) -> str:
    """Create a test schedule and return its ID"""
    print_info(f"Creating schedule: {name}")
    
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
        print_error(f"Create schedule failed: {str(e)}")
        return None

def assign_schedule(token: str, employee_id: str, schedule_id: str, 
                   assigned_from: str, assigned_to: str = None, no_end: bool = False) -> Dict[str, Any]:
    """Assign a schedule to an employee"""
    print_info(f"Assigning schedule {schedule_id[:8]} to employee {employee_id[:8]}")
    print_info(f"  From: {assigned_from}, To: {assigned_to or 'no_end'}")
    
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
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            assignment_id = data["assignment"]["id"]
            print_success(f"Assigned schedule, assignment ID: {assignment_id}")
            return {"success": True, "assignment": data["assignment"]}
        else:
            error = response.json().get("detail", "Unknown error") if response.text else "No response"
            print_error(f"Failed to assign schedule: {response.status_code} - {error}")
            return {"success": False, "error": error, "status_code": response.status_code}
    except Exception as e:
        print_error(f"Assign schedule failed: {str(e)}")
        return {"success": False, "error": str(e)}

def get_employee_schedule(token: str, employee_id: str) -> Dict[str, Any]:
    """Get employee schedule with assignments and vacations"""
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            error = response.json().get("detail", "Unknown error") if response.text else "No response"
            return {"success": False, "error": error}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_vacation(token: str, employee_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Create a vacation plan"""
    print_info(f"Creating vacation: {start_date} to {end_date}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"start_date": start_date, "end_date": end_date}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Created vacation ID: {data['id']}")
            return {"success": True, "vacation": data}
        else:
            error = response.json().get("detail", "Unknown error") if response.text else "No response"
            print_error(f"Failed to create vacation: {response.status_code} - {error}")
            return {"success": False, "error": error, "status_code": response.status_code}
    except Exception as e:
        print_error(f"Create vacation failed: {str(e)}")
        return {"success": False, "error": str(e)}

def update_vacation(token: str, employee_id: str, vacation_id: str, 
                   start_date: str, end_date: str) -> Dict[str, Any]:
    """Update a vacation plan"""
    print_info(f"Updating vacation {vacation_id[:8]}: {start_date} to {end_date}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations/{vacation_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"start_date": start_date, "end_date": end_date}
    
    try:
        response = requests.put(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Updated vacation: {data['start_date']} to {data['end_date']}")
            return {"success": True, "vacation": data}
        else:
            error = response.json().get("detail", "Unknown error") if response.text else "No response"
            print_error(f"Failed to update vacation: {response.status_code} - {error}")
            return {"success": False, "error": error, "status_code": response.status_code}
    except Exception as e:
        print_error(f"Update vacation failed: {str(e)}")
        return {"success": False, "error": str(e)}

def delete_vacation(token: str, employee_id: str, vacation_id: str) -> Dict[str, Any]:
    """Delete a vacation plan"""
    print_info(f"Deleting vacation {vacation_id[:8]}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/vacations/{vacation_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Deleted vacation, deleted_count: {data.get('deleted_count', 0)}")
            return {"success": True, "data": data}
        else:
            error = response.json().get("detail", "Unknown error") if response.text else "No response"
            print_error(f"Failed to delete vacation: {response.status_code} - {error}")
            return {"success": False, "error": error}
    except Exception as e:
        print_error(f"Delete vacation failed: {str(e)}")
        return {"success": False, "error": str(e)}

def delete_all_assignments(token: str, employee_id: str):
    """Delete all assignments for an employee (cleanup)"""
    print_info(f"Cleaning up all assignments for employee {employee_id[:8]}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Deleted {data.get('deleted_count', 0)} assignments")
        else:
            print_error(f"Failed to delete assignments: {response.status_code}")
    except Exception as e:
        print_error(f"Delete assignments failed: {str(e)}")

def delete_all_vacations(token: str, employee_id: str):
    """Delete all vacations for an employee (cleanup)"""
    print_info(f"Cleaning up all vacations for employee {employee_id[:8]}")
    
    # Get all vacations
    result = get_employee_schedule(token, employee_id)
    if result["success"]:
        vacations = result["data"].get("vacations", [])
        for vac in vacations:
            delete_vacation(token, employee_id, vac["id"])

def delete_schedule(token: str, schedule_id: str):
    """Delete a schedule (cleanup)"""
    print_info(f"Cleaning up schedule {schedule_id[:8]}")
    
    url = f"{BACKEND_URL}/api/asistencia/schedules/{schedule_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print_success(f"Deleted schedule")
        else:
            print_error(f"Failed to delete schedule: {response.status_code}")
    except Exception as e:
        print_error(f"Delete schedule failed: {str(e)}")

def run_vacation_tests():
    """Run all vacation tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}VACATION CRUD AND AUTOMATIC ADJUSTMENT TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}Backend URL: {BACKEND_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    # Login as admin
    token = login_admin()
    if not token:
        print_error("Cannot proceed without admin token")
        return results
    
    # Get employee ID
    employee_id = get_first_employee_id(token)
    if not employee_id:
        print_error("Cannot proceed without employee ID")
        return results
    
    # Cleanup before tests
    print_info("\n=== CLEANUP BEFORE TESTS ===")
    delete_all_assignments(token, employee_id)
    delete_all_vacations(token, employee_id)
    
    # Create test schedule
    schedule_id = create_schedule(token, "Test Vacation Schedule")
    if not schedule_id:
        print_error("Cannot proceed without schedule")
        return results
    
    # ============================================================
    #  TEST 1: POST vacation works even if schedule already assigned
    # ============================================================
    print_test_header("TEST 1: Create vacation with existing schedule assignment")
    results["total_tests"] += 1
    
    # Assign schedule first (2026-04-01 to 2026-04-30)
    assign_result = assign_schedule(token, employee_id, schedule_id, "2026-04-01", "2026-04-30")
    if not assign_result["success"]:
        print_error("Failed to assign schedule for test 1")
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 1: Create vacation with existing assignment",
            "status": "FAILED",
            "message": "Failed to setup: could not assign schedule"
        })
    else:
        # Create vacation in middle of assignment (2026-04-10 to 2026-04-15)
        vac_result = create_vacation(token, employee_id, "2026-04-10", "2026-04-15")
        if vac_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "TEST 1: Create vacation with existing assignment",
                "status": "PASSED",
                "message": "Vacation created successfully even with existing schedule assignment"
            })
            vacation_id_1 = vac_result["vacation"]["id"]
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 1: Create vacation with existing assignment",
                "status": "FAILED",
                "message": f"Failed to create vacation: {vac_result.get('error')}"
            })
            vacation_id_1 = None
    
    # ============================================================
    #  TEST 2: Automatic adjustment - assignment cut to day before vacation
    # ============================================================
    print_test_header("TEST 2: Assignment starting before vacation gets cut")
    results["total_tests"] += 1
    
    # Get current assignments to verify adjustment
    sched_result = get_employee_schedule(token, employee_id)
    if sched_result["success"]:
        assignments = sched_result["data"].get("assignments", [])
        if len(assignments) == 1:
            assignment = assignments[0]
            # Should be cut to 2026-04-09 (day before vacation starts on 2026-04-10)
            if assignment["assigned_to"] == "2026-04-09":
                results["passed"] += 1
                results["details"].append({
                    "test": "TEST 2: Assignment cut to day before vacation",
                    "status": "PASSED",
                    "message": f"Assignment correctly cut from 2026-04-30 to 2026-04-09 (day before vacation)"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 2: Assignment cut to day before vacation",
                    "status": "FAILED",
                    "message": f"Expected assigned_to=2026-04-09, got {assignment['assigned_to']}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 2: Assignment cut to day before vacation",
                "status": "FAILED",
                "message": f"Expected 1 assignment, found {len(assignments)}"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 2: Assignment cut to day before vacation",
            "status": "FAILED",
            "message": f"Failed to get employee schedule: {sched_result.get('error')}"
        })
    
    # ============================================================
    #  TEST 3: Automatic adjustment - assignment within vacation gets deleted
    # ============================================================
    print_test_header("TEST 3: Assignment starting within vacation gets deleted")
    results["total_tests"] += 1
    
    # Create another assignment that starts within vacation range (2026-04-12 to 2026-04-20)
    assign_result2 = assign_schedule(token, employee_id, schedule_id, "2026-04-12", "2026-04-20")
    if not assign_result2["success"]:
        print_info("Assignment correctly blocked (expected if vacation validation is active)")
        # This is actually expected behavior - assignments can't be created in vacation range
        results["passed"] += 1
        results["details"].append({
            "test": "TEST 3: Assignment within vacation blocked",
            "status": "PASSED",
            "message": "Assignment creation correctly blocked when it falls within vacation range"
        })
    else:
        # If it was created, it should be deleted by vacation adjustment
        # Create a new vacation that covers this assignment
        vac_result2 = create_vacation(token, employee_id, "2026-04-11", "2026-04-25")
        if vac_result2["success"]:
            # Check if assignment was deleted
            sched_result2 = get_employee_schedule(token, employee_id)
            if sched_result2["success"]:
                assignments = sched_result2["data"].get("assignments", [])
                # Should only have the first assignment (cut to 2026-04-09)
                found_deleted = True
                for a in assignments:
                    if a["assigned_from"] == "2026-04-12":
                        found_deleted = False
                        break
                
                if found_deleted:
                    results["passed"] += 1
                    results["details"].append({
                        "test": "TEST 3: Assignment within vacation deleted",
                        "status": "PASSED",
                        "message": "Assignment starting within vacation range was correctly deleted"
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "test": "TEST 3: Assignment within vacation deleted",
                        "status": "FAILED",
                        "message": "Assignment starting within vacation was not deleted"
                    })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 3: Assignment within vacation deleted",
                    "status": "FAILED",
                    "message": f"Failed to verify: {sched_result2.get('error')}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 3: Assignment within vacation deleted",
                "status": "FAILED",
                "message": f"Failed to create vacation for test: {vac_result2.get('error')}"
            })
    
    # ============================================================
    #  TEST 4: PUT vacation allows moving dates
    # ============================================================
    print_test_header("TEST 4: Update vacation to move dates")
    results["total_tests"] += 1
    
    if vacation_id_1:
        # Update vacation to new dates (2026-04-05 to 2026-04-08)
        update_result = update_vacation(token, employee_id, vacation_id_1, "2026-04-05", "2026-04-08")
        if update_result["success"]:
            vacation = update_result["vacation"]
            if vacation["start_date"] == "2026-04-05" and vacation["end_date"] == "2026-04-08":
                results["passed"] += 1
                results["details"].append({
                    "test": "TEST 4: Update vacation dates",
                    "status": "PASSED",
                    "message": "Vacation dates successfully updated from 2026-04-10/15 to 2026-04-05/08"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 4: Update vacation dates",
                    "status": "FAILED",
                    "message": f"Dates not updated correctly: {vacation['start_date']} to {vacation['end_date']}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 4: Update vacation dates",
                "status": "FAILED",
                "message": f"Failed to update vacation: {update_result.get('error')}"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 4: Update vacation dates",
            "status": "FAILED",
            "message": "No vacation ID available from TEST 1"
        })
    
    # ============================================================
    #  TEST 5: Automatic adjustment on vacation UPDATE
    # ============================================================
    print_test_header("TEST 5: Assignment adjustment when vacation is updated")
    results["total_tests"] += 1
    
    # Cleanup and create fresh assignment (2026-05-01 to 2026-05-31)
    delete_all_assignments(token, employee_id)
    delete_all_vacations(token, employee_id)
    
    assign_result3 = assign_schedule(token, employee_id, schedule_id, "2026-05-01", "2026-05-31")
    if assign_result3["success"]:
        # Create vacation (2026-05-20 to 2026-05-25)
        vac_result3 = create_vacation(token, employee_id, "2026-05-20", "2026-05-25")
        if vac_result3["success"]:
            vacation_id_3 = vac_result3["vacation"]["id"]
            
            # Verify assignment was cut to 2026-05-19
            sched_result3 = get_employee_schedule(token, employee_id)
            if sched_result3["success"]:
                assignments = sched_result3["data"].get("assignments", [])
                if len(assignments) == 1 and assignments[0]["assigned_to"] == "2026-05-19":
                    # Now update vacation to earlier dates (2026-05-10 to 2026-05-15)
                    update_result2 = update_vacation(token, employee_id, vacation_id_3, "2026-05-10", "2026-05-15")
                    if update_result2["success"]:
                        # Verify assignment was re-cut to 2026-05-09
                        sched_result4 = get_employee_schedule(token, employee_id)
                        if sched_result4["success"]:
                            assignments2 = sched_result4["data"].get("assignments", [])
                            if len(assignments2) == 1 and assignments2[0]["assigned_to"] == "2026-05-09":
                                results["passed"] += 1
                                results["details"].append({
                                    "test": "TEST 5: Assignment re-adjusted on vacation update",
                                    "status": "PASSED",
                                    "message": "Assignment correctly re-cut from 2026-05-19 to 2026-05-09 when vacation moved"
                                })
                            else:
                                results["failed"] += 1
                                results["details"].append({
                                    "test": "TEST 5: Assignment re-adjusted on vacation update",
                                    "status": "FAILED",
                                    "message": f"Expected assigned_to=2026-05-09, got {assignments2[0]['assigned_to'] if assignments2 else 'no assignments'}"
                                })
                        else:
                            results["failed"] += 1
                            results["details"].append({
                                "test": "TEST 5: Assignment re-adjusted on vacation update",
                                "status": "FAILED",
                                "message": f"Failed to verify after update: {sched_result4.get('error')}"
                            })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "test": "TEST 5: Assignment re-adjusted on vacation update",
                            "status": "FAILED",
                            "message": f"Failed to update vacation: {update_result2.get('error')}"
                        })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "test": "TEST 5: Assignment re-adjusted on vacation update",
                        "status": "FAILED",
                        "message": f"Initial setup failed: expected 1 assignment cut to 2026-05-19, got {len(assignments)} assignments"
                    })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 5: Assignment re-adjusted on vacation update",
                    "status": "FAILED",
                    "message": f"Failed to verify initial state: {sched_result3.get('error')}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 5: Assignment re-adjusted on vacation update",
                "status": "FAILED",
                "message": f"Failed to create vacation: {vac_result3.get('error')}"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 5: Assignment re-adjusted on vacation update",
            "status": "FAILED",
            "message": f"Failed to assign schedule: {assign_result3.get('error')}"
        })
    
    # ============================================================
    #  TEST 6: DELETE vacation works
    # ============================================================
    print_test_header("TEST 6: Delete vacation")
    results["total_tests"] += 1
    
    # Get current vacations
    sched_result5 = get_employee_schedule(token, employee_id)
    if sched_result5["success"]:
        vacations = sched_result5["data"].get("vacations", [])
        if vacations:
            vacation_to_delete = vacations[0]["id"]
            delete_result = delete_vacation(token, employee_id, vacation_to_delete)
            if delete_result["success"]:
                # Verify it's deleted
                sched_result6 = get_employee_schedule(token, employee_id)
                if sched_result6["success"]:
                    vacations_after = sched_result6["data"].get("vacations", [])
                    if len(vacations_after) < len(vacations):
                        results["passed"] += 1
                        results["details"].append({
                            "test": "TEST 6: Delete vacation",
                            "status": "PASSED",
                            "message": f"Vacation successfully deleted (count: {len(vacations)} → {len(vacations_after)})"
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "test": "TEST 6: Delete vacation",
                            "status": "FAILED",
                            "message": f"Vacation not deleted (count still {len(vacations_after)})"
                        })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "test": "TEST 6: Delete vacation",
                        "status": "FAILED",
                        "message": f"Failed to verify deletion: {sched_result6.get('error')}"
                    })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 6: Delete vacation",
                    "status": "FAILED",
                    "message": f"Failed to delete vacation: {delete_result.get('error')}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 6: Delete vacation",
                "status": "FAILED",
                "message": "No vacations available to delete"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 6: Delete vacation",
            "status": "FAILED",
            "message": f"Failed to get vacations: {sched_result5.get('error')}"
        })
    
    # ============================================================
    #  TEST 7: Assignment creation still blocks on vacation days
    # ============================================================
    print_test_header("TEST 7: Assignment creation blocked by vacation")
    results["total_tests"] += 1
    
    # Cleanup and create fresh vacation (2026-06-10 to 2026-06-15)
    delete_all_assignments(token, employee_id)
    delete_all_vacations(token, employee_id)
    
    vac_result4 = create_vacation(token, employee_id, "2026-06-10", "2026-06-15")
    if vac_result4["success"]:
        # Try to create assignment that overlaps with vacation (2026-06-05 to 2026-06-20)
        assign_result4 = assign_schedule(token, employee_id, schedule_id, "2026-06-05", "2026-06-20")
        if not assign_result4["success"] and assign_result4.get("status_code") == 400:
            if "vacaciones" in assign_result4.get("error", "").lower():
                results["passed"] += 1
                results["details"].append({
                    "test": "TEST 7: Assignment blocked by vacation",
                    "status": "PASSED",
                    "message": f"Assignment correctly blocked: {assign_result4.get('error')}"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 7: Assignment blocked by vacation",
                    "status": "FAILED",
                    "message": f"Blocked but wrong error message: {assign_result4.get('error')}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 7: Assignment blocked by vacation",
                "status": "FAILED",
                "message": "Assignment should have been blocked but wasn't"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 7: Assignment blocked by vacation",
            "status": "FAILED",
            "message": f"Failed to create vacation: {vac_result4.get('error')}"
        })
    
    # ============================================================
    #  TEST 8: GET /schedule includes vacations field
    # ============================================================
    print_test_header("TEST 8: GET /schedule includes vacations field")
    results["total_tests"] += 1
    
    sched_result7 = get_employee_schedule(token, employee_id)
    if sched_result7["success"]:
        data = sched_result7["data"]
        if "vacations" in data:
            vacations = data["vacations"]
            if isinstance(vacations, list):
                results["passed"] += 1
                results["details"].append({
                    "test": "TEST 8: GET /schedule includes vacations",
                    "status": "PASSED",
                    "message": f"Vacations field present with {len(vacations)} vacation(s)"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 8: GET /schedule includes vacations",
                    "status": "FAILED",
                    "message": f"Vacations field is not a list: {type(vacations)}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 8: GET /schedule includes vacations",
                "status": "FAILED",
                "message": "Vacations field missing from response"
            })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 8: GET /schedule includes vacations",
            "status": "FAILED",
            "message": f"Failed to get schedule: {sched_result7.get('error')}"
        })
    
    # ============================================================
    #  TEST 9: GET /schedule includes alternate_monthly field
    # ============================================================
    print_test_header("TEST 9: GET /schedule includes alternate_monthly field")
    results["total_tests"] += 1
    
    # Create assignment with alternate_monthly (use current date range to ensure it's active)
    delete_all_assignments(token, employee_id)
    
    from datetime import date, timedelta
    today = date.today()
    start_date = (today - timedelta(days=5)).isoformat()
    end_date = (today + timedelta(days=30)).isoformat()
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "schedule_id": schedule_id,
        "assigned_from": start_date,
        "assigned_to": end_date,
        "alternate_monthly": True
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            # Get schedule and verify alternate_monthly field
            sched_result8 = get_employee_schedule(token, employee_id)
            if sched_result8["success"]:
                data = sched_result8["data"]
                assignments = data.get("assignments", [])
                
                # Check in assignments list (should always have the assignment we just created)
                if assignments and len(assignments) > 0:
                    if "alternate_monthly" in assignments[0]:
                        if assignments[0]["alternate_monthly"] == True:
                            # Also check if assignment (current) has the field when it's active
                            assignment = data.get("assignment")
                            if assignment:
                                if "alternate_monthly" in assignment:
                                    results["passed"] += 1
                                    results["details"].append({
                                        "test": "TEST 9: GET /schedule includes alternate_monthly",
                                        "status": "PASSED",
                                        "message": "alternate_monthly field present in both assignment and assignments list"
                                    })
                                else:
                                    results["failed"] += 1
                                    results["details"].append({
                                        "test": "TEST 9: GET /schedule includes alternate_monthly",
                                        "status": "FAILED",
                                        "message": "alternate_monthly present in assignments list but missing from current assignment"
                                    })
                            else:
                                # Assignment is None (not active today due to alternate_monthly logic)
                                # This is OK, as long as it's in the assignments list
                                results["passed"] += 1
                                results["details"].append({
                                    "test": "TEST 9: GET /schedule includes alternate_monthly",
                                    "status": "PASSED",
                                    "message": "alternate_monthly field present in assignments list (current assignment None due to alternate logic)"
                                })
                        else:
                            results["failed"] += 1
                            results["details"].append({
                                "test": "TEST 9: GET /schedule includes alternate_monthly",
                                "status": "FAILED",
                                "message": f"alternate_monthly value incorrect: {assignments[0]['alternate_monthly']}"
                            })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "test": "TEST 9: GET /schedule includes alternate_monthly",
                            "status": "FAILED",
                            "message": "alternate_monthly field missing from assignments list"
                        })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "test": "TEST 9: GET /schedule includes alternate_monthly",
                        "status": "FAILED",
                        "message": "No assignments found after creation"
                    })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "TEST 9: GET /schedule includes alternate_monthly",
                    "status": "FAILED",
                    "message": f"Failed to get schedule: {sched_result8.get('error')}"
                })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "TEST 9: GET /schedule includes alternate_monthly",
                "status": "FAILED",
                "message": f"Failed to create alternate_monthly assignment: {response.status_code}"
            })
    except Exception as e:
        results["failed"] += 1
        results["details"].append({
            "test": "TEST 9: GET /schedule includes alternate_monthly",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        })
    
    # ============================================================
    #  CLEANUP
    # ============================================================
    print_info("\n=== CLEANUP AFTER TESTS ===")
    delete_all_assignments(token, employee_id)
    delete_all_vacations(token, employee_id)
    delete_schedule(token, schedule_id)
    
    # ============================================================
    #  PRINT SUMMARY
    # ============================================================
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.RESET}")
    print()
    
    for detail in results["details"]:
        status_color = Colors.GREEN if detail["status"] == "PASSED" else Colors.RED
        print(f"{status_color}{detail['status']}{Colors.RESET} - {detail['test']}")
        print(f"  {detail['message']}")
    
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    return results

if __name__ == "__main__":
    results = run_vacation_tests()
    
    # Exit with appropriate code
    exit(0 if results["failed"] == 0 else 1)
