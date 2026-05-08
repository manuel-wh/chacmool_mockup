"""
Test suite for EvalPro - Asistencia / Time tracking module
Tests: Schedules CRUD, Employee schedule assignment, Attendance fichaje flow, Devices config
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kpi-360-hub.preview.emergentagent.com').rstrip('/')

ADMIN_CREDENTIALS = {"email": "admin@empresa.com", "password": "admin123"}
ADMIN_EMP_CREDENTIALS = {"email": "maria@empresa.com", "password": "maria123"}
EMPLOYEE_CREDENTIALS = {"email": "juan@empresa.com", "password": "juan123"}


def _login(creds):
    r = requests.post(f"{BASE_URL}/api/auth/login", json=creds)
    assert r.status_code == 200, f"Login failed for {creds['email']}: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def admin_token():
    return _login(ADMIN_CREDENTIALS)


@pytest.fixture(scope="module")
def maria_token():
    return _login(ADMIN_EMP_CREDENTIALS)


@pytest.fixture(scope="module")
def juan_token():
    return _login(EMPLOYEE_CREDENTIALS)


def _hdr(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ================== AUTH ==================

class TestAuthAsistencia:
    def test_admin_login(self):
        token = _login(ADMIN_CREDENTIALS)
        assert token

    def test_maria_login(self):
        token = _login(ADMIN_EMP_CREDENTIALS)
        assert token

    def test_juan_login(self):
        token = _login(EMPLOYEE_CREDENTIALS)
        assert token


# ================== SCHEDULES CRUD ==================

class TestSchedulesCRUD:

    def _build_days(self):
        # 5 working days L-V 09-13 + 14-18, weekend off
        ranges = [{"start": "09:00", "end": "13:00"}, {"start": "14:00", "end": "18:00"}]
        days = []
        for i in range(7):
            days.append({
                "day": i,
                "enabled": i < 5,
                "ranges": ranges if i < 5 else []
            })
        return days

    def test_list_schedules(self, admin_token):
        r = requests.get(f"{BASE_URL}/api/asistencia/schedules", headers=_hdr(admin_token))
        assert r.status_code == 200, r.text
        assert isinstance(r.json(), list)

    def test_create_schedule_calculates_totals(self, admin_token):
        payload = {
            "name": "TEST_Schedule_CRUD",
            "type": "fijo",
            "days": self._build_days(),
            "template_kind": "jornada_partida"
        }
        r = requests.post(f"{BASE_URL}/api/asistencia/schedules", json=payload, headers=_hdr(admin_token))
        assert r.status_code == 200, r.text
        data = r.json()
        # 5 days * 8h = 40h, 5 weekly_days, 5 breaks (one between two ranges per day)
        assert data["weekly_hours"] == 40.0, f"weekly_hours={data['weekly_hours']}"
        assert data["weekly_days"] == 5
        assert data["breaks_count"] == 5
        assert data["name"] == "TEST_Schedule_CRUD"
        assert "id" in data
        # Save for cleanup/next tests
        pytest.test_schedule_id = data["id"]

    def test_get_schedule(self, admin_token):
        sid = pytest.test_schedule_id
        r = requests.get(f"{BASE_URL}/api/asistencia/schedules/{sid}", headers=_hdr(admin_token))
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_update_schedule_recalcs(self, admin_token):
        sid = pytest.test_schedule_id
        # Reduce to 3 days, single range 09-17 = 8h => 24h, 0 breaks, 3 days
        days = []
        ranges = [{"start": "09:00", "end": "17:00"}]
        for i in range(7):
            days.append({"day": i, "enabled": i < 3, "ranges": ranges if i < 3 else []})
        r = requests.put(
            f"{BASE_URL}/api/asistencia/schedules/{sid}",
            json={"name": "TEST_Schedule_CRUD_v2", "days": days},
            headers=_hdr(admin_token)
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["name"] == "TEST_Schedule_CRUD_v2"
        assert data["weekly_hours"] == 24.0
        assert data["weekly_days"] == 3
        assert data["breaks_count"] == 0

    def test_create_schedule_requires_admin(self, juan_token):
        payload = {"name": "TEST_unauthorized", "type": "fijo", "days": self._build_days()}
        r = requests.post(f"{BASE_URL}/api/asistencia/schedules", json=payload, headers=_hdr(juan_token))
        assert r.status_code in (401, 403), f"Expected forbidden, got {r.status_code}: {r.text}"

    def test_delete_schedule(self, admin_token):
        sid = pytest.test_schedule_id
        r = requests.delete(f"{BASE_URL}/api/asistencia/schedules/{sid}", headers=_hdr(admin_token))
        assert r.status_code == 200
        # Verify it's gone
        r2 = requests.get(f"{BASE_URL}/api/asistencia/schedules/{sid}", headers=_hdr(admin_token))
        assert r2.status_code == 404


# ================== EMPLOYEE SCHEDULE ASSIGNMENT ==================

class TestEmployeeSchedule:

    @pytest.fixture(scope="class")
    def schedule_id(self, admin_token):
        # Create a schedule for assignment tests
        days = [{"day": i, "enabled": i < 5, "ranges": [{"start": "09:00", "end": "17:00"}] if i < 5 else []} for i in range(7)]
        r = requests.post(
            f"{BASE_URL}/api/asistencia/schedules",
            json={"name": "TEST_Schedule_Assign", "type": "fijo", "days": days},
            headers=_hdr(admin_token),
        )
        assert r.status_code == 200, r.text
        sid = r.json()["id"]
        yield sid
        # cleanup
        requests.delete(f"{BASE_URL}/api/asistencia/schedules/{sid}", headers=_hdr(admin_token))

    def test_get_employee_schedule_unassigned(self, admin_token):
        # Use a non-existent employee id
        r = requests.get(f"{BASE_URL}/api/asistencia/employees/9999/schedule", headers=_hdr(admin_token))
        assert r.status_code == 200
        assert r.json()["assigned"] is False

    def test_assign_schedule_requires_admin(self, juan_token, schedule_id):
        r = requests.post(
            f"{BASE_URL}/api/asistencia/employees/2/schedule",
            json={"schedule_id": schedule_id},
            headers=_hdr(juan_token),
        )
        assert r.status_code in (401, 403)

    def test_assign_and_get_schedule(self, admin_token, schedule_id):
        # Assign to employee 2 (juan)
        r = requests.post(
            f"{BASE_URL}/api/asistencia/employees/2/schedule",
            json={"schedule_id": schedule_id},
            headers=_hdr(admin_token),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["assigned"] is True
        assert data["schedule"]["id"] == schedule_id

        # Verify GET
        r2 = requests.get(f"{BASE_URL}/api/asistencia/employees/2/schedule", headers=_hdr(admin_token))
        assert r2.status_code == 200
        assert r2.json()["assigned"] is True

    def test_assign_invalid_schedule(self, admin_token):
        r = requests.post(
            f"{BASE_URL}/api/asistencia/employees/2/schedule",
            json={"schedule_id": "non-existent-id"},
            headers=_hdr(admin_token),
        )
        assert r.status_code == 404

    def test_remove_employee_schedule(self, admin_token, schedule_id):
        # ensure assigned first
        requests.post(
            f"{BASE_URL}/api/asistencia/employees/2/schedule",
            json={"schedule_id": schedule_id},
            headers=_hdr(admin_token),
        )
        r = requests.delete(f"{BASE_URL}/api/asistencia/employees/2/schedule", headers=_hdr(admin_token))
        assert r.status_code == 200
        # Verify
        r2 = requests.get(f"{BASE_URL}/api/asistencia/employees/2/schedule", headers=_hdr(admin_token))
        assert r2.json()["assigned"] is False

    def test_delete_schedule_releases_assignments(self, admin_token):
        # Create a schedule and assign, then delete schedule -> assignment gone
        days = [{"day": i, "enabled": i < 5, "ranges": [{"start": "09:00", "end": "17:00"}] if i < 5 else []} for i in range(7)]
        r = requests.post(
            f"{BASE_URL}/api/asistencia/schedules",
            json={"name": "TEST_Schedule_Release", "type": "fijo", "days": days},
            headers=_hdr(admin_token),
        )
        sid = r.json()["id"]
        requests.post(
            f"{BASE_URL}/api/asistencia/employees/3/schedule",
            json={"schedule_id": sid},
            headers=_hdr(admin_token),
        )
        # Delete schedule
        d = requests.delete(f"{BASE_URL}/api/asistencia/schedules/{sid}", headers=_hdr(admin_token))
        assert d.status_code == 200
        # Verify employee 3 has no assignment
        g = requests.get(f"{BASE_URL}/api/asistencia/employees/3/schedule", headers=_hdr(admin_token))
        assert g.json()["assigned"] is False


# ================== ATTENDANCE / FICHAJE ==================

class TestAttendance:

    @pytest.fixture(scope="class", autouse=True)
    def setup_schedule_for_maria(self, maria_token, admin_token):
        # Create schedule and assign to maria (employee_id=1)
        days = [{"day": i, "enabled": True, "ranges": [{"start": "09:00", "end": "17:00"}]} for i in range(7)]
        r = requests.post(
            f"{BASE_URL}/api/asistencia/schedules",
            json={"name": "TEST_Maria_Schedule", "type": "fijo", "days": days},
            headers=_hdr(admin_token),
        )
        sid = r.json()["id"]
        requests.post(
            f"{BASE_URL}/api/asistencia/employees/1/schedule",
            json={"schedule_id": sid},
            headers=_hdr(admin_token),
        )
        # Ensure no active session for maria
        requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-out", headers=_hdr(maria_token))
        yield sid
        # cleanup: clock out if any, delete schedule
        requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-out", headers=_hdr(maria_token))
        requests.delete(f"{BASE_URL}/api/asistencia/schedules/{sid}", headers=_hdr(admin_token))

    def test_clock_in_without_schedule_admin(self, admin_token):
        # admin@empresa.com has no employee_id, so .get('id')='admin-1' which has no assignment
        # Ensure no assignment for "admin-1"
        requests.delete(f"{BASE_URL}/api/asistencia/employees/admin-1/schedule", headers=_hdr(admin_token))
        r = requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-in", headers=_hdr(admin_token))
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text}"
        assert "horario" in r.json().get("detail", "").lower()

    def test_get_current_no_session(self, juan_token):
        # Ensure juan has no session
        requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-out", headers=_hdr(juan_token))
        r = requests.get(f"{BASE_URL}/api/asistencia/attendance/current", headers=_hdr(juan_token))
        assert r.status_code == 200
        assert r.json()["session"] is None

    def test_full_clock_in_pause_resume_clock_out_flow(self, maria_token):
        # Clock in
        r = requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-in", headers=_hdr(maria_token))
        assert r.status_code == 200, r.text
        session = r.json()
        assert session["status"] == "active"
        assert session["clock_in"]
        assert session["clock_out"] is None

        # Wait 2s working
        time.sleep(2)

        # Pause
        r2 = requests.post(f"{BASE_URL}/api/asistencia/attendance/pause", headers=_hdr(maria_token))
        assert r2.status_code == 200
        assert r2.json()["status"] == "paused"
        assert len(r2.json()["breaks"]) == 1

        # While paused 2s
        time.sleep(2)

        # Resume
        r3 = requests.post(f"{BASE_URL}/api/asistencia/attendance/resume", headers=_hdr(maria_token))
        assert r3.status_code == 200
        assert r3.json()["status"] == "active"
        assert r3.json()["breaks"][0]["end"] is not None

        # Work 2 more seconds
        time.sleep(2)

        # Clock-out
        r4 = requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-out", headers=_hdr(maria_token))
        assert r4.status_code == 200, r4.text
        closed = r4.json()
        assert closed["status"] == "closed"
        assert closed["clock_out"]
        # duration should be roughly 4s (2 working + 2 working), excluding 2s pause; allow margin
        dur = closed["duration_seconds"]
        assert 3 <= dur <= 8, f"Expected ~4s worked excluding pause, got {dur}s"

    def test_clock_in_when_active_session(self, maria_token):
        # First ensure active
        requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-out", headers=_hdr(maria_token))
        r1 = requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-in", headers=_hdr(maria_token))
        assert r1.status_code == 200
        # Try second clock-in
        r2 = requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-in", headers=_hdr(maria_token))
        assert r2.status_code == 400
        # Cleanup
        requests.post(f"{BASE_URL}/api/asistencia/attendance/clock-out", headers=_hdr(maria_token))

    def test_records_and_summary(self, maria_token):
        # Records
        r = requests.get(f"{BASE_URL}/api/asistencia/attendance/records", headers=_hdr(maria_token))
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        # Summary for current month
        from datetime import date
        today = date.today()
        first = today.replace(day=1).isoformat()
        last = today.isoformat()
        r2 = requests.get(
            f"{BASE_URL}/api/asistencia/attendance/summary?date_from={first}&date_to={last}",
            headers=_hdr(maria_token),
        )
        assert r2.status_code == 200, r2.text
        data = r2.json()
        assert "worked_seconds" in data
        assert "planned_seconds" in data
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_employee_cannot_view_other_records(self, juan_token):
        r = requests.get(
            f"{BASE_URL}/api/asistencia/attendance/records?employee_id=1",
            headers=_hdr(juan_token),
        )
        assert r.status_code == 403


# ================== DEVICES ==================

class TestDevices:

    def test_get_devices_creates_default(self, admin_token):
        r = requests.get(f"{BASE_URL}/api/asistencia/devices", headers=_hdr(admin_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["panel_web_enabled"] is True
        assert "mobile_enabled" in data
        assert "kiosco_enabled" in data

    def test_update_devices_requires_admin(self, juan_token):
        r = requests.put(
            f"{BASE_URL}/api/asistencia/devices",
            json={"mobile_enabled": True},
            headers=_hdr(juan_token),
        )
        assert r.status_code in (401, 403)

    def test_update_devices(self, admin_token):
        r = requests.put(
            f"{BASE_URL}/api/asistencia/devices",
            json={"mobile_enabled": True, "kiosco_enabled": True},
            headers=_hdr(admin_token),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["mobile_enabled"] is True
        assert data["kiosco_enabled"] is True

        # Reset
        requests.put(
            f"{BASE_URL}/api/asistencia/devices",
            json={"mobile_enabled": False, "kiosco_enabled": False},
            headers=_hdr(admin_token),
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
