import { useState, useMemo, useEffect } from 'react';
import { X, Plus, Trash2, Clock } from 'lucide-react';
import {
  DAY_LABELS, DAY_SHORT, hhmmToMinutes, minutesToHHMM, computeWeeklyHours,
  TEMPLATE_JORNADA_CONTINUA, TEMPLATE_JORNADA_PARTIDA,
} from '../utils/asistencia';

/**
 * Editor de jornada laboral - replica diseño de las capturas:
 * - Panel izquierdo: nombre, días pill, total horas, half-day calc
 * - Panel derecho: por cada día activo, rangos con "slider" visual e inputs HH:MM
 *
 * Props:
 *  - initial: schedule existente (o null)
 *  - onSave({ name, type, days, template_kind })
 *  - onCancel()
 */
const MIN_OF_DAY = 0;
const MAX_OF_DAY = 24 * 60;

const getTemplateDays = (kind) => (
  kind === 'jornada_partida' ? TEMPLATE_JORNADA_PARTIDA() : TEMPLATE_JORNADA_CONTINUA()
);

const HorarioEditor = ({ initial = null, onSave, onCancel }) => {
  const [name, setName] = useState(initial?.name || '');
  const [templateKind, setTemplateKind] = useState(initial?.template_kind === 'jornada_partida' ? 'jornada_partida' : 'jornada_continua');
  const [days, setDays] = useState(initial?.days || getTemplateDays(initial?.template_kind));
  const [error, setError] = useState('');
  const isEditMode = Boolean(initial?.id);

  useEffect(() => {
    if (initial) {
      setName(initial.name || '');
      setTemplateKind(initial.template_kind === 'jornada_partida' ? 'jornada_partida' : 'jornada_continua');
      setDays(initial.days || getTemplateDays(initial.template_kind));
    }
  }, [initial]);

  const weeklyHours = useMemo(() => computeWeeklyHours(days), [days]);
  const weeklyDays = days.filter((d) => d.enabled).length;

  const toggleDay = (i) => {
    setDays((prev) => prev.map((d, idx) => idx === i
      ? { ...d, enabled: !d.enabled, ranges: !d.enabled && d.ranges.length === 0 ? [{ start: '09:00', end: '18:00' }] : d.ranges }
      : d
    ));
  };

  const updateRange = (dayIdx, rangeIdx, field, value) => {
    setDays((prev) => prev.map((d, di) => {
      if (di !== dayIdx) return d;
      return {
        ...d,
        ranges: d.ranges.map((r, ri) => ri === rangeIdx ? { ...r, [field]: value } : r),
      };
    }));
  };

  const addRange = (dayIdx) => {
    setDays((prev) => prev.map((d, di) => di === dayIdx
      ? { ...d, ranges: [...d.ranges, { start: '14:00', end: '17:00' }] }
      : d
    ));
  };

  const removeRange = (dayIdx, rangeIdx) => {
    setDays((prev) => prev.map((d, di) => di === dayIdx
      ? { ...d, ranges: d.ranges.filter((_, ri) => ri !== rangeIdx) }
      : d
    ));
  };

  const applyTemplate = (kind) => {
    setTemplateKind(kind);
    if (kind === 'jornada_continua') setDays(TEMPLATE_JORNADA_CONTINUA());
    if (kind === 'jornada_partida') setDays(TEMPLATE_JORNADA_PARTIDA());
  };

  const handleSubmit = () => {
    if (!name.trim()) { setError('Indica un nombre para la jornada'); return; }
    if (weeklyDays === 0) { setError('Selecciona al menos un día laboral'); return; }
    onSave({ name: name.trim(), type: 'fijo', days, template_kind: templateKind });
  };

  // Cálculo de medio día (40% del día más alto)
  const dailyHoursMap = useMemo(() => days.map((d) =>
    d.ranges.reduce((s, r) => s + (hhmmToMinutes(r.end) - hhmmToMinutes(r.start)), 0)
  ), [days]);
  const totalMinutes = dailyHoursMap.reduce((a, b) => a + b, 0);
  const halfDayWeekly = weeklyDays > 0 ? totalMinutes / weeklyDays / 2 : 0;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center z-50 p-4 overflow-y-auto" data-testid="horario-editor">
      <div className="bg-white rounded-2xl w-full max-w-6xl my-4 max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 rounded-t-2xl px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>
            {isEditMode ? 'Editar horario' : 'Crear horario'}
          </h2>
          <button onClick={onCancel} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mx-6 mt-4 bg-red-50 border border-red-200 text-red-800 rounded-xl px-3 py-2 text-sm">
            {error}
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-0 flex-1 min-h-0 overflow-hidden">
          {/* Panel izquierdo: meta */}
          <div className="p-6 space-y-5 overflow-y-auto border-r border-slate-200">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Nombre</label>
              <input
                data-testid="horario-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ej: Normal"
                className="w-full border border-slate-200 rounded-xl px-4 py-3 font-medium text-slate-900"
              />
            </div>

            <p className="text-sm text-slate-500 leading-relaxed">
              A la derecha podrás visualizar y editar el horario que estás creando.
              Añade descansos preestablecidos, nuevas franjas de tiempo o modifica días en particular.
            </p>

            {/* Días pill */}
            <div>
              <p className="text-sm font-medium text-slate-700 mb-3">Selecciona los días laborales</p>
              <div className="flex gap-2" data-testid="day-pills">
                {DAY_SHORT.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => toggleDay(i)}
                    data-testid={`day-pill-${i}`}
                    className={`w-9 h-9 rounded-full text-xs font-semibold flex items-center justify-center transition ${
                      days[i].enabled
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-indigo-50 text-indigo-300'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-100 pt-4 space-y-2">
              <p className="text-sm text-slate-700">
                Total de horas en la semana:{' '}
                <span className="font-bold text-slate-900" data-testid="weekly-total">
                  {minutesToHHMM(weeklyHours * 60)}
                </span>
              </p>
            </div>

            <div className="border-t border-slate-100 pt-4">
              <p className="text-sm font-semibold text-slate-900 mb-3">¿Cómo se calcula el medio día de vacaciones?</p>
              <p className="text-sm text-slate-600 mb-3">
                Según horario semanal: <span className="font-semibold text-slate-900">{minutesToHHMM(halfDayWeekly)}</span>
              </p>
              <p className="text-sm text-slate-600 mb-2">Según horario diario:</p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {dailyHoursMap.map((mins, i) => days[i].enabled && (
                  <div key={i} className="flex justify-between">
                    <span className="text-slate-600">{DAY_LABELS[i]}</span>
                    <span className="font-semibold text-slate-900">{minutesToHHMM(mins / 2)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Tipo */}
            <div className="border-t border-slate-100 pt-4">
              <p className="text-sm font-medium text-slate-700 mb-2">Tipo de horario</p>
              <div className="border border-slate-200 rounded-xl p-3 text-sm bg-slate-50">
                <div className="font-semibold text-slate-900">Horario fijo</div>
                <div className="text-xs text-slate-500">Definido por plantilla de jornada continua o partida</div>
              </div>
            </div>
          </div>

          {/* Panel derecho: días */}
          <div className="p-6 overflow-y-auto bg-slate-50/30">
            <div className="flex items-center justify-between mb-5">
              <span className="text-sm font-medium text-slate-700">Aplicar plantilla de:</span>
              <select
                value={templateKind}
                onChange={(e) => applyTemplate(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2 text-sm bg-white"
                data-testid="template-select"
              >
                <option value="jornada_continua">Jornada continua</option>
                <option value="jornada_partida">Jornada partida</option>
              </select>
            </div>
            <p className="text-xs text-slate-500 mb-5 leading-relaxed">
              La jornada continua creará una sola franja de tiempo mientras que la jornada partida creará dos franjas con un periodo no remunerado en medio.
            </p>

            <div className="space-y-5">
              {days.map((day, i) => day.enabled && (
                <DayEditor
                  key={i}
                  label={DAY_LABELS[i]}
                  day={day}
                  dayIdx={i}
                  onUpdateRange={updateRange}
                  onAddRange={addRange}
                  onRemoveRange={removeRange}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 px-6 py-4 flex justify-end gap-3 bg-white rounded-b-2xl">
          <button
            data-testid="horario-cancel"
            onClick={onCancel}
            className="px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-xl"
          >
            Cancelar
          </button>
          <button
            data-testid="horario-save"
            onClick={handleSubmit}
            className="px-5 py-2.5 text-sm font-medium bg-slate-900 text-white rounded-xl hover:bg-slate-800"
          >
            {isEditMode ? 'Editar horario' : 'Crear horario'}
          </button>
        </div>
      </div>
    </div>
  );
};

const DayEditor = ({ label, day, dayIdx, onUpdateRange, onAddRange, onRemoveRange }) => {
  const totalMin = day.ranges.reduce((s, r) => s + Math.max(0, hhmmToMinutes(r.end) - hhmmToMinutes(r.start)), 0);
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4" data-testid={`day-editor-${dayIdx}`}>
      <h3 className="font-semibold text-slate-900 mb-4" style={{ fontFamily: 'Outfit' }}>
        {label} <span className="text-slate-400 font-normal">({minutesToHHMM(totalMin)})</span>
      </h3>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
        {day.ranges.map((r, ri) => (
          <RangeRow
            key={ri}
            range={r}
            onChange={(field, value) => onUpdateRange(dayIdx, ri, field, value)}
            onRemove={day.ranges.length > 1 ? () => onRemoveRange(dayIdx, ri) : null}
          />
        ))}
      </div>
      <button
        onClick={() => onAddRange(dayIdx)}
        className="mt-3 inline-flex items-center gap-1 text-sm text-emerald-600 hover:text-emerald-700 font-medium"
        data-testid={`add-range-${dayIdx}`}
      >
        <Plus className="w-3.5 h-3.5" /> Añadir rango
      </button>
    </div>
  );
};

/**
 * RangeRow: un rango horario con doble slider visual + inputs HH:MM.
 * Implementación: dos inputs type=range superpuestos + chips con horas.
 */
const RangeRow = ({ range, onChange, onRemove }) => {
  const startMin = hhmmToMinutes(range.start);
  const endMin = hhmmToMinutes(range.end);

  const handleStart = (val) => {
    const v = Math.min(Number(val), endMin - 15);
    onChange('start', minutesToHHMM(v));
  };
  const handleEnd = (val) => {
    const v = Math.max(Number(val), startMin + 15);
    onChange('end', minutesToHHMM(v));
  };

  // Para mostrar AM/PM
  const fmt = (mins) => {
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h % 12 === 0 ? 12 : h % 12;
    return `${String(h12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${ampm}`;
  };

  return (
    <div className="flex items-center gap-3" data-testid="range-row">
      {/* Chip start */}
      <div className="flex flex-col items-center gap-1 flex-shrink-0">
        <div className="bg-white border border-slate-200 rounded-full px-3 py-1.5 text-xs font-medium text-slate-900 inline-flex items-center gap-1.5">
          {fmt(startMin)} <Clock className="w-3 h-3 text-slate-400" />
        </div>
      </div>

      {/* Doble slider */}
      <div className="flex-1 relative h-2">
        <div className="absolute inset-0 bg-slate-200 rounded-full" />
        <div
          className="absolute h-2 bg-emerald-500 rounded-full"
          style={{
            left: `${(startMin / MAX_OF_DAY) * 100}%`,
            width: `${((endMin - startMin) / MAX_OF_DAY) * 100}%`,
          }}
        />
        <input
          type="range"
          min={MIN_OF_DAY}
          max={MAX_OF_DAY}
          step={15}
          value={startMin}
          onChange={(e) => handleStart(e.target.value)}
          className="absolute inset-0 w-full appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-emerald-500 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:shadow"
          data-testid="range-start"
        />
        <input
          type="range"
          min={MIN_OF_DAY}
          max={MAX_OF_DAY}
          step={15}
          value={endMin}
          onChange={(e) => handleEnd(e.target.value)}
          className="absolute inset-0 w-full appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-emerald-500 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:shadow"
          data-testid="range-end"
        />
      </div>

      {/* Chip end */}
      <div className="flex flex-col items-center gap-1 flex-shrink-0">
        <div className="bg-white border border-slate-200 rounded-full px-3 py-1.5 text-xs font-medium text-slate-900 inline-flex items-center gap-1.5">
          {fmt(endMin)} <Clock className="w-3 h-3 text-slate-400" />
        </div>
      </div>

      {onRemove && (
        <button onClick={onRemove} className="text-red-400 hover:text-red-600 flex-shrink-0" data-testid="remove-range">
          <Trash2 className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

export default HorarioEditor;
