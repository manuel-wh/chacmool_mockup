import { useState, useEffect, useCallback, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, X, Check, KeyRound, RefreshCcw } from 'lucide-react';
import { asistenciaAPI } from '../services/api';
import { DAY_LABELS, MONTH_LABELS, toISODate, secondsToHM, addDays, startOfWeek, hhmmToMinutes } from '../utils/asistencia';

/**
 * Tab "Horarios" del perfil del empleado.
 * - Muestra calendario mensual con su horario asignado pintado por día
 * - Resumen mes / semana (tiempo trabajado vs teórico)
 * - Botón "Asignar horario" (solo admin)
 */
const EmployeeHorariosTab = ({ employeeId, isAdmin }) => {
  const [data, setData] = useState({ assigned: false, schedule: null, assignment: null });
  const [anchor, setAnchor] = useState(new Date());
  const [summaryMonth, setSummaryMonth] = useState({ worked_seconds: 0, planned_seconds: 0 });
  const [summaryWeek, setSummaryWeek] = useState({ worked_seconds: 0, planned_seconds: 0 });
  const [loading, setLoading] = useState(true);
  const [showAssign, setShowAssign] = useState(false);
  const [kioskAccess, setKioskAccess] = useState(null);
  const [kioskCode, setKioskCode] = useState('');
  const [kioskBusy, setKioskBusy] = useState(false);
  const [kioskError, setKioskError] = useState('');

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

      if (isAdmin) {
        const ka = await asistenciaAPI.getEmployeeKioskAccess(employeeId);
        setKioskAccess(ka || null);
        setKioskCode(ka?.access_code || '');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [employeeId, monthRange.from, monthRange.to, weekRange.from, weekRange.to, isAdmin]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const generateKioskAccess = async () => {
    setKioskBusy(true);
    setKioskError('');
    try {
      const dataResp = await asistenciaAPI.generateEmployeeKioskAccess(employeeId, kioskCode || null);
      setKioskAccess(dataResp);
      setKioskCode(dataResp.access_code || '');
    } catch (e) {
      setKioskError(e.message);
    } finally {
      setKioskBusy(false);
    }
  };

  const saveKioskCode = async () => {
    if (!kioskCode?.trim()) {
      setKioskError('Ingresa un código de acceso válido.');
      return;
    }
    setKioskBusy(true);
    setKioskError('');
    try {
      const dataResp = await asistenciaAPI.updateEmployeeKioskAccess(employeeId, kioskCode.trim());
      setKioskAccess(dataResp);
      setKioskCode(dataResp.access_code || kioskCode.trim().toUpperCase());
    } catch (e) {
      setKioskError(e.message);
    } finally {
      setKioskBusy(false);
    }
  };

  const regeneratePin = async () => {
    setKioskBusy(true);
    setKioskError('');
    try {
      const dataResp = await asistenciaAPI.regenerateEmployeeKioskPin(employeeId);
      setKioskAccess(dataResp);
      setKioskCode(dataResp.access_code || kioskCode);
    } catch (e) {
      setKioskError(e.message);
    } finally {
      setKioskBusy(false);
    }
  };

  const navMonth = (delta) => setAnchor((d) => new Date(d.getFullYear(), d.getMonth() + delta, 1));

  if (loading) return <div className="py-8 text-center text-slate-400">Cargando…</div>;

  const schedule = data.schedule;

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
          <button
            onClick={() => setShowAssign(true)}
            className="bg-slate-900 text-white rounded-xl px-4 py-2.5 text-sm font-medium hover:bg-slate-800 inline-flex items-center gap-2"
            data-testid="assign-schedule-btn"
          >
            {schedule ? 'Cambiar horario' : 'Asignar horario'}
          </button>
        )}
      </div>

      {/* Resumen */}
      <div className="grid md:grid-cols-2 gap-4">
        <SummaryCard title={`Mes: ${MONTH_LABELS[anchor.getMonth()]}`} {...summaryMonth} testId="summary-month" />
        <SummaryCard title="Semana actual" {...summaryWeek} testId="summary-week" />
      </div>

      {/* Estado horario */}
      {!schedule ? (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 text-amber-900">
          <p className="font-medium">El empleado no tiene horario asignado.</p>
          <p className="text-sm text-amber-800 mt-1">
            {isAdmin
              ? 'Asigna un horario para habilitar el registro de asistencia.'
              : 'Contacta al administrador para asignar tu horario.'}
          </p>
        </div>
      ) : (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-sm text-emerald-900 inline-flex items-center gap-2">
          <Check className="w-4 h-4" /> Horario asignado: <strong>{schedule.name}</strong>
        </div>
      )}

      {isAdmin && (
        <div className="border border-indigo-200 bg-indigo-50 rounded-2xl p-5" data-testid="employee-kiosk-access-card">
          <div className="flex items-center gap-2 mb-3">
            <KeyRound className="w-4 h-4 text-indigo-700" />
            <h3 className="font-semibold text-indigo-900" style={{ fontFamily: 'Outfit' }}>Acceso de Kiosco</h3>
          </div>
          <p className="text-sm text-indigo-800 mb-4">
            Configura código de acceso (editable) y PIN para que este empleado fiche en la vista de kiosco.
          </p>

          {kioskError && (
            <div className="mb-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {kioskError}
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-xs font-medium text-indigo-800 mb-1">Código de acceso</label>
              <input
                value={kioskCode}
                onChange={(e) => setKioskCode(e.target.value.toUpperCase())}
                className="w-full border border-indigo-200 bg-white rounded-lg px-3 py-2 text-sm"
                placeholder="Ej: EMP10234"
                data-testid="kiosk-access-code"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-indigo-800 mb-1">PIN actual</label>
              <input
                value={kioskAccess?.pin || '----'}
                readOnly
                className="w-full border border-indigo-200 bg-white rounded-lg px-3 py-2 text-sm tracking-[0.25em] font-semibold"
                data-testid="kiosk-access-pin"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={generateKioskAccess}
              disabled={kioskBusy}
              className="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm hover:bg-indigo-700 disabled:opacity-60"
              data-testid="kiosk-generate-btn"
            >
              {kioskAccess ? 'Regenerar credenciales' : 'Generar código + PIN'}
            </button>
            <button
              onClick={saveKioskCode}
              disabled={kioskBusy || !kioskAccess}
              className="px-3 py-2 rounded-lg border border-indigo-200 bg-white text-indigo-800 text-sm hover:bg-indigo-100 disabled:opacity-60"
              data-testid="kiosk-save-code-btn"
            >
              Guardar código
            </button>
            <button
              onClick={regeneratePin}
              disabled={kioskBusy || !kioskAccess}
              className="inline-flex items-center gap-1 px-3 py-2 rounded-lg border border-indigo-200 bg-white text-indigo-800 text-sm hover:bg-indigo-100 disabled:opacity-60"
              data-testid="kiosk-regenerate-pin-btn"
            >
              <RefreshCcw className="w-3.5 h-3.5" /> Regenerar PIN
            </button>
          </div>
        </div>
      )}

      {/* Calendario mensual */}
      <CalendarMonth anchor={anchor} schedule={schedule} />

      {showAssign && (
        <AssignModal
          employeeId={employeeId}
          current={schedule?.id}
          onClose={() => setShowAssign(false)}
          onSaved={() => { setShowAssign(false); fetchAll(); }}
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

const CalendarMonth = ({ anchor, schedule }) => {
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

  const dayInfo = (d) => {
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
                <div className="mt-1 text-xs">
                  <div className="font-medium text-slate-800 truncate">{info.label}</div>
                  <div className="text-slate-500">{info.range}</div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

const AssignModal = ({ employeeId, current, onClose, onSaved }) => {
  const [list, setList] = useState([]);
  const [picked, setPicked] = useState(current || '');
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  useEffect(() => {
    asistenciaAPI.listSchedules().then(setList).catch((e) => setErr(e.message));
  }, []);

  const save = async () => {
    if (!picked) return;
    setBusy(true);
    try {
      await asistenciaAPI.assignSchedule(employeeId, picked);
      onSaved();
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  const removeAll = async () => {
    setBusy(true);
    try {
      await asistenciaAPI.removeEmployeeSchedule(employeeId);
      onSaved();
    } catch (e) {
      setErr(e.message);
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
        </div>
        <div className="border-t border-slate-200 px-6 py-4 flex gap-2 justify-end">
          {current && (
            <button onClick={removeAll} disabled={busy} className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-xl">
              Quitar horario
            </button>
          )}
          <button onClick={onClose} className="px-4 py-2 text-sm border border-slate-200 rounded-xl hover:bg-slate-50">Cancelar</button>
          <button
            onClick={save}
            disabled={!picked || busy}
            className="px-4 py-2 text-sm bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50"
            data-testid="confirm-assign"
          >
            {busy ? 'Guardando…' : 'Asignar'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmployeeHorariosTab;
