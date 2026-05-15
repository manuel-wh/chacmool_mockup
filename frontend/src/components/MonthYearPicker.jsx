import { useEffect, useRef, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const MONTHS_ES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];
const DAYS_ES = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];

/**
 * Selector avanzado de fecha con drill-down día/mes/año.
 *
 * Props:
 *  - value: Date — fecha actual seleccionada
 *  - onChange: (Date) => void
 *  - mode: 'month' | 'week' | 'day'   (mes ancla la fecha al día 1, semana al lunes)
 *  - label?: string                   (label opcional para el botón)
 */
const MonthYearPicker = ({ value, onChange, mode = 'month', label }) => {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState('months'); // 'months' | 'years' | 'days'
  const [tempYear, setTempYear] = useState(value.getFullYear());
  const [tempMonth, setTempMonth] = useState(value.getMonth());
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handle = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handle);
    return () => document.removeEventListener('mousedown', handle);
  }, [open]);

  useEffect(() => {
    setTempYear(value.getFullYear());
    setTempMonth(value.getMonth());
  }, [value]);

  const handleSelectMonth = (m) => {
    setTempMonth(m);
    if (mode === 'month') {
      onChange(new Date(tempYear, m, 1));
      setOpen(false);
    } else {
      setView('days');
    }
  };

  const handleSelectYear = (y) => {
    setTempYear(y);
    setView('months');
  };

  const handleSelectDay = (d) => {
    const picked = new Date(tempYear, tempMonth, d);
    if (mode === 'week') {
      // Snap to Monday of that week
      const day = (picked.getDay() + 6) % 7;
      picked.setDate(picked.getDate() - day);
    }
    onChange(picked);
    setOpen(false);
  };

  const triggerLabel = label || (mode === 'month'
    ? `${MONTHS_ES[value.getMonth()]} ${value.getFullYear()}`
    : value.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' }));

  // Construir grilla de días del mes en vista
  const daysInMonth = new Date(tempYear, tempMonth + 1, 0).getDate();
  const firstDayOffset = (new Date(tempYear, tempMonth, 1).getDay() + 6) % 7;

  const yearRangeStart = Math.floor(tempYear / 12) * 12;

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => { setOpen((o) => !o); setView('months'); }}
        className="px-3 py-1.5 text-sm font-medium text-slate-900 hover:bg-slate-100 rounded-lg transition-colors capitalize min-w-[140px]"
        data-testid="datepicker-trigger"
      >
        {triggerLabel}
      </button>

      {open && (
        <div className="absolute z-40 mt-2 bg-white border border-slate-200 rounded-2xl shadow-xl p-4 w-[280px]" data-testid="datepicker-popover">
          {view === 'months' && (
            <>
              <div className="flex items-center justify-between mb-3">
                <button onClick={() => setTempYear((y) => y - 1)} className="p-1 rounded hover:bg-slate-100">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button onClick={() => setView('years')} className="text-sm font-semibold text-slate-900 hover:bg-slate-100 px-3 py-1 rounded-lg" data-testid="datepicker-year-trigger">
                  {tempYear}
                </button>
                <button onClick={() => setTempYear((y) => y + 1)} className="p-1 rounded hover:bg-slate-100">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {MONTHS_ES.map((m, i) => {
                  const isCurrent = i === value.getMonth() && tempYear === value.getFullYear();
                  return (
                    <button
                      key={m}
                      onClick={() => handleSelectMonth(i)}
                      className={`text-sm py-2 rounded-lg transition-colors ${isCurrent ? 'bg-slate-900 text-white' : 'hover:bg-slate-100 text-slate-700'}`}
                      data-testid={`datepicker-month-${i}`}
                    >
                      {m.slice(0, 3)}
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {view === 'years' && (
            <>
              <div className="flex items-center justify-between mb-3">
                <button onClick={() => setTempYear((y) => y - 12)} className="p-1 rounded hover:bg-slate-100">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-sm font-semibold text-slate-900">{yearRangeStart} - {yearRangeStart + 11}</span>
                <button onClick={() => setTempYear((y) => y + 12)} className="p-1 rounded hover:bg-slate-100">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {Array.from({ length: 12 }, (_, i) => yearRangeStart + i).map((y) => {
                  const isCurrent = y === value.getFullYear();
                  return (
                    <button
                      key={y}
                      onClick={() => handleSelectYear(y)}
                      className={`text-sm py-2 rounded-lg transition-colors ${isCurrent ? 'bg-slate-900 text-white' : 'hover:bg-slate-100 text-slate-700'}`}
                      data-testid={`datepicker-year-${y}`}
                    >
                      {y}
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {view === 'days' && (
            <>
              <div className="flex items-center justify-between mb-3">
                <button onClick={() => setView('months')} className="p-1 rounded hover:bg-slate-100">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-sm font-semibold text-slate-900 capitalize">{MONTHS_ES[tempMonth]} {tempYear}</span>
                <span className="w-6" />
              </div>
              <div className="grid grid-cols-7 gap-1 mb-1">
                {DAYS_ES.map((d) => <div key={d} className="text-[10px] text-slate-400 text-center">{d}</div>)}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {Array.from({ length: firstDayOffset }, (_, i) => <div key={`off-${i}`} />)}
                {Array.from({ length: daysInMonth }, (_, i) => i + 1).map((d) => {
                  const isCurrent = d === value.getDate() && tempMonth === value.getMonth() && tempYear === value.getFullYear();
                  return (
                    <button
                      key={d}
                      onClick={() => handleSelectDay(d)}
                      className={`text-xs py-1.5 rounded transition-colors ${isCurrent ? 'bg-slate-900 text-white' : 'hover:bg-slate-100 text-slate-700'}`}
                      data-testid={`datepicker-day-${d}`}
                    >
                      {d}
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default MonthYearPicker;
