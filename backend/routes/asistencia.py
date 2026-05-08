"""
Asistencia / Time tracking endpoints:
- Schedules (jornadas laborales)
- Employee schedule assignments
- Attendance sessions (fichaje con cronómetro persistente)
- Devices config
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import uuid4
from datetime import datetime, date, timedelta, timezone

from models.asistencia import (
    Schedule, ScheduleCreate, ScheduleUpdate,
    EmployeeSchedule, EmployeeScheduleAssign,
    AttendanceSession,
    DevicesConfig, DevicesConfigUpdate,
)
from middlewares.auth import db, get_current_active_user, require_admin

router = APIRouter(prefix="/api/asistencia", tags=["asistencia"])


# ---------------- helpers ----------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_str() -> str:
    return date.today().isoformat()


def _hours_in_ranges(ranges) -> float:
    total = 0.0
    for r in ranges or []:
        try:
            sh, sm = map(int, r["start"].split(":"))
            eh, em = map(int, r["end"].split(":"))
            mins = (eh * 60 + em) - (sh * 60 + sm)
            if mins > 0:
                total += mins / 60.0
        except Exception:
            continue
    return total


def _compute_summary(days):
    """Recalcula weekly_hours, weekly_days, breaks_count a partir de days."""
    weekly_hours = 0.0
    weekly_days = 0
    breaks_count = 0
    for d in days:
        if d.get("enabled") and d.get("ranges"):
            weekly_days += 1
            weekly_hours += _hours_in_ranges(d["ranges"])
            if len(d["ranges"]) > 1:
                breaks_count += len(d["ranges"]) - 1
    return weekly_hours, weekly_days, breaks_count


def _parse_dt(s: str) -> datetime:
    """Parse ISO string -> aware datetime (UTC fallback)."""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _seconds_worked(session: dict, until: datetime = None) -> int:
    """Calcula segundos trabajados (excluyendo pausas abiertas/cerradas)."""
    ci = _parse_dt(session.get("clock_in"))
    if not ci:
        return 0
    end_dt = _parse_dt(session.get("clock_out")) or until or datetime.now(timezone.utc)
    total = (end_dt - ci).total_seconds()
    for br in session.get("breaks", []) or []:
        bs = _parse_dt(br.get("start"))
        be = _parse_dt(br.get("end")) or end_dt
        if bs and be and be > bs:
            total -= (be - bs).total_seconds()
    return max(0, int(total))


def _planned_seconds_for_day(schedule: dict, weekday: int) -> int:
    """weekday: 0..6 (Lunes=0)."""
    if not schedule:
        return 0
    for d in schedule.get("days", []):
        if d.get("day") == weekday and d.get("enabled"):
            return int(_hours_in_ranges(d.get("ranges", [])) * 3600)
    return 0


# ============================================================
#                    SCHEDULES (jornadas)
# ============================================================

@router.get("/schedules", response_model=List[Schedule])
async def list_schedules(current_user: dict = Depends(get_current_active_user)):
    items = await db.schedules.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return items


@router.get("/schedules/{schedule_id}", response_model=Schedule)
async def get_schedule(schedule_id: str, current_user: dict = Depends(get_current_active_user)):
    item = await db.schedules.find_one({"id": schedule_id}, {"_id": 0})
    if not item:
        raise HTTPException(404, "Schedule not found")
    return item


@router.post("/schedules", response_model=Schedule)
async def create_schedule(
    data: ScheduleCreate,
    current_user: dict = Depends(require_admin),
):
    days_dicts = [d.dict() for d in data.days]
    weekly_hours, weekly_days, breaks_count = _compute_summary(days_dicts)
    new_doc = {
        "id": str(uuid4()),
        "name": data.name,
        "type": data.type,
        "days": days_dicts,
        "weekly_hours": round(weekly_hours, 2),
        "weekly_days": weekly_days,
        "breaks_count": breaks_count,
        "template_kind": data.template_kind,
        "created_at": _now_iso(),
        "created_by": current_user.get("email"),
    }
    await db.schedules.insert_one(dict(new_doc))
    new_doc.pop("_id", None)
    return new_doc


@router.put("/schedules/{schedule_id}", response_model=Schedule)
async def update_schedule(
    schedule_id: str,
    data: ScheduleUpdate,
    current_user: dict = Depends(require_admin),
):
    existing = await db.schedules.find_one({"id": schedule_id}, {"_id": 0})
    if not existing:
        raise HTTPException(404, "Schedule not found")

    update = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    if "days" in update:
        update["days"] = [d if isinstance(d, dict) else d.dict() for d in update["days"]]
        wh, wd, br = _compute_summary(update["days"])
        update["weekly_hours"] = round(wh, 2)
        update["weekly_days"] = wd
        update["breaks_count"] = br

    await db.schedules.update_one({"id": schedule_id}, {"$set": update})
    updated = await db.schedules.find_one({"id": schedule_id}, {"_id": 0})
    return updated


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str, current_user: dict = Depends(require_admin)):
    res = await db.schedules.delete_one({"id": schedule_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Schedule not found")
    # Liberar empleados asignados a ese horario
    await db.employee_schedules.delete_many({"schedule_id": schedule_id})
    return {"deleted": True}


# ============================================================
#               EMPLOYEE SCHEDULE ASSIGNMENTS
# ============================================================

@router.get("/employees/{employee_id}/schedule")
async def get_employee_schedule(
    employee_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    """Retorna asignación actual del empleado + el horario completo."""
    assign = await db.employee_schedules.find_one(
        {"employee_id": employee_id}, {"_id": 0}
    )
    if not assign:
        return {"assigned": False, "schedule": None, "assignment": None}
    schedule = await db.schedules.find_one({"id": assign["schedule_id"]}, {"_id": 0})
    return {"assigned": True, "schedule": schedule, "assignment": assign}


@router.post("/employees/{employee_id}/schedule")
async def assign_schedule(
    employee_id: str,
    data: EmployeeScheduleAssign,
    current_user: dict = Depends(require_admin),
):
    schedule = await db.schedules.find_one({"id": data.schedule_id}, {"_id": 0})
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(404, "Employee not found")

    doc = {
        "id": str(uuid4()),
        "employee_id": employee_id,
        "schedule_id": data.schedule_id,
        "schedule_name": schedule["name"],
        "assigned_from": data.assigned_from or _today_str(),
        "assigned_at": _now_iso(),
    }
    # Reemplaza asignación previa (1 horario activo a la vez)
    await db.employee_schedules.delete_many({"employee_id": employee_id})
    await db.employee_schedules.insert_one(dict(doc))
    doc.pop("_id", None)
    return {"assigned": True, "assignment": doc, "schedule": schedule}


@router.delete("/employees/{employee_id}/schedule")
async def remove_employee_schedule(
    employee_id: str,
    current_user: dict = Depends(require_admin),
):
    await db.employee_schedules.delete_many({"employee_id": employee_id})
    return {"removed": True}


# ============================================================
#                ATTENDANCE / FICHAJE
# ============================================================

async def _get_user_employee_id(user: dict) -> str:
    """Resuelve el employee_id del usuario actual."""
    return user.get("employee_id") or user.get("id")


async def _get_active_session(employee_id: str):
    return await db.attendance_sessions.find_one(
        {"employee_id": employee_id, "status": {"$ne": "closed"}}, {"_id": 0}
    )


@router.get("/attendance/current")
async def get_current_session(current_user: dict = Depends(get_current_active_user)):
    """Sesión activa del usuario logueado (si la hay) + horario asignado."""
    eid = await _get_user_employee_id(current_user)
    session = await _get_active_session(eid)
    assignment = await db.employee_schedules.find_one({"employee_id": eid}, {"_id": 0})
    schedule = None
    if assignment:
        schedule = await db.schedules.find_one({"id": assignment["schedule_id"]}, {"_id": 0})

    today = date.today()
    weekday = today.weekday()
    planned = _planned_seconds_for_day(schedule, weekday) if schedule else 0

    if session:
        session["seconds_elapsed"] = _seconds_worked(session)
        session["planned_seconds"] = planned

    return {
        "session": session,
        "schedule": schedule,
        "assigned": bool(assignment),
        "planned_seconds_today": planned,
        "server_time": _now_iso(),
    }


@router.post("/attendance/clock-in")
async def clock_in(current_user: dict = Depends(get_current_active_user)):
    eid = await _get_user_employee_id(current_user)

    # Requiere horario asignado
    assignment = await db.employee_schedules.find_one({"employee_id": eid}, {"_id": 0})
    if not assignment:
        raise HTTPException(400, "No tienes un horario asignado. Contacta al administrador.")

    # Si ya hay sesión activa, no permitir otra
    active = await _get_active_session(eid)
    if active:
        raise HTTPException(400, "Ya tienes una sesión de fichaje activa.")

    schedule = await db.schedules.find_one({"id": assignment["schedule_id"]}, {"_id": 0})
    today = date.today()
    weekday = today.weekday()
    planned = _planned_seconds_for_day(schedule, weekday) if schedule else 0

    doc = {
        "id": str(uuid4()),
        "employee_id": eid,
        "employee_name": current_user.get("name"),
        "date": _today_str(),
        "clock_in": _now_iso(),
        "clock_out": None,
        "duration_seconds": 0,
        "breaks": [],
        "status": "active",
        "device": "panel_web",
        "schedule_id": assignment["schedule_id"],
        "schedule_name": schedule["name"] if schedule else None,
        "planned_seconds": planned,
    }
    await db.attendance_sessions.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@router.post("/attendance/pause")
async def pause(current_user: dict = Depends(get_current_active_user)):
    eid = await _get_user_employee_id(current_user)
    session = await _get_active_session(eid)
    if not session:
        raise HTTPException(400, "No hay sesión activa.")
    if session["status"] == "paused":
        raise HTTPException(400, "Ya está en pausa.")

    breaks = session.get("breaks", [])
    breaks.append({"start": _now_iso(), "end": None})
    await db.attendance_sessions.update_one(
        {"id": session["id"]},
        {"$set": {"status": "paused", "breaks": breaks}},
    )
    return await db.attendance_sessions.find_one({"id": session["id"]}, {"_id": 0})


@router.post("/attendance/resume")
async def resume(current_user: dict = Depends(get_current_active_user)):
    eid = await _get_user_employee_id(current_user)
    session = await _get_active_session(eid)
    if not session:
        raise HTTPException(400, "No hay sesión activa.")
    if session["status"] != "paused":
        raise HTTPException(400, "La sesión no está en pausa.")

    breaks = session.get("breaks", [])
    if breaks and not breaks[-1].get("end"):
        breaks[-1]["end"] = _now_iso()
    await db.attendance_sessions.update_one(
        {"id": session["id"]},
        {"$set": {"status": "active", "breaks": breaks}},
    )
    return await db.attendance_sessions.find_one({"id": session["id"]}, {"_id": 0})


@router.post("/attendance/clock-out")
async def clock_out(current_user: dict = Depends(get_current_active_user)):
    eid = await _get_user_employee_id(current_user)
    session = await _get_active_session(eid)
    if not session:
        raise HTTPException(400, "No hay sesión activa.")

    # Cerrar pausa abierta si existe
    breaks = session.get("breaks", [])
    if breaks and not breaks[-1].get("end"):
        breaks[-1]["end"] = _now_iso()

    now_iso = _now_iso()
    duration = _seconds_worked({**session, "breaks": breaks, "clock_out": now_iso})

    await db.attendance_sessions.update_one(
        {"id": session["id"]},
        {"$set": {
            "status": "closed",
            "clock_out": now_iso,
            "breaks": breaks,
            "duration_seconds": duration,
        }},
    )
    return await db.attendance_sessions.find_one({"id": session["id"]}, {"_id": 0})


@router.get("/attendance/records")
async def get_records(
    employee_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: dict = Depends(get_current_active_user),
):
    """Lista de sesiones (fichajes) en rango de fechas. Si no se pasa employee_id,
    usa el del usuario actual."""
    eid = employee_id or await _get_user_employee_id(current_user)
    # Solo admin puede ver registros de otros
    if eid != await _get_user_employee_id(current_user) and current_user.get("role") != "admin":
        raise HTTPException(403, "Sin permisos para ver registros de otros.")

    q = {"employee_id": eid}
    if date_from or date_to:
        q["date"] = {}
        if date_from:
            q["date"]["$gte"] = date_from
        if date_to:
            q["date"]["$lte"] = date_to

    items = await db.attendance_sessions.find(q, {"_id": 0}).sort("clock_in", 1).to_list(2000)
    # Para sesiones aún abiertas, calcula seconds_elapsed actuales
    for s in items:
        if s.get("status") != "closed":
            s["seconds_elapsed"] = _seconds_worked(s)
    return items


@router.get("/attendance/summary")
async def attendance_summary(
    employee_id: Optional[str] = Query(None),
    date_from: str = Query(..., description="YYYY-MM-DD"),
    date_to: str = Query(..., description="YYYY-MM-DD"),
    current_user: dict = Depends(get_current_active_user),
):
    """Resumen tiempo trabajado vs teórico para un periodo."""
    eid = employee_id or await _get_user_employee_id(current_user)
    if eid != await _get_user_employee_id(current_user) and current_user.get("role") != "admin":
        raise HTTPException(403, "Sin permisos.")

    sessions = await db.attendance_sessions.find(
        {"employee_id": eid, "date": {"$gte": date_from, "$lte": date_to}},
        {"_id": 0},
    ).to_list(2000)

    worked_seconds = 0
    for s in sessions:
        if s.get("status") == "closed":
            worked_seconds += s.get("duration_seconds", 0)
        else:
            worked_seconds += _seconds_worked(s)

    # Tiempo teórico desde el horario asignado
    assignment = await db.employee_schedules.find_one({"employee_id": eid}, {"_id": 0})
    schedule = None
    if assignment:
        schedule = await db.schedules.find_one({"id": assignment["schedule_id"]}, {"_id": 0})

    planned_seconds = 0
    try:
        d_from = date.fromisoformat(date_from)
        d_to = date.fromisoformat(date_to)
        cur = d_from
        while cur <= d_to:
            planned_seconds += _planned_seconds_for_day(schedule, cur.weekday())
            cur += timedelta(days=1)
    except Exception:
        pass

    return {
        "worked_seconds": worked_seconds,
        "planned_seconds": planned_seconds,
        "sessions": sessions,
    }


# ============================================================
#                       DEVICES
# ============================================================

DEVICES_DOC_ID = "devices_singleton"


@router.get("/devices", response_model=DevicesConfig)
async def get_devices(current_user: dict = Depends(get_current_active_user)):
    doc = await db.devices_config.find_one({"id": DEVICES_DOC_ID}, {"_id": 0})
    if not doc:
        default = {"id": DEVICES_DOC_ID, "panel_web_enabled": True,
                   "mobile_enabled": False, "kiosco_enabled": False, "biometric_enabled": False}
        await db.devices_config.insert_one(dict(default))
        doc = {k: v for k, v in default.items() if k != "id"}
        return DevicesConfig(**doc)
    doc.pop("id", None)
    return DevicesConfig(**doc)


@router.put("/devices", response_model=DevicesConfig)
async def update_devices(
    data: DevicesConfigUpdate,
    current_user: dict = Depends(require_admin),
):
    update = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    if not update:
        raise HTTPException(400, "Nothing to update.")
    await db.devices_config.update_one(
        {"id": DEVICES_DOC_ID},
        {"$set": update, "$setOnInsert": {"id": DEVICES_DOC_ID}},
        upsert=True,
    )
    doc = await db.devices_config.find_one({"id": DEVICES_DOC_ID}, {"_id": 0})
    doc.pop("id", None)
    return DevicesConfig(**doc)
