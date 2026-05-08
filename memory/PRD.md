# EvalPro - Sistema de Evaluación 360°

## Problem Statement
Sistema web de evaluación de empleados (KPIs, 360°, 9-box) + módulos auxiliares de gestión RR.HH.
Stack: **React + FastAPI + MongoDB**. Frontend en español.

---

## Funcionalidades Implementadas ✅

### Core (sesiones previas)
- [x] Autenticación JWT (admin / manager / empleado)
- [x] Dashboard con estadísticas
- [x] Empleados (CRUD, perfil completo)
- [x] Matriz 9-Box con clasificaciones A/B/C basadas en valores y resultados
- [x] Evaluaciones 360° (plantillas, enlaces públicos, formularios)
- [x] PDI (Plan de Desarrollo Individual)
- [x] KPIs (indicadores)
- [x] Aciertos y Desaciertos (evaluación bilateral colaborador↔empresa)
- [x] Empleado A/B/C (diagnóstico de talento)
- [x] Perfil de empleado con tabs (Perfil, Fichajes, Ausencias, Horarios, Evaluaciones, etc.)

### Asistencia / Time Tracking (Feb 2026) ⭐ NUEVO
**Inspirado en Sesame HR — UI/UX 1:1 con capturas del cliente.**

- [x] **Cronómetro persistente con backend**
  - Botones: Iniciar jornada, Pausar, Reanudar, Finalizar jornada
  - Estado vivo (active/paused/closed) sobrevive recargas y cierres de navegador
  - Excluye correctamente tiempo en pausa del `duration_seconds`
- [x] **Vista del empleado** (`/asistencia`)
  - Cronómetro grande HH:MM:SS con barra de progreso vs horas planificadas del día
  - Card "Esta semana" con tiempo trabajado / planificadas
  - Calendario semanal y mensual de fichajes (toggle Semanal/Mensual + navegación)
- [x] **Configuración admin** (`/asistencia/configuracion`)
  - 6 tabs: Empresa, Horarios, Calendarios, Automatizaciones, Dispositivos, Plan
  - **Tab Horarios**: tabla CRUD de jornadas con resumen visual de días (LMMJVSD pills),
    tipo (fijo/flexible), descansos, horas semanales, fecha creación
  - **Modal "Crear nueva jornada"** con elección Horario fijo / Horario flexible
  - **Editor de jornada con sliders**: doble-handle range slider por día con chips horarios,
    plantillas (jornada continua / jornada partida / personalizado), múltiples rangos
    por día (descansos en medio), cálculo automático de medio día de vacaciones
  - **Tab Dispositivos**: 3 cards (Panel web activo, Celular y Kiosco como "Próximamente")
    + card "Registro Biométrico"
- [x] **Asignación de horarios**
  - Tab Horarios en perfil del empleado con calendario mensual ilustrando el horario
  - Resumen mes / semana (tiempo trabajado vs teórico)
  - Botón "Asignar horario" / "Cambiar horario" / "Quitar horario" (solo admin)
  - **Bloqueo**: si empleado no tiene horario asignado → no puede iniciar fichaje
- [x] **Backend completo** (`/api/asistencia/...`)
  - Schedules CRUD + auto-cálculo de horas/días/descansos
  - Employee schedule assignments
  - Attendance: clock-in / pause / resume / clock-out / current / records / summary
  - Devices config (singleton)
  - Tests: **24/24 pytest pasados** en `/app/backend/tests/test_asistencia.py`

---

## Endpoints Asistencia
```
GET    /api/asistencia/schedules
POST   /api/asistencia/schedules                    [admin]
GET    /api/asistencia/schedules/{id}
PUT    /api/asistencia/schedules/{id}               [admin]
DELETE /api/asistencia/schedules/{id}               [admin]

GET    /api/asistencia/employees/{employee_id}/schedule
POST   /api/asistencia/employees/{employee_id}/schedule   [admin]
DELETE /api/asistencia/employees/{employee_id}/schedule   [admin]

GET    /api/asistencia/attendance/current
POST   /api/asistencia/attendance/clock-in
POST   /api/asistencia/attendance/pause
POST   /api/asistencia/attendance/resume
POST   /api/asistencia/attendance/clock-out
GET    /api/asistencia/attendance/records?employee_id=&date_from=&date_to=
GET    /api/asistencia/attendance/summary?date_from=&date_to=

GET    /api/asistencia/devices
PUT    /api/asistencia/devices                      [admin]
```

## Modelos MongoDB
- `schedules` — plantillas de jornada (id, name, type, days[], weekly_hours, breaks_count)
- `employee_schedules` — asignación 1:1 empleado↔horario
- `attendance_sessions` — sesiones de fichaje con breaks[]
- `devices_config` — singleton con flags de dispositivos habilitados

---

## Backlog / Roadmap

### P1 (próximas iteraciones)
- [ ] Solicitud manual de fichaje (botón "Solicitar registro" cuando se olvidó marcar)
- [ ] Edición de fichajes ya cerrados (admin)
- [ ] Notificaciones cuando un empleado supera horas planificadas
- [ ] Alerta si empleado lleva más de N horas con sesión abierta sin pausa

### P2 (futuro)
- [ ] Soporte Móvil (app Sesame Mobile)
- [ ] Soporte Kiosco (tablet con QR/foto)
- [ ] Registro biométrico (huella/facial)
- [ ] Importación masiva de fichajes desde Excel
- [ ] Reportes/exportación PDF de horas trabajadas
- [ ] Multi-tenant (org_id en `devices_config`)
- [ ] Tabs Calendarios, Automatizaciones, Empresa, Plan de la config

### Refactoring
- `routes/asistencia.py` (489 líneas) → considerar split en `routes/asistencia/{schedules,attendance,devices}.py`
- `App.js` (~2150 líneas) → extraer componentes inline (AciertosDesaciertosView, etc.)

---

## Credenciales test
Ver `/app/memory/test_credentials.md`.

## Testing
- Backend: `pytest /app/backend/tests/` (24 tests asistencia + previos)
- Frontend: testing_agent_v3_fork iteración 7 ✅

---
*Última actualización: Feb 2026 — Módulo Asistencia completado*
