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

# ============================================================
#                    KIOSK TESTS
# ============================================================

def test_get_kiosk_access(token: str, employee_id: str) -> Dict[str, Any]:
    """Test getting kiosk access credentials for an employee"""
    print_test_header(f"Get Kiosk Access - Employee: {employee_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print_info(f"Response: {json.dumps(data, indent=2)}")
                print_success(f"Kiosk access found for employee {employee_id}")
                return {"success": True, "credentials": data}
            else:
                print_info("No kiosk access credentials found (null response)")
                return {"success": True, "credentials": None}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get kiosk access failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_generate_kiosk_access(token: str, employee_id: str, custom_code: str = None) -> Dict[str, Any]:
    """Test generating kiosk access credentials"""
    print_test_header(f"Generate Kiosk Access - Employee: {employee_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access/generate"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"access_code": custom_code} if custom_code else {}
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            
            required_fields = ["employee_id", "access_code", "pin"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print_error(f"Missing fields: {missing}")
                return {"success": False, "error": f"Missing fields: {missing}"}
            
            print_success(f"Generated kiosk access - Code: {data['access_code']}, PIN: {data['pin']}")
            return {"success": True, "credentials": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Generate kiosk access failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_update_kiosk_access(token: str, employee_id: str, new_code: str) -> Dict[str, Any]:
    """Test updating kiosk access code"""
    print_test_header(f"Update Kiosk Access - Employee: {employee_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"access_code": new_code}
    
    try:
        print_info(f"PUT {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.put(url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get("access_code") != new_code.strip().upper():
                print_error(f"Code mismatch: expected {new_code.strip().upper()}, got {data.get('access_code')}")
                return {"success": False, "error": "Code mismatch"}
            
            print_success(f"Updated kiosk access code to: {data['access_code']}")
            return {"success": True, "credentials": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Update kiosk access failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_regenerate_pin(token: str, employee_id: str) -> Dict[str, Any]:
    """Test regenerating PIN"""
    print_test_header(f"Regenerate PIN - Employee: {employee_id}")
    
    url = f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/kiosk-access/regenerate-pin"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"POST {url}")
        response = requests.post(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            print_success(f"Regenerated PIN: {data['pin']}")
            return {"success": True, "credentials": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Regenerate PIN failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_kiosk_public_config() -> Dict[str, Any]:
    """Test public kiosk configuration endpoint"""
    print_test_header("Kiosk Public Config")
    
    url = f"{BACKEND_URL}/api/asistencia/kiosco/public-config"
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            print_success(f"Kiosk enabled: {data.get('kiosco_enabled', False)}")
            return {"success": True, "config": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get public config failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_kiosk_punch(access_code: str, pin: str, expected_action: str = None) -> Dict[str, Any]:
    """Test kiosk punch (clock in/out)"""
    print_test_header(f"Kiosk Punch - Code: {access_code}, PIN: {pin}")
    
    url = f"{BACKEND_URL}/api/asistencia/kiosco/punch"
    payload = {"access_code": access_code, "pin": pin}
    
    try:
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(url, json=payload, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2, default=str)}")
            
            action = data.get("action")
            message = data.get("message")
            
            if expected_action and action != expected_action:
                print_error(f"Action mismatch: expected {expected_action}, got {action}")
                return {"success": False, "error": f"Expected {expected_action}, got {action}"}
            
            print_success(f"Punch successful - Action: {action}, Message: {message}")
            return {"success": True, "punch": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Kiosk punch failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail, "status_code": response.status_code}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_enable_kiosk(token: str, enabled: bool = True) -> Dict[str, Any]:
    """Test enabling/disabling kiosk"""
    print_test_header(f"{'Enable' if enabled else 'Disable'} Kiosk")
    
    url = f"{BACKEND_URL}/api/asistencia/devices"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"kiosco_enabled": enabled}
    
    try:
        print_info(f"PUT {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.put(url, json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response: {json.dumps(data, indent=2)}")
            print_success(f"Kiosk {'enabled' if enabled else 'disabled'}")
            return {"success": True, "config": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Enable/disable kiosk failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_attendance_current(token: str) -> Dict[str, Any]:
    """Test getting current attendance session"""
    print_test_header("Get Current Attendance Session")
    
    url = f"{BACKEND_URL}/api/asistencia/attendance/current"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Response keys: {list(data.keys())}")
            print_success("Successfully retrieved current attendance session")
            return {"success": True, "data": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get current attendance failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_attendance_records(token: str) -> Dict[str, Any]:
    """Test getting attendance records"""
    print_test_header("Get Attendance Records")
    
    url = f"{BACKEND_URL}/api/asistencia/attendance/records"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Found {len(data)} attendance records")
            print_success("Successfully retrieved attendance records")
            return {"success": True, "records": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get attendance records failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_attendance_summary(token: str, date_from: str, date_to: str) -> Dict[str, Any]:
    """Test getting attendance summary"""
    print_test_header(f"Get Attendance Summary ({date_from} to {date_to})")
    
    url = f"{BACKEND_URL}/api/asistencia/attendance/summary?date_from={date_from}&date_to={date_to}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print_info(f"GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Worked seconds: {data.get('worked_seconds', 0)}, Planned seconds: {data.get('planned_seconds', 0)}")
            print_success("Successfully retrieved attendance summary")
            return {"success": True, "summary": data}
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.text else "No response body"
            print_error(f"Get attendance summary failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return {"success": False, "error": error_detail}
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}

def get_first_employee_id(token: str) -> str:
    """Helper to get first employee ID from database"""
    print_info("Fetching first employee ID from database...")
    
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
    
    # ============================================================
    #                    KIOSK TESTS
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}SECTION 3: KIOSK TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    # Get an employee ID for testing
    employee_id = get_first_employee_id(admin_token)
    if not employee_id:
        print_error("Cannot proceed with kiosk tests - no employee found")
    else:
        # Test 11: Enable kiosk
        results["total_tests"] += 1
        enable_result = test_enable_kiosk(admin_token, enabled=True)
        if enable_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Enable Kiosk",
                "status": "PASSED",
                "message": "Successfully enabled kiosk"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Enable Kiosk",
                "status": "FAILED",
                "message": enable_result.get("error", "Unknown error")
            })
        
        # Test 12: Get kiosk public config
        results["total_tests"] += 1
        config_result = test_kiosk_public_config()
        if config_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Get Kiosk Public Config",
                "status": "PASSED",
                "message": f"Kiosk enabled: {config_result['config'].get('kiosco_enabled', False)}"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Get Kiosk Public Config",
                "status": "FAILED",
                "message": config_result.get("error", "Unknown error")
            })
        
        # Test 13: Get kiosk access (should be None initially)
        results["total_tests"] += 1
        get_access_result = test_get_kiosk_access(admin_token, employee_id)
        if get_access_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Get Kiosk Access (initial)",
                "status": "PASSED",
                "message": "Successfully retrieved kiosk access (may be null)"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Get Kiosk Access (initial)",
                "status": "FAILED",
                "message": get_access_result.get("error", "Unknown error")
            })
        
        # Test 14: Generate kiosk access with custom code
        results["total_tests"] += 1
        generate_result = test_generate_kiosk_access(admin_token, employee_id, custom_code="TEST123")
        if generate_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Generate Kiosk Access",
                "status": "PASSED",
                "message": f"Generated credentials - Code: {generate_result['credentials']['access_code']}"
            })
            kiosk_credentials = generate_result["credentials"]
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Generate Kiosk Access",
                "status": "FAILED",
                "message": generate_result.get("error", "Unknown error")
            })
            kiosk_credentials = None
        
        # Test 15: Update kiosk access code
        if kiosk_credentials:
            results["total_tests"] += 1
            update_result = test_update_kiosk_access(admin_token, employee_id, "UPDATED456")
            if update_result["success"]:
                results["passed"] += 1
                results["details"].append({
                    "test": "Update Kiosk Access Code",
                    "status": "PASSED",
                    "message": f"Updated code to: {update_result['credentials']['access_code']}"
                })
                kiosk_credentials = update_result["credentials"]
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "Update Kiosk Access Code",
                    "status": "FAILED",
                    "message": update_result.get("error", "Unknown error")
                })
        
        # Test 16: Regenerate PIN
        if kiosk_credentials:
            results["total_tests"] += 1
            regen_result = test_regenerate_pin(admin_token, employee_id)
            if regen_result["success"]:
                results["passed"] += 1
                results["details"].append({
                    "test": "Regenerate PIN",
                    "status": "PASSED",
                    "message": f"Regenerated PIN: {regen_result['credentials']['pin']}"
                })
                kiosk_credentials = regen_result["credentials"]
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "Regenerate PIN",
                    "status": "FAILED",
                    "message": regen_result.get("error", "Unknown error")
                })
        
        # Test 17: Kiosk punch with invalid credentials (should fail)
        results["total_tests"] += 1
        invalid_punch = test_kiosk_punch("INVALID", "9999")
        if not invalid_punch["success"] and invalid_punch.get("status_code") == 401:
            results["passed"] += 1
            results["details"].append({
                "test": "Kiosk Punch - Invalid Credentials",
                "status": "PASSED",
                "message": "Correctly rejected invalid credentials with 401"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Kiosk Punch - Invalid Credentials",
                "status": "FAILED",
                "message": "Should have rejected invalid credentials"
            })
        
        # Setup: Create and assign schedule for punch testing
        test_schedule_id = None
        if kiosk_credentials:
            print_info("Setting up schedule for punch testing...")
            # Create a test schedule
            schedule_payload = {
                "name": "Test Kiosk Schedule",
                "type": "fijo",
                "template_kind": "jornada_continua",
                "days": [
                    {"day": i, "enabled": True if i < 5 else False, 
                     "ranges": [{"start": "09:00", "end": "17:00"}] if i < 5 else []}
                    for i in range(7)
                ]
            }
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/asistencia/schedules",
                    json=schedule_payload,
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    test_schedule_id = resp.json()["id"]
                    print_success(f"Created test schedule: {test_schedule_id}")
                    
                    # Assign schedule to employee
                    assign_resp = requests.post(
                        f"{BACKEND_URL}/api/asistencia/employees/{employee_id}/schedule",
                        json={"schedule_id": test_schedule_id},
                        headers={"Authorization": f"Bearer {admin_token}"},
                        timeout=10
                    )
                    if assign_resp.status_code == 200:
                        print_success(f"Assigned schedule to employee {employee_id}")
                    else:
                        print_error(f"Failed to assign schedule: {assign_resp.status_code}")
                else:
                    print_error(f"Failed to create schedule: {resp.status_code}")
            except Exception as e:
                print_error(f"Setup failed: {str(e)}")
        
        # Test 18: First kiosk punch (clock_in)
        if kiosk_credentials and test_schedule_id:
            results["total_tests"] += 1
            punch1 = test_kiosk_punch(
                kiosk_credentials["access_code"],
                kiosk_credentials["pin"],
                expected_action="clock_in"
            )
            if punch1["success"]:
                results["passed"] += 1
                results["details"].append({
                    "test": "Kiosk Punch #1 (clock_in)",
                    "status": "PASSED",
                    "message": f"First punch successful - Action: {punch1['punch']['action']}"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "Kiosk Punch #1 (clock_in)",
                    "status": "FAILED",
                    "message": punch1.get("error", "Unknown error")
                })
        
        # Test 19: Second kiosk punch (clock_out)
        if kiosk_credentials and test_schedule_id:
            results["total_tests"] += 1
            punch2 = test_kiosk_punch(
                kiosk_credentials["access_code"],
                kiosk_credentials["pin"],
                expected_action="clock_out"
            )
            if punch2["success"]:
                results["passed"] += 1
                results["details"].append({
                    "test": "Kiosk Punch #2 (clock_out)",
                    "status": "PASSED",
                    "message": f"Second punch successful - Action: {punch2['punch']['action']}"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "Kiosk Punch #2 (clock_out)",
                    "status": "FAILED",
                    "message": punch2.get("error", "Unknown error")
                })
        
        # Cleanup: Delete test schedule
        if test_schedule_id:
            try:
                requests.delete(
                    f"{BACKEND_URL}/api/asistencia/schedules/{test_schedule_id}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=10
                )
                print_info(f"Cleaned up test schedule {test_schedule_id}")
            except Exception:
                pass
        
        # Test 20: Disable kiosk
        results["total_tests"] += 1
        disable_result = test_enable_kiosk(admin_token, enabled=False)
        if disable_result["success"]:
            results["passed"] += 1
            results["details"].append({
                "test": "Disable Kiosk",
                "status": "PASSED",
                "message": "Successfully disabled kiosk"
            })
        else:
            results["failed"] += 1
            results["details"].append({
                "test": "Disable Kiosk",
                "status": "FAILED",
                "message": disable_result.get("error", "Unknown error")
            })
        
        # Test 21: Kiosk punch with disabled kiosk (should fail)
        if kiosk_credentials:
            results["total_tests"] += 1
            disabled_punch = test_kiosk_punch(
                kiosk_credentials["access_code"],
                kiosk_credentials["pin"]
            )
            if not disabled_punch["success"] and disabled_punch.get("status_code") == 403:
                results["passed"] += 1
                results["details"].append({
                    "test": "Kiosk Punch - Disabled Kiosk",
                    "status": "PASSED",
                    "message": "Correctly rejected punch when kiosk disabled with 403"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "test": "Kiosk Punch - Disabled Kiosk",
                    "status": "FAILED",
                    "message": "Should have rejected punch when kiosk disabled"
                })
    
    # ============================================================
    #                    ATTENDANCE SMOKE TESTS
    # ============================================================
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}SECTION 4: ATTENDANCE SMOKE TESTS{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    
    # Test 22: Get current attendance session
    results["total_tests"] += 1
    current_result = test_attendance_current(admin_token)
    if current_result["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Get Current Attendance",
            "status": "PASSED",
            "message": "Successfully retrieved current attendance session"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Get Current Attendance",
            "status": "FAILED",
            "message": current_result.get("error", "Unknown error")
        })
    
    # Test 23: Get attendance records
    results["total_tests"] += 1
    records_result = test_attendance_records(admin_token)
    if records_result["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Get Attendance Records",
            "status": "PASSED",
            "message": f"Successfully retrieved {len(records_result.get('records', []))} records"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Get Attendance Records",
            "status": "FAILED",
            "message": records_result.get("error", "Unknown error")
        })
    
    # Test 24: Get attendance summary
    from datetime import date, timedelta
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    results["total_tests"] += 1
    summary_result = test_attendance_summary(admin_token, week_ago.isoformat(), today.isoformat())
    if summary_result["success"]:
        results["passed"] += 1
        results["details"].append({
            "test": "Get Attendance Summary",
            "status": "PASSED",
            "message": "Successfully retrieved attendance summary"
        })
    else:
        results["failed"] += 1
        results["details"].append({
            "test": "Get Attendance Summary",
            "status": "FAILED",
            "message": summary_result.get("error", "Unknown error")
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
