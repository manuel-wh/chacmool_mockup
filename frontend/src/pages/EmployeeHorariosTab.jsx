import { useState, useEffect, useCallback, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, X, Check } from 'lucide-react';
import { asistenciaAPI } from '../services/api';
import { DAY_LABELS, MONTH_LABELS, toISODate, secondsToHM, addDays, startOfWeek, hhmmToMinutes } from '../utils/asistencia';

/**
 * Tab "Horarios" del perfil del empleado.
 * - Muestra calendario mensual con su horario asignado pintado por día
 * - Resumen mes / semana (tiempo trabajado vs teórico)
 * - Botón "Asignar horario" (solo admin)
 */
const EmployeeHorariosTab = ({ employeeId, isAdmin }) => {
  const [data, setData] = useState({ assigned: false, schedule: null, assignment: null, assignments: [], vacations: [] });
  const [anchor, setAnchor] = useState(new Date());
  const [summaryMonth, setSummaryMonth] = useState({ worked_seconds: 0, planned_seconds: 0 });
  const [summaryWeek, setSummaryWeek] = useState({ worked_seconds: 0, planned_seconds: 0 });
  const [loading, setLoading] = useState(true);
  const [showAssign, setShowAssign] = useState(false);

  const [editingAssignment, setEditingAssignment] = useState(null);
  const [showVacationModal, setShowVacationModal] = useState(false);
  const monthRange = useMemo(() => ({
    from: new Date(anchor.getFullYear(), anchor.getMonth(), 1),
    to: new Date(anchor.getFullYear(), anchor.getMonth() + 1, 0),
  }), [anchor]);

  const weekRange = useMemo(() => {
    const f = startOfWeek(new Date());
    return { from: f, to: addDays(f, 6) };
  }, []);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const sched = await asistenciaAPI.getEmployeeSchedule(employeeId);
      setData(sched);
      const sm = await asistenciaAPI.summary({
        employeeId,
        dateFrom: toISODate(monthRange.from),
        dateTo: toISODate(monthRange.to),
      });
      setSummaryMonth({ worked_seconds: sm.worked_seconds, planned_seconds: sm.planned_seconds });
      const sw = await asistenciaAPI.summary({
        employeeId,
        dateFrom: toISODate(weekRange.from),
        dateTo: toISODate(weekRange.to),
      });
      setSummaryWeek({ worked_seconds: sw.worked_seconds, planned_seconds: sw.planned_seconds });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [employeeId, monthRange.from, monthRange.to, weekRange.from, weekRange.to]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const navMonth = (delta) => setAnchor((d) => new Date(d.getFullYear(), d.getMonth() + delta, 1));

  if (loading) return <div className="py-8 text-center text-slate-400">Cargando…</div>;

  const schedule = data.schedule;
  const assignments = data.assignments || [];
  const vacations = data.vacations || [];

  return (
    <div className="space-y-6" data-testid="employee-horarios-tab">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3 border border-slate-200 rounded-full px-3 py-2 bg-white">
          <button onClick={() => navMonth(-1)} className="text-slate-500 hover:text-slate-900" data-testid="month-prev">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-sm font-medium text-slate-900 min-w-[100px] text-center">
            {MONTH_LABELS[anchor.getMonth()]} {anchor.getFullYear()}
          </span>
          <button onClick={() => navMonth(1)} className="text-slate-500 hover:text-slate-900" data-testid="month-next">
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {isAdmin && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowVacationModal(true)}
              className="px-4 py-2.5 text-sm font-medium rounded-xl border border-slate-200 hover:bg-slate-50"
              data-testid="add-vacation-btn"
            >
              Plan de vacaciones
            </button>
            <button
              onClick={() => setShowAssign(true)}
              className="bg-slate-900 text-white rounded-xl px-4 py-2.5 text-sm font-medium hover:bg-slate-800 inline-flex items-center gap-2"
              data-testid="assign-schedule-btn"
            >
              Agregar asignación
            </button>
          </div>
        )}
      </div>

      {/* Resumen */}
      <div className="grid md:grid-cols-2 gap-4">
        <SummaryCard title={`Mes: ${MONTH_LABELS[anchor.getMonth()]}`} {...summaryMonth} testId="summary-month" />
        <SummaryCard title="Semana actual" {...summaryWeek} testId="summary-week" />
      </div>

      {/* Estado de asignaciones */}
      {assignments.length === 0 ? (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 text-amber-900">
          <p className="font-medium">El empleado no tiene horarios asignados.</p>
          <p className="text-sm text-amber-800 mt-1">
            {isAdmin
              ? 'Asigna al menos un horario con rango de fechas para habilitar el registro de asistencia.'
              : 'Contacta al administrador para asignar tus horarios.'}
          </p>
        </div>
      ) : (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-sm text-emerald-900 inline-flex items-center gap-2">
          <Check className="w-4 h-4" /> Asignaciones activas en historial: <strong>{assignments.length}</strong>
        </div>
      )}

      <AssignmentsList
        assignments={assignments}
        vacations={vacations}
        isAdmin={isAdmin}
        employeeId={employeeId}
        onChanged={fetchAll}
        onEdit={(a) => setEditingAssignment(a)}
      />

      {/* Calendario mensual */}
      <CalendarMonth anchor={anchor} assignments={assignments} vacations={vacations} />

      {showAssign && (
        <AssignModal
          employeeId={employeeId}
          onClose={() => setShowAssign(false)}
          onSaved={() => { setShowAssign(false); fetchAll(); }}
        />
      )}

      {editingAssignment && (
        <EditAssignmentModal
          employeeId={employeeId}
          assignment={editingAssignment}
          onClose={() => setEditingAssignment(null)}
          onSaved={() => { setEditingAssignment(null); fetchAll(); }}
        />
      )}

      {showVacationModal && (
        <VacationModal
          employeeId={employeeId}
          onClose={() => setShowVacationModal(false)}
          onSaved={() => { setShowVacationModal(false); fetchAll(); }}
        />
      )}
    </div>
  );
};

const SummaryCard = ({ title, worked_seconds, planned_seconds, testId }) => {
  const progress = planned_seconds > 0 ? Math.min(100, (worked_seconds / planned_seconds) * 100) : 0;
  return (
    <div className="border border-slate-200 rounded-2xl p-5 bg-white" data-testid={testId}>
      <div className="flex items-center gap-2 text-slate-700 text-sm mb-2">
        <CalendarIcon className="w-4 h-4" />
        <span className="font-semibold">{title}</span>
      </div>
      <p className="text-xs text-slate-500 mb-1">Tiempo trabajado vs teórico</p>
      <p className="text-lg font-bold text-slate-900">
        {secondsToHM(worked_seconds)} <span className="text-slate-400 font-normal">/ {secondsToHM(planned_seconds)} teóricas</span>
      </p>
      <div className="h-2 bg-slate-100 rounded-full mt-3 overflow-hidden">
        <div className="h-full bg-emerald-500" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
};

const AssignmentsList = ({ assignments, vacations, isAdmin, employeeId, onChanged, onEdit }) => {
  const removeOne = async (assignmentId) => {
    try {
      await asistenciaAPI.removeEmployeeSchedule(employeeId, assignmentId);
      onChanged();
    } catch (e) {
      alert(e.message);
    }
  };

  if (!assignments || assignments.length === 0) return null;

  return (
    <div className="border border-slate-200 rounded-2xl bg-white p-4" data-testid="assignments-list">
      <h4 className="font-semibold text-slate-900 mb-3" style={{ fontFamily: 'Outfit' }}>Asignaciones de horario</h4>
      <div className="space-y-2">
        {assignments
          .slice()
          .sort((a, b) => String(a.assigned_from).localeCompare(String(b.assigned_from)))
          .map((a) => (
            <div key={a.id} className="border border-slate-100 rounded-xl p-3 flex items-center justify-between gap-3">
              <div>
                <div className="text-sm font-medium text-slate-900">{a.schedule_name}</div>
                <div className="text-xs text-slate-500 flex items-center gap-2">
                  <span>{a.assigned_from} → {a.no_end ? 'Sin fin' : (a.assigned_to || 'Sin fin')}</span>
                  {a.alternate_monthly && (
                    <span className="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">Mes sí / mes no</span>
                  )}
                </div>
              </div>
              {isAdmin && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onEdit(a)}
                    className="text-xs px-2 py-1 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50"
                    data-testid={`edit-assignment-${a.id}`}
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => removeOne(a.id)}
                    className="text-xs px-2 py-1 rounded-lg border border-red-200 text-red-700 hover:bg-red-50"
                    data-testid={`remove-assignment-${a.id}`}
                  >
                    Eliminar
                  </button>
                </div>
              )}
            </div>
          ))}
      </div>

      <div className="mt-4">
        <h5 className="text-sm font-semibold text-slate-800 mb-2">Vacaciones</h5>
        {(!vacations || vacations.length === 0) ? (
          <div className="text-xs text-slate-500">Sin planes de vacaciones.</div>
        ) : (
          <div className="space-y-2">
            {vacations.map((v) => (
              <div key={v.id} className="border border-rose-200 bg-rose-50 rounded-xl p-3 flex items-center justify-between">
                <div className="text-sm text-rose-800 font-medium">Vacaciones: {v.start_date} → {v.end_date}</div>
                {isAdmin && (
                  <button
                    onClick={async () => {
                      try {
                        await asistenciaAPI.deleteEmployeeVacation(employeeId, v.id);
                        onChanged();
                      } catch (e) {
                        alert(e.message);
                      }
                    }}
                    className="text-xs px-2 py-1 rounded-lg border border-rose-200 text-rose-700 hover:bg-rose-100"
                    data-testid={`remove-vacation-${v.id}`}
                  >
                    Eliminar
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const CalendarMonth = ({ anchor, assignments, vacations }) => {
  const year = anchor.getFullYear();
  const month = anchor.getMonth();
  const firstDay = new Date(year, month, 1);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const totalDays = new Date(year, month + 1, 0).getDate();

  const cells = [];
  for (let i = 0; i < startOffset; i++) {
    const d = new Date(year, month, -startOffset + i + 1);
    cells.push({ date: d, outside: true });
  }
  for (let d = 1; d <= totalDays; d++) cells.push({ date: new Date(year, month, d), outside: false });
  while (cells.length % 7 !== 0) {
    const last = cells[cells.length - 1].date;
    cells.push({ date: new Date(last.getFullYear(), last.getMonth(), last.getDate() + 1), outside: true });
  }

  const today = toISODate(new Date());

  const assignmentForDate = (d) => {
    const iso = toISODate(d);
    const found = (assignments || []).filter((a) => {
      const from = a.assigned_from;
      const to = a.no_end ? null : a.assigned_to;
      if (!from) return false;
      if (iso < from) return false;
      if (to && iso > to) return false;

      if (a.alternate_monthly) {
        const start = new Date(`${from}T00:00:00`);
        const monthsDiff = ((d.getFullYear() - start.getFullYear()) * 12) + (d.getMonth() - start.getMonth());
        if (monthsDiff % 2 !== 0) return false;
      }
      return true;
    });
    if (found.length === 0) return null;
    found.sort((a, b) => String(b.assigned_from).localeCompare(String(a.assigned_from)));
    return found[0];
  };

  const vacationForDate = (d) => {
    const iso = toISODate(d);
    return (vacations || []).find((v) => iso >= v.start_date && iso <= v.end_date) || null;
  };

  const dayInfo = (d) => {
    const vacation = vacationForDate(d);
    if (vacation) {
      return { isVacation: true, label: 'Vacaciones', range: `${vacation.start_date} → ${vacation.end_date}` };
    }

    const assign = assignmentForDate(d);
    const schedule = assign?.schedule;
    if (!schedule) return null;
    const wd = (d.getDay() + 6) % 7;
    const dayCfg = schedule.days?.find((x) => x.day === wd);
    if (!dayCfg || !dayCfg.enabled) return null;
    const ranges = dayCfg.ranges || [];
    if (ranges.length === 0) return null;
    const first = ranges[0].start;
    const last = ranges[ranges.length - 1].end;
    return { label: schedule.name, range: `${first} - ${last}` };
  };

  return (
    <div data-testid="calendar-month">
      <div className="grid grid-cols-7 gap-px text-xs text-slate-500 mb-2 px-2">
        {DAY_LABELS.map((l) => <div key={l} className="py-1">{l}</div>)}
      </div>
      <div className="grid grid-cols-7 gap-px bg-slate-200 rounded-xl overflow-hidden">
        {cells.map(({ date: d, outside }, i) => {
          const iso = toISODate(d);
          const info = !outside ? dayInfo(d) : null;
          const isToday = iso === today;
          return (
            <div key={i} className={`bg-white p-2 min-h-[100px] ${outside ? 'opacity-40' : ''}`}>
              <div className={`text-right text-sm ${
                isToday ? 'inline-block w-7 h-7 rounded-full bg-indigo-500 text-white text-center leading-7 font-semibold ml-auto'
                  : 'text-slate-700'
              }`}>
                {d.getDate()}
              </div>
              {info && (
                <div className={`mt-1 text-xs rounded-lg px-2 py-1 ${info.isVacation ? 'bg-rose-50 border border-rose-200' : ''}`}>
                  <div className={`font-medium truncate ${info.isVacation ? 'text-rose-700' : 'text-slate-800'}`}>{info.label}</div>
                  <div className={info.isVacation ? 'text-rose-500' : 'text-slate-500'}>{info.range}</div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

const AssignModal = ({ employeeId, onClose, onSaved }) => {
  const [list, setList] = useState([]);
  const [picked, setPicked] = useState('');
  const [assignedFrom, setAssignedFrom] = useState(toISODate(new Date()));
  const [assignedTo, setAssignedTo] = useState('');
  const [noEnd, setNoEnd] = useState(false);
  const [alternateMonthly, setAlternateMonthly] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  useEffect(() => {
    asistenciaAPI.listSchedules().then(setList).catch((e) => setErr(e.message));
  }, []);

  const save = async () => {
    if (!picked) return;
    if (!assignedFrom) {
      setErr('Selecciona una fecha de inicio.');
      return;
    }
    if (!noEnd && !assignedTo) {
      setErr('Selecciona fecha de fin o activa "Sin fecha fin".');
      return;
    }
    setBusy(true);
    try {
      await asistenciaAPI.assignSchedule(employeeId, picked, assignedFrom, noEnd ? null : assignedTo, noEnd, alternateMonthly);
      onSaved();
    } catch (e) {
      setErr(e.message === 'HTTP 400' ? 'Este horario se sobrelapa con una asignación existente o tiene fechas inválidas.' : e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="assign-modal">
      <div className="bg-white rounded-2xl w-full max-w-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>Asignar horario</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <div className="p-6 space-y-3 max-h-[60vh] overflow-y-auto">
          {err && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{err}</div>}
          {list.length === 0 && (
            <p className="text-sm text-slate-500">Aún no hay horarios creados. Ve a Asistencia → Configuración → Horarios y crea uno.</p>
          )}
          {list.map((s) => (
            <label
              key={s.id}
              className={`block border rounded-xl p-4 cursor-pointer transition ${picked === s.id ? 'border-slate-900 bg-slate-50' : 'border-slate-200 hover:border-slate-300'}`}
              data-testid={`pick-${s.id}`}
            >
              <input type="radio" className="hidden" checked={picked === s.id} onChange={() => setPicked(s.id)} />
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold text-slate-900">{s.name}</div>
                  <div className="text-xs text-slate-500 mt-1">
                    {s.weekly_hours.toFixed(1)}h semanales · {s.weekly_days} días · {s.type === 'fijo' ? 'Horario fijo' : 'Horario flexible'}
                  </div>
                </div>
                {picked === s.id && <Check className="w-4 h-4 text-emerald-600" />}
              </div>
            </label>
          ))}
          <div className="border border-slate-200 rounded-xl p-3">
            <label className="block text-xs font-medium text-slate-700 mb-1">Fecha de inicio</label>
            <input
              type="date"
              value={assignedFrom}
              onChange={(e) => setAssignedFrom(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
              data-testid="assign-from"
            />
          </div>

          <div className="border border-slate-200 rounded-xl p-3">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-slate-700">Sin fecha fin</label>
              <button
                type="button"
                onClick={() => setNoEnd((v) => !v)}
                className={`w-10 h-6 rounded-full transition ${noEnd ? 'bg-emerald-500' : 'bg-slate-200'}`}
                data-testid="assign-no-end"
              >
                <span className={`block w-4 h-4 bg-white rounded-full transform transition ${noEnd ? 'translate-x-5' : 'translate-x-1'}`} />
              </button>
            </div>
            <input
              type="date"
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
              disabled={noEnd}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm disabled:bg-slate-50"
              data-testid="assign-to"
            />
          </div>

          <div className="border border-slate-200 rounded-xl p-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-xs font-medium text-slate-700">Modo alternado</label>
                <p className="text-[11px] text-slate-500 mt-1">Aplica un mes sí y un mes no (desde el mes de inicio).</p>
              </div>
              <button
                type="button"
                onClick={() => setAlternateMonthly((v) => !v)}
                className={`w-10 h-6 rounded-full transition ${alternateMonthly ? 'bg-indigo-500' : 'bg-slate-200'}`}
                data-testid="assign-alternate-monthly"
              >
                <span className={`block w-4 h-4 bg-white rounded-full transform transition ${alternateMonthly ? 'translate-x-5' : 'translate-x-1'}`} />
              </button>
            </div>
          </div>
        </div>
        <div className="border-t border-slate-200 px-6 py-4 flex gap-2 justify-end">
          <button onClick={onClose} className="px-4 py-2 text-sm border border-slate-200 rounded-xl hover:bg-slate-50">Cancelar</button>
          <button
            onClick={save}
            disabled={!picked || busy}
            className="px-4 py-2 text-sm bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50"
            data-testid="confirm-assign"
          >
            {busy ? 'Guardando…' : 'Asignar horario'}
          </button>
        </div>
      </div>
    </div>
  );
};

const EditAssignmentModal = ({ employeeId, assignment, onClose, onSaved }) => {
  const [assignedFrom, setAssignedFrom] = useState(assignment.assigned_from || '');
  const [assignedTo, setAssignedTo] = useState(assignment.assigned_to || '');
  const [noEnd, setNoEnd] = useState(Boolean(assignment.no_end));
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const isAlternated = Boolean(assignment.alternate_monthly);

  const save = async () => {
    setBusy(true);
    setErr('');
    try {
      const payload = isAlternated
        ? { assigned_to: assignedTo }
        : { assigned_from: assignedFrom, assigned_to: noEnd ? null : assignedTo, no_end: noEnd };
      await asistenciaAPI.updateEmployeeScheduleAssignment(employeeId, assignment.id, payload);
      onSaved();
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="edit-assignment-modal">
      <div className="bg-white rounded-2xl w-full max-w-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>Editar asignación</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <div className="p-6 space-y-3">
          {err && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{err}</div>}
          <div className="text-sm text-slate-700">Horario: <strong>{assignment.schedule_name}</strong></div>

          {!isAlternated && (
            <div className="border border-slate-200 rounded-xl p-3">
              <label className="block text-xs font-medium text-slate-700 mb-1">Fecha de inicio</label>
              <input type="date" value={assignedFrom} onChange={(e) => setAssignedFrom(e.target.value)} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
            </div>
          )}

          {isAlternated ? (
            <div className="border border-indigo-200 bg-indigo-50 rounded-xl p-3 text-sm text-indigo-800">
              Asignación intermitente: solo puedes editar la fecha fin.
            </div>
          ) : (
            <div className="border border-slate-200 rounded-xl p-3">
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-medium text-slate-700">Sin fecha fin</label>
                <button type="button" onClick={() => setNoEnd((v) => !v)} className={`w-10 h-6 rounded-full transition ${noEnd ? 'bg-emerald-500' : 'bg-slate-200'}`}>
                  <span className={`block w-4 h-4 bg-white rounded-full transform transition ${noEnd ? 'translate-x-5' : 'translate-x-1'}`} />
                </button>
              </div>
              <input type="date" value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)} disabled={noEnd} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm disabled:bg-slate-50" />
            </div>
          )}

          {isAlternated && (
            <div className="border border-slate-200 rounded-xl p-3">
              <label className="block text-xs font-medium text-slate-700 mb-1">Fecha de fin</label>
              <input type="date" value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
            </div>
          )}
        </div>
        <div className="border-t border-slate-200 px-6 py-4 flex gap-2 justify-end">
          <button onClick={onClose} className="px-4 py-2 text-sm border border-slate-200 rounded-xl hover:bg-slate-50">Cancelar</button>
          <button onClick={save} disabled={busy} className="px-4 py-2 text-sm bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50">
            {busy ? 'Guardando…' : 'Guardar cambios'}
          </button>
        </div>
      </div>
    </div>
  );
};

const VacationModal = ({ employeeId, onClose, onSaved }) => {
  const [startDate, setStartDate] = useState(toISODate(new Date()));
  const [endDate, setEndDate] = useState(toISODate(new Date()));
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const save = async () => {
    setBusy(true);
    setErr('');
    try {
      await asistenciaAPI.createEmployeeVacation(employeeId, startDate, endDate);
      onSaved();
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="vacation-modal">
      <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>Plan de vacaciones</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <div className="p-6 space-y-3">
          {err && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{err}</div>}
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Fecha inicio</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Fecha fin</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="border-t border-slate-200 px-6 py-4 flex gap-2 justify-end">
          <button onClick={onClose} className="px-4 py-2 text-sm border border-slate-200 rounded-xl hover:bg-slate-50">Cancelar</button>
          <button onClick={save} disabled={busy} className="px-4 py-2 text-sm bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50">
            {busy ? 'Guardando…' : 'Guardar vacaciones'}
          </button>
        </div>
      </div>
    </div>
  );
};


export default EmployeeHorariosTab;
