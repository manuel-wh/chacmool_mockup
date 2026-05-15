from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ============== HORARIOS / SCHEDULES ==============

class TimeRange(BaseModel):
    """Un rango horario dentro de un día (ej: 09:00 - 13:00)"""
    start: str  # "HH:MM" (24h)
    end: str    # "HH:MM"


class DaySchedule(BaseModel):
    """Configuración de un día específico"""
    day: int  # 0=Lunes ... 6=Domingo (ISO: 0..6)
    enabled: bool
    ranges: List[TimeRange] = []   # múltiples rangos por día (descansos en medio)


class Schedule(BaseModel):
    """Plantilla de horario / Jornada laboral"""
    id: str
    name: str
    type: Literal["fijo", "flexible"]
    days: List[DaySchedule]
    weekly_hours: float = 0
    weekly_days: int = 0
    breaks_count: int = 0
    template_kind: Literal["jornada_continua", "jornada_partida"] = "jornada_continua"
    created_at: str
    created_by: Optional[str] = None


class ScheduleCreate(BaseModel):
    name: str
    type: Literal["fijo", "flexible"] = "fijo"
    days: List[DaySchedule] = []
    template_kind: Literal["jornada_continua", "jornada_partida"] = "jornada_continua"


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal["fijo", "flexible"]] = None
    days: Optional[List[DaySchedule]] = None

class EmployeeScheduleUpdate(BaseModel):
    assigned_from: Optional[str] = None
    assigned_to: Optional[str] = None
    no_end: Optional[bool] = None


class VacationPlan(BaseModel):
    id: str
    employee_id: str
    start_date: str
    end_date: str
    created_at: str
    template_kind: Optional[Literal["jornada_continua", "jornada_partida"]] = None


# ============== ASIGNACIÓN HORARIO A EMPLEADO ==============

class VacationPlanCreate(BaseModel):
    start_date: str
    end_date: str

class EmployeeSchedule(BaseModel):
    id: str
    employee_id: str
    schedule_id: str
    schedule_name: str
    assigned_from: str  # ISO date
    assigned_to: Optional[str] = None  # ISO date
    no_end: bool = False
    alternate_monthly: bool = False
    assigned_at: str    # ISO datetime


class EmployeeScheduleAssign(BaseModel):
    schedule_id: str
    assigned_from: str
    assigned_to: Optional[str] = None
    no_end: bool = False
    alternate_monthly: bool = False


# ============== ATTENDANCE / FICHAJE ==============

class AttendanceBreak(BaseModel):
    start: str  # ISO datetime
    end: Optional[str] = None


class AttendanceSession(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    date: str           # YYYY-MM-DD (en TZ del servidor)
    clock_in: str       # ISO datetime
    clock_out: Optional[str] = None
    duration_seconds: int = 0
    breaks: List[AttendanceBreak] = []
    status: Literal["active", "paused", "closed"] = "active"
    device: Literal["panel_web", "mobile", "kiosco"] = "panel_web"
    schedule_id: Optional[str] = None
    schedule_name: Optional[str] = None
    planned_seconds: int = 0


# ============== DEVICES ==============

class DevicesConfig(BaseModel):
    panel_web_enabled: bool = True
    mobile_enabled: bool = False
    kiosco_enabled: bool = False
    biometric_enabled: bool = False


class DevicesConfigUpdate(BaseModel):
    panel_web_enabled: Optional[bool] = None
    mobile_enabled: Optional[bool] = None
    kiosco_enabled: Optional[bool] = None
    biometric_enabled: Optional[bool] = None



# ============== KIOSCO / ACCESS CREDENTIALS ==============

class KioskAccessCredential(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    access_code: str
    pin: str
    updated_at: str
    updated_by: Optional[str] = None


class KioskAccessCreateRequest(BaseModel):
    access_code: Optional[str] = None


class KioskAccessUpdateRequest(BaseModel):
    access_code: str = Field(..., min_length=4, max_length=12)
    pin: Optional[str] = Field(default=None, min_length=4, max_length=8)


class KioskPunchRequest(BaseModel):
    access_code: str = Field(..., min_length=4, max_length=12)
    pin: str = Field(..., min_length=4, max_length=8)


class KioskPunchResponse(BaseModel):
    action: Literal["clock_in", "clock_out"]
    message: str
    employee: dict
    session: dict


class KioskPublicConfig(BaseModel):
    kiosco_enabled: bool = False