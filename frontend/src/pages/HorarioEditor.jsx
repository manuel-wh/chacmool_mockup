import { useState, useMemo, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
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

const getDefaultRangesForKind = (kind) => (
  kind === 'jornada_partida'
    ? [{ start: '09:00', end: '13:00' }, { start: '14:00', end: '18:00' }]
    : [{ start: '09:00', end: '18:00' }]
);

const TIME_OPTIONS = Array.from({ length: 96 }, (_, idx) => {
  const mins = idx * 15;
  return minutesToHHMM(mins);
});

const hhmmToAmPm = (hhmm) => {
  const mins = hhmmToMinutes(hhmm);
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 === 0 ? 12 : h % 12;
  return `${String(h12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${ampm}`;
};

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
  const allowMixedRanges = templateKind === 'jornada_partida';

  const toggleDay = (i) => {
    setDays((prev) => prev.map((d, idx) => {
      if (idx !== i) return d;
      if (d.enabled) return { ...d, enabled: false, ranges: [] };
      return { ...d, enabled: true, ranges: d.ranges.length > 0 ? d.ranges : getDefaultRangesForKind(templateKind) };
    }));
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
    if (templateKind !== 'jornada_partida') return;
    setDays((prev) => prev.map((d, di) => {
      if (di !== dayIdx) return d;
      if ((d.ranges || []).length >= 2) return d;
      const firstEnd = d.ranges?.[0]?.end || '13:00';
      const suggestedStart = minutesToHHMM(Math.min(hhmmToMinutes(firstEnd) + 60, MAX_OF_DAY - 30));
      const suggestedEnd = minutesToHHMM(Math.min(hhmmToMinutes(suggestedStart) + 240, MAX_OF_DAY - 15));
      return { ...d, ranges: [...d.ranges, { start: suggestedStart, end: suggestedEnd }] };
    }));
  };

  const removeRange = (dayIdx, rangeIdx) => {
    setDays((prev) => prev.map((d, di) => di === dayIdx
      ? { ...d, ranges: d.ranges.filter((_, ri) => ri !== rangeIdx) }
      : d
    ));
  };

  const applyTemplate = (kind) => {
    setTemplateKind(kind);
    setDays(getTemplateDays(kind));
  };

  const handleSubmit = () => {
    if (!name.trim()) { setError('Indica un nombre para la jornada'); return; }
    if (weeklyDays === 0) { setError('Selecciona al menos un día laboral'); return; }

    let validationError = '';

    const normalizedDays = days.map((d) => {
      if (!d.enabled) {
        return { ...d, ranges: [] };
      }

      let normalizedRanges = (d.ranges || [])
        .map((r) => ({ start: r.start, end: r.end }))
        .filter((r) => hhmmToMinutes(r.end) > hhmmToMinutes(r.start))
        .sort((a, b) => hhmmToMinutes(a.start) - hhmmToMinutes(b.start));

      if (templateKind === 'jornada_continua') {
        normalizedRanges = normalizedRanges.slice(0, 1);
      } else {
        normalizedRanges = normalizedRanges.slice(0, 2);
      }

      if (normalizedRanges.length === 0) {
        normalizedRanges = getDefaultRangesForKind(templateKind).slice(0, 1);
      }

      const totalDayMinutes = normalizedRanges.reduce(
        (acc, r) => acc + (hhmmToMinutes(r.end) - hhmmToMinutes(r.start)),
        0,
      );

      if (totalDayMinutes > (24 * 60)) {
        validationError = `El día ${DAY_LABELS[d.day]} supera 24 horas.`;
      }

      if (templateKind === 'jornada_partida' && normalizedRanges.length === 2) {
        const firstEnd = hhmmToMinutes(normalizedRanges[0].end);
        const secondStart = hhmmToMinutes(normalizedRanges[1].start);
        if (secondStart <= firstEnd) {
          validationError = `En ${DAY_LABELS[d.day]} el segundo tramo debe empezar después del primero.`;
        }
      }

      return { ...d, ranges: normalizedRanges };
    });

    if (validationError) {
      setError(validationError);
      return;
    }

    onSave({ name: name.trim(), type: 'fijo', days: normalizedDays, template_kind: templateKind });
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
              La jornada continua usa una sola franja por día. La jornada partida permite hasta dos franjas por día para planificar comida y días mixtos.
            </p>
            {allowMixedRanges && (
              <p className="text-[11px] text-emerald-700 mb-5">
                En jornada partida puedes dejar días con un solo rango (sin comida) o dos rangos (con comida).
              </p>
            )}

            <div className="space-y-5">
              {days.map((day, i) => day.enabled && (
                <DayEditor
                  key={i}
                  label={DAY_LABELS[i]}
                  day={day}
                  dayIdx={i}
                  allowMixedRanges={allowMixedRanges}
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

const DayEditor = ({ label, day, dayIdx, allowMixedRanges, onUpdateRange, onAddRange, onRemoveRange }) => {
  const totalMin = day.ranges.reduce((s, r) => s + Math.max(0, hhmmToMinutes(r.end) - hhmmToMinutes(r.start)), 0);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4" data-testid={`day-editor-${dayIdx}`}>
      <h3 className="font-semibold text-slate-900 mb-4" style={{ fontFamily: 'Outfit' }}>
        {label} <span className="text-slate-400 font-normal">({minutesToHHMM(totalMin)})</span>
      </h3>

      {allowMixedRanges ? (
        <PartidaLineEditor
          day={day}
          dayIdx={dayIdx}
          onUpdateRange={onUpdateRange}
          onAddRange={onAddRange}
          onRemoveRange={onRemoveRange}
        />
      ) : (
        <div className="space-y-3">
          {day.ranges.map((r, ri) => (
            <RangeRow
              key={ri}
              range={r}
              onChange={(field, value) => onUpdateRange(dayIdx, ri, field, value)}
              onRemove={null}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const PartidaLineEditor = ({ day, dayIdx, onUpdateRange, onAddRange, onRemoveRange }) => {
  const first = day.ranges?.[0] || { start: '09:00', end: '13:00' };
  const second = day.ranges?.[1] || null;

  const firstStart = hhmmToMinutes(first.start);
  const firstEnd = hhmmToMinutes(first.end);
  const secondStart = second ? hhmmToMinutes(second.start) : null;
  const secondEnd = second ? hhmmToMinutes(second.end) : null;

  const setRangeValue = (rangeIndex, field, valueInMinutes) => {
    onUpdateRange(dayIdx, rangeIndex, field, minutesToHHMM(valueInMinutes));
  };

  const onFirstStart = (mins) => {
    const max = firstEnd - 15;
    const safe = Math.max(MIN_OF_DAY, Math.min(mins, max));
    setRangeValue(0, 'start', safe);
  };

  const onFirstEnd = (mins) => {
    const min = firstStart + 15;
    const max = second ? secondStart - 15 : MAX_OF_DAY - 15;
    const safe = Math.max(min, Math.min(mins, max));
    setRangeValue(0, 'end', safe);
  };

  const onSecondStart = (mins) => {
    if (!second) return;
    const min = firstEnd + 15;
    const max = secondEnd - 15;
    const safe = Math.max(min, Math.min(mins, max));
    setRangeValue(1, 'start', safe);
  };

  const onSecondEnd = (mins) => {
    if (!second) return;
    const min = secondStart + 15;
    const safe = Math.max(min, Math.min(mins, MAX_OF_DAY - 15));
    setRangeValue(1, 'end', safe);
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3" data-testid="partida-line-editor">
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <select
          value={first.start}
          onChange={(e) => onFirstStart(hhmmToMinutes(e.target.value))}
          className="w-[130px] border border-slate-200 rounded-lg px-2.5 py-2 text-sm font-medium text-slate-900 bg-white"
          data-testid="partida-first-start"
        >
          {TIME_OPTIONS.map((opt) => (
            <option key={`partida-fs-${opt}`} value={opt}>{hhmmToAmPm(opt)}</option>
          ))}
        </select>
        <span className="text-slate-400 text-sm">—</span>
        <select
          value={first.end}
          onChange={(e) => onFirstEnd(hhmmToMinutes(e.target.value))}
          className="w-[130px] border border-slate-200 rounded-lg px-2.5 py-2 text-sm font-medium text-slate-900 bg-white"
          data-testid="partida-first-end"
        >
          {TIME_OPTIONS.map((opt) => (
            <option key={`partida-fe-${opt}`} value={opt}>{hhmmToAmPm(opt)}</option>
          ))}
        </select>

        {second ? (
          <>
            <span className="text-slate-300 mx-1">|</span>
            <select
              value={second.start}
              onChange={(e) => onSecondStart(hhmmToMinutes(e.target.value))}
              className="w-[130px] border border-slate-200 rounded-lg px-2.5 py-2 text-sm font-medium text-slate-900 bg-white"
              data-testid="partida-second-start"
            >
              {TIME_OPTIONS.map((opt) => (
                <option key={`partida-ss-${opt}`} value={opt}>{hhmmToAmPm(opt)}</option>
              ))}
            </select>
            <span className="text-slate-400 text-sm">—</span>
            <select
              value={second.end}
              onChange={(e) => onSecondEnd(hhmmToMinutes(e.target.value))}
              className="w-[130px] border border-slate-200 rounded-lg px-2.5 py-2 text-sm font-medium text-slate-900 bg-white"
              data-testid="partida-second-end"
            >
              {TIME_OPTIONS.map((opt) => (
                <option key={`partida-se-${opt}`} value={opt}>{hhmmToAmPm(opt)}</option>
              ))}
            </select>
            <button
              onClick={() => onRemoveRange(dayIdx, 1)}
              className="text-red-400 hover:text-red-600"
              data-testid="partida-remove-second"
              title="Quitar segundo rango"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </>
        ) : (
          <button
            onClick={() => onAddRange(dayIdx)}
            className="ml-1 inline-flex items-center gap-1 text-sm text-emerald-600 hover:text-emerald-700 font-medium"
            data-testid={`add-range-${dayIdx}`}
          >
            <Plus className="w-3.5 h-3.5" /> Añadir rango
          </button>
        )}
      </div>

      <div className="mt-3 relative h-2">
        <div className="absolute inset-0 bg-slate-200 rounded-full" />

        <div
          className="absolute h-2 bg-emerald-500 rounded-full"
          style={{
            left: `${(firstStart / MAX_OF_DAY) * 100}%`,
            width: `${((firstEnd - firstStart) / MAX_OF_DAY) * 100}%`,
          }}
        />

        {second && (
          <div
            className="absolute h-2 bg-emerald-500 rounded-full"
            style={{
              left: `${(secondStart / MAX_OF_DAY) * 100}%`,
              width: `${((secondEnd - secondStart) / MAX_OF_DAY) * 100}%`,
            }}
          />
        )}

        <input
          type="range"
          min={MIN_OF_DAY}
          max={MAX_OF_DAY - 15}
          step={15}
          value={firstStart}
          onChange={(e) => onFirstStart(Number(e.target.value))}
          className="absolute inset-0 w-full appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-emerald-500 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:shadow"
          data-testid="partida-slider-first-start"
        />

        <input
          type="range"
          min={MIN_OF_DAY + 15}
          max={MAX_OF_DAY - 15}
          step={15}
          value={firstEnd}
          onChange={(e) => onFirstEnd(Number(e.target.value))}
          className="absolute inset-0 w-full appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-emerald-500 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:shadow"
          data-testid="partida-slider-first-end"
        />

        {second && (
          <>
            <input
              type="range"
              min={MIN_OF_DAY + 15}
              max={MAX_OF_DAY - 15}
              step={15}
              value={secondStart}
              onChange={(e) => onSecondStart(Number(e.target.value))}
              className="absolute inset-0 w-full appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-emerald-500 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:shadow"
              data-testid="partida-slider-second-start"
            />

            <input
              type="range"
              min={MIN_OF_DAY + 15}
              max={MAX_OF_DAY - 15}
              step={15}
              value={secondEnd}
              onChange={(e) => onSecondEnd(Number(e.target.value))}
              className="absolute inset-0 w-full appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-emerald-500 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:shadow"
              data-testid="partida-slider-second-end"
            />
          </>
        )}
      </div>
    </div>
  );
};

/**
 * RangeRow: un rango horario con dos selectores (inicio/fin) en la misma fila
 * y slider visual para ajustes rápidos.
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

  const handleStartSelect = (value) => {
    const selected = hhmmToMinutes(value);
    const nextStart = Math.min(selected, endMin - 15);
    onChange('start', minutesToHHMM(nextStart));
  };

  const handleEndSelect = (value) => {
    const selected = hhmmToMinutes(value);
    const nextEnd = Math.max(selected, startMin + 15);
    onChange('end', minutesToHHMM(nextEnd));
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3" data-testid="range-row">
      <div className="flex items-center gap-2">
        <select
          value={range.start}
          onChange={(e) => handleStartSelect(e.target.value)}
          className="flex-1 min-w-[140px] border border-slate-200 rounded-lg px-2.5 py-2 text-sm font-medium text-slate-900 bg-white"
          data-testid="range-start-select"
        >
          {TIME_OPTIONS.map((opt) => (
            <option key={`start-${opt}`} value={opt}>{hhmmToAmPm(opt)}</option>
          ))}
        </select>

        <span className="text-slate-400 text-sm">—</span>

        <select
          value={range.end}
          onChange={(e) => handleEndSelect(e.target.value)}
          className="flex-1 min-w-[140px] border border-slate-200 rounded-lg px-2.5 py-2 text-sm font-medium text-slate-900 bg-white"
          data-testid="range-end-select"
        >
          {TIME_OPTIONS.map((opt) => (
            <option key={`end-${opt}`} value={opt}>{hhmmToAmPm(opt)}</option>
          ))}
        </select>

        {onRemove && (
          <button onClick={onRemove} className="text-red-400 hover:text-red-600 flex-shrink-0" data-testid="remove-range">
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="mt-3 relative h-2">
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
    </div>
  );
};

export default HorarioEditor;
