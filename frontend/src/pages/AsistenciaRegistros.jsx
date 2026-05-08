import { useState, useEffect, useMemo, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import { asistenciaAPI } from '../services/api';
import {
  DAY_LABELS, MONTH_LABELS, secondsToHM, toISODate, startOfWeek, addDays, pad2,
} from '../utils/asistencia';

/**
 * Vista de registros de asistencia (calendario semanal o mensual).
 * Props:
 *  - employeeId: null para usuario actual, string para admin viendo a otro
 */
const AsistenciaRegistros = ({ employeeId = null }) => {
  const [view, setView] = useState('semanal'); // 'semanal' | 'mensual'
  const [anchor, setAnchor] = useState(new Date());
  const [sessions, setSessions] = useState([]);
  const [summary, setSummary] = useState({ worked_seconds: 0, planned_seconds: 0 });
  const [loading, setLoading] = useState(true);

  const range = useMemo(() => {
    if (view === 'semanal') {
      const from = startOfWeek(anchor);
      const to = addDays(from, 6);
      return { from, to };
    }
    const from = new Date(anchor.getFullYear(), anchor.getMonth(), 1);
    const to = new Date(anchor.getFullYear(), anchor.getMonth() + 1, 0);
    return { from, to };
  }, [view, anchor]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const dateFrom = toISODate(range.from);
      const dateTo = toISODate(range.to);
      const sum = await asistenciaAPI.summary({ employeeId, dateFrom, dateTo });
      setSummary({ worked_seconds: sum.worked_seconds, planned_seconds: sum.planned_seconds });
      setSessions(sum.sessions || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [employeeId, range.from, range.to]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const navigatePrev = () => {
    if (view === 'semanal') setAnchor((d) => addDays(d, -7));
    else setAnchor((d) => new Date(d.getFullYear(), d.getMonth() - 1, 1));
  };
  const navigateNext = () => {
    if (view === 'semanal') setAnchor((d) => addDays(d, 7));
    else setAnchor((d) => new Date(d.getFullYear(), d.getMonth() + 1, 1));
  };

  const rangeLabel = view === 'semanal'
    ? `${pad2(range.from.getDate())}/${pad2(range.from.getMonth() + 1)}/${range.from.getFullYear()} - ${pad2(range.to.getDate())}/${pad2(range.to.getMonth() + 1)}/${range.to.getFullYear()}`
    : `${MONTH_LABELS[anchor.getMonth()]} ${anchor.getFullYear()}`;

  const progress = summary.planned_seconds > 0
    ? Math.min(100, (summary.worked_seconds / summary.planned_seconds) * 100)
    : 0;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm" data-testid="registros-card">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3 mb-5">
        <div>
          <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>
            {view === 'semanal' ? 'Esta semana' : 'Este mes'}
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            <span className="font-semibold text-slate-900" data-testid="worked-time">{secondsToHM(summary.worked_seconds)}</span>
            {' / '}
            <span data-testid="planned-time">{secondsToHM(summary.planned_seconds)} planificadas</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Navegador */}
          <div className="flex items-center gap-1 border border-slate-200 rounded-xl px-2 py-1.5 bg-white" data-testid="range-picker">
            <button onClick={navigatePrev} className="p-1 text-slate-500 hover:text-slate-900" data-testid="prev-btn">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-sm font-medium text-slate-900 px-2 min-w-[200px] text-center">
              {rangeLabel}
            </span>
            <button onClick={navigateNext} className="p-1 text-slate-500 hover:text-slate-900" data-testid="next-btn">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          {/* Selector de vista */}
          <select
            value={view}
            onChange={(e) => setView(e.target.value)}
            className="border border-slate-200 rounded-xl px-3 py-2 text-sm bg-white"
            data-testid="view-select"
          >
            <option value="semanal">Semanal</option>
            <option value="mensual">Mensual</option>
          </select>
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-6">
        <div className="h-full bg-emerald-500 transition-all" style={{ width: `${progress}%` }} />
      </div>

      {loading ? (
        <div className="py-8 text-center text-slate-400 text-sm">Cargando…</div>
      ) : view === 'semanal' ? (
        <WeekView from={range.from} sessions={sessions} />
      ) : (
        <MonthView anchor={anchor} sessions={sessions} />
      )}
    </div>
  );
};

// ============== Sub-vistas ==============

const WeekView = ({ from, sessions }) => {
  const days = Array.from({ length: 7 }, (_, i) => addDays(from, i));
  const sessionsByDate = useMemo(() => {
    const m = {};
    for (const s of sessions) {
      (m[s.date] = m[s.date] || []).push(s);
    }
    return m;
  }, [sessions]);

  return (
    <div className="grid grid-cols-7 gap-2 min-h-[280px]" data-testid="week-grid">
      {days.map((d, idx) => {
        const iso = toISODate(d);
        const list = sessionsByDate[iso] || [];
        const dayWorked = list.reduce(
          (acc, s) => acc + (s.duration_seconds || s.seconds_elapsed || 0),
          0,
        );
        return (
          <div key={iso} className="border border-slate-200 rounded-xl p-3 flex flex-col">
            <p className="text-xs text-slate-500 uppercase tracking-wide">
              {DAY_LABELS[idx].slice(0, 3)}
            </p>
            <p className="text-lg font-semibold text-slate-900 mb-2">{d.getDate()}</p>
            <div className="space-y-1.5 flex-1">
              {list.length === 0 && (
                <div className="text-xs text-slate-300">—</div>
              )}
              {list.map((s) => (
                <div
                  key={s.id}
                  className={`rounded-lg px-2 py-1.5 text-xs ${
                    s.status === 'closed' ? 'bg-emerald-50 border border-emerald-200 text-emerald-800' :
                    s.status === 'paused' ? 'bg-amber-50 border border-amber-200 text-amber-800' :
                    'bg-blue-50 border border-blue-200 text-blue-800'
                  }`}
                  data-testid={`session-${s.id}`}
                >
                  <div className="font-medium">
                    {new Date(s.clock_in).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                    {s.clock_out && ` - ${new Date(s.clock_out).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`}
                  </div>
                </div>
              ))}
              {list.length > 0 && (
                <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-100 mt-1">
                  {secondsToHM(dayWorked)}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const MonthView = ({ anchor, sessions }) => {
  const year = anchor.getFullYear();
  const month = anchor.getMonth();
  const firstDay = new Date(year, month, 1);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const totalDays = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < startOffset; i++) cells.push(null);
  for (let d = 1; d <= totalDays; d++) cells.push(new Date(year, month, d));
  while (cells.length % 7 !== 0) cells.push(null);

  const sessionsByDate = useMemo(() => {
    const m = {};
    for (const s of sessions) (m[s.date] = m[s.date] || []).push(s);
    return m;
  }, [sessions]);

  const today = toISODate(new Date());

  return (
    <div data-testid="month-grid">
      <div className="grid grid-cols-7 gap-1 mb-2">
        {DAY_LABELS.map((l) => (
          <div key={l} className="text-xs text-slate-500 text-center font-medium py-1">{l.slice(0, 3)}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {cells.map((d, i) => {
          if (!d) return <div key={`e-${i}`} className="aspect-square" />;
          const iso = toISODate(d);
          const list = sessionsByDate[iso] || [];
          const dayWorked = list.reduce((acc, s) => acc + (s.duration_seconds || s.seconds_elapsed || 0), 0);
          const isToday = iso === today;
          return (
            <div
              key={iso}
              className={`aspect-square border rounded-lg p-1.5 flex flex-col text-xs ${
                isToday ? 'border-indigo-400 bg-indigo-50/40' : 'border-slate-200'
              }`}
            >
              <span className={`font-medium ${isToday ? 'text-indigo-700' : 'text-slate-700'}`}>
                {d.getDate()}
              </span>
              {list.length > 0 && (
                <div className="mt-auto">
                  <div className="h-1 bg-emerald-500 rounded-full mb-0.5" />
                  <div className="text-[10px] text-emerald-700 font-semibold truncate">
                    {secondsToHM(dayWorked)}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AsistenciaRegistros;
