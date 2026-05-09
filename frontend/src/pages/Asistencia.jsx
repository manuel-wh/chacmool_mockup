import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Settings, Calendar, AlertCircle, CheckCircle2, Clock, LogOut } from 'lucide-react';
import { asistenciaAPI } from '../services/api';
import { secondsToHM, secondsToHMS, toISODate, startOfWeek, addDays } from '../utils/asistencia';
import AsistenciaRegistros from './AsistenciaRegistros';

/**
 * Vista principal de Asistencia.
 * - Empleado: ve cronómetro + sus registros
 * - Admin: ve lo mismo + botón a Configuración
 */
const Asistencia = ({ isAdmin = false }) => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);   // { session, schedule, assigned, planned_seconds_today }
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [tick, setTick] = useState(0);
  const [error, setError] = useState('');
  const intervalRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const d = await asistenciaAPI.current();
      setData(d);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Cronómetro local: incrementa solo cuando hay sesión activa (no pausada)
  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (data?.session && data.session.status === 'active') {
      intervalRef.current = setInterval(() => setTick((t) => t + 1), 1000);
    }
    return () => intervalRef.current && clearInterval(intervalRef.current);
  }, [data?.session?.status, data?.session?.id]);

  const baseSeconds = data?.session?.seconds_elapsed || 0;
  const elapsed = data?.session?.status === 'active' ? baseSeconds + tick : baseSeconds;
  const planned = data?.planned_seconds_today || 0;
  const remaining = Math.max(0, planned - elapsed);
  const progress = planned > 0 ? Math.min(100, (elapsed / planned) * 100) : 0;

  const handleAction = async (fn) => {
    setBusy(true);
    setError('');
    try {
      await fn();
      setTick(0);
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500">
        <div className="animate-spin w-8 h-8 border-2 border-slate-300 border-t-slate-900 rounded-full mx-auto mb-3" />
        Cargando…
      </div>
    );
  }

  const { session, schedule, assigned } = data || {};

  // Rango "Esta semana" para mostrar resumen rápido
  const weekStart = startOfWeek(new Date());
  const weekEnd = addDays(weekStart, 6);

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto" data-testid="asistencia-view">
      {/* Header */}
      <div className="flex items-start justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>
            Asistencia
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Registra tu jornada laboral y consulta tus horarios
          </p>
        </div>
        {isAdmin && (
          <button
            data-testid="asistencia-config-btn"
            onClick={() => navigate('/asistencia/configuracion')}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 transition"
          >
            <Settings className="w-4 h-4" /> Configuración
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-800 rounded-xl px-4 py-3 text-sm flex items-start gap-2">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Card cronómetro */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 lg:p-8 mb-6 shadow-sm" data-testid="clock-card">
        {!assigned ? (
          <div className="text-center py-6">
            <div className="w-16 h-16 mx-auto rounded-full bg-amber-50 border border-amber-200 flex items-center justify-center mb-3">
              <AlertCircle className="w-7 h-7 text-amber-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit' }}>
              Sin horario asignado
            </h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Para empezar a registrar tu jornada, un administrador debe asignarte un horario en tu perfil.
            </p>
          </div>
        ) : (
          <div className="grid lg:grid-cols-2 gap-6 items-center">
            {/* Cronómetro grande */}
            <div className="text-center lg:text-left">
              <div className="text-xs uppercase tracking-wider text-slate-500 mb-2">
                {schedule?.name || 'Tu jornada'} · Hoy
              </div>
              <div
                className={`text-6xl lg:text-7xl font-semibold tabular-nums ${
                  session?.status === 'active' ? 'text-emerald-600' :
                  session?.status === 'paused' ? 'text-amber-600' : 'text-slate-400'
                }`}
                style={{ fontFamily: 'Outfit' }}
                data-testid="clock-elapsed"
              >
                {secondsToHMS(elapsed)}
              </div>
              <div className="text-sm text-slate-500 mt-2">
                {planned > 0 ? (
                  <>Planificado: <span className="font-semibold text-slate-900">{secondsToHM(planned)}</span> · Restante: <span className="font-semibold text-slate-900" data-testid="clock-remaining">{secondsToHM(remaining)}</span></>
                ) : (
                  <>Hoy no tienes horas planificadas en tu horario</>
                )}
              </div>
              {planned > 0 && (
                <div className="mt-4 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
            </div>

            {/* Botón único de acción */}
            <div className="flex flex-col gap-3 max-w-sm mx-auto w-full">
              <button
                data-testid="toggle-attendance-btn"
                disabled={busy}
                onClick={() => handleAction(session ? asistenciaAPI.clockOut : asistenciaAPI.clockIn)}
                className={`rounded-xl px-5 py-4 font-medium disabled:opacity-50 inline-flex items-center justify-center gap-2 transition text-white ${
                  session ? 'bg-slate-900 hover:bg-slate-800' : 'bg-emerald-600 hover:bg-emerald-700'
                }`}
              >
                {session ? <LogOut className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                {session ? 'Registrar salida' : 'Registrar entrada'}
              </button>

              {session && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-600 flex items-center gap-2 mt-2">
                  <Clock className="w-3.5 h-3.5" />
                  Iniciado: {new Date(session.clock_in).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  <span className="ml-auto inline-flex items-center gap-1 text-emerald-700"><CheckCircle2 className="w-3 h-3" /> Activa</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Registros (calendario) */}
      <AsistenciaRegistros
        employeeId={null}  /* null = usuario actual */
        canRequest={true}
      />
    </div>
  );
};

export default Asistencia;
