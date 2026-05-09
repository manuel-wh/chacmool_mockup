import { useEffect, useMemo, useState } from 'react';
import { Clock3, Hash, LockKeyhole, ArrowLeft, CheckCircle2, AlertCircle, LogIn, LogOut } from 'lucide-react';
import { asistenciaAPI } from '../services/api';

const padDigits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'C', '0', '←'];

const KioscoPage = () => {
  const [now, setNow] = useState(new Date());
  const [configLoading, setConfigLoading] = useState(true);
  const [kioscoEnabled, setKioscoEnabled] = useState(false);
  const [accessCode, setAccessCode] = useState('');
  const [pin, setPin] = useState('');
  const [activeField, setActiveField] = useState('code');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setConfigLoading(true);
      try {
        const cfg = await asistenciaAPI.kioskPublicConfig();
        if (!mounted) return;
        setKioscoEnabled(Boolean(cfg.kiosco_enabled));
      } catch (e) {
        if (!mounted) return;
        setError(e.message || 'No se pudo cargar la configuración del kiosco.');
      } finally {
        if (mounted) setConfigLoading(false);
      }
    };
    load();
    return () => { mounted = false; };
  }, []);

  const formattedDate = useMemo(() => now.toLocaleDateString('es-ES', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  }), [now]);

  const formattedTime = useMemo(() => now.toLocaleTimeString('es-ES', {
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  }), [now]);

  const applyDigit = (digit) => {
    setError('');
    setMessage('');

    if (digit === 'C') {
      if (activeField === 'code') setAccessCode('');
      if (activeField === 'pin') setPin('');
      return;
    }
    if (digit === '←') {
      if (activeField === 'code') setAccessCode((v) => v.slice(0, -1));
      if (activeField === 'pin') setPin((v) => v.slice(0, -1));
      return;
    }

    if (activeField === 'code') {
      setAccessCode((prev) => (prev + digit).slice(0, 16));
    } else {
      setPin((prev) => (prev + digit).slice(0, 8));
    }
  };

  const submitPunch = async () => {
    if (!accessCode || !pin) {
      setError('Ingresa código de acceso y PIN.');
      return;
    }
    setBusy(true);
    setError('');
    setMessage('');
    try {
      const res = await asistenciaAPI.kioskPunch({ accessCode, pin });
      setResult(res);
      setMessage(res.message || 'Registro exitoso.');
      setPin('');
      setActiveField('pin');
    } catch (e) {
      setError(e.message || 'No se pudo registrar.');
    } finally {
      setBusy(false);
    }
  };

  if (configLoading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-14 h-14 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/80">Cargando kiosco…</p>
        </div>
      </div>
    );
  }

  if (!kioscoEnabled) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
        <div className="max-w-lg w-full border border-slate-700 bg-slate-900 rounded-3xl p-8 text-center">
          <AlertCircle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
          <h1 className="text-2xl font-semibold mb-2" style={{ fontFamily: 'Outfit' }}>Kiosco deshabilitado</h1>
          <p className="text-slate-300 text-sm mb-4">
            El administrador debe activar el modo kiosco desde Asistencia → Configuración → Dispositivos.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white p-4 md:p-8" data-testid="kiosco-page">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-[1.2fr_1fr] gap-6">
        <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm p-6 md:p-8">
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-indigo-200/80 mb-4">
            <Clock3 className="w-4 h-4" /> Kiosco de asistencia
          </div>
          <h1 className="text-4xl md:text-6xl font-semibold mb-2" style={{ fontFamily: 'Outfit' }}>{formattedTime}</h1>
          <p className="text-slate-300 capitalize mb-8">{formattedDate}</p>

          <div className="grid md:grid-cols-2 gap-4 mb-5">
            <button
              onClick={() => setActiveField('code')}
              className={`text-left rounded-2xl border p-4 transition ${
                activeField === 'code' ? 'border-indigo-300 bg-indigo-500/20' : 'border-white/10 bg-white/5 hover:bg-white/10'
              }`}
              data-testid="kiosco-code-field"
            >
              <div className="text-xs text-slate-300 mb-1 inline-flex items-center gap-1"><Hash className="w-3.5 h-3.5" /> Código de acceso</div>
              <div className="text-2xl font-semibold tracking-wider">{accessCode || '----'}</div>
            </button>

            <button
              onClick={() => setActiveField('pin')}
              className={`text-left rounded-2xl border p-4 transition ${
                activeField === 'pin' ? 'border-indigo-300 bg-indigo-500/20' : 'border-white/10 bg-white/5 hover:bg-white/10'
              }`}
              data-testid="kiosco-pin-field"
            >
              <div className="text-xs text-slate-300 mb-1 inline-flex items-center gap-1"><LockKeyhole className="w-3.5 h-3.5" /> PIN</div>
              <div className="text-2xl font-semibold tracking-[0.35em]">{pin ? '•'.repeat(pin.length) : '----'}</div>
            </button>
          </div>

          <button
            onClick={submitPunch}
            disabled={busy}
            className="w-full rounded-2xl py-4 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 font-semibold text-slate-950 text-lg transition"
            data-testid="kiosco-submit"
          >
            {busy ? 'Registrando…' : 'Registrar entrada / salida'}
          </button>

          {(message || error) && (
            <div className={`mt-4 rounded-xl p-3 text-sm border ${error ? 'border-red-400/50 bg-red-500/15 text-red-100' : 'border-emerald-400/50 bg-emerald-500/15 text-emerald-100'}`} data-testid="kiosco-feedback">
              {error || message}
            </div>
          )}

          {result && (
            <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-100 flex items-center gap-2" data-testid="kiosco-last-result">
              {result.action === 'clock_in'
                ? <LogIn className="w-4 h-4 text-emerald-300" />
                : <LogOut className="w-4 h-4 text-amber-300" />}
              <span>
                <strong>{result.employee?.name}</strong> · {result.action === 'clock_in' ? 'Entrada' : 'Salida'} registrada
              </span>
            </div>
          )}
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm p-6 md:p-8">
          <div className="grid grid-cols-3 gap-3">
            {padDigits.map((digit) => (
              <button
                key={digit}
                onClick={() => applyDigit(digit)}
                className={`h-16 rounded-2xl text-2xl font-semibold transition ${
                  digit === 'C'
                    ? 'bg-rose-500/80 hover:bg-rose-500'
                    : digit === '←'
                      ? 'bg-slate-700 hover:bg-slate-600'
                      : 'bg-white/10 hover:bg-white/20'
                }`}
                data-testid={`kiosco-pad-${digit.replace('←', 'back').replace('C', 'clear')}`}
              >
                {digit}
              </button>
            ))}
          </div>

          <div className="mt-6 border border-white/10 rounded-2xl p-4 text-sm text-slate-300">
            <div className="flex items-center gap-2 mb-2 text-slate-100">
              <CheckCircle2 className="w-4 h-4 text-emerald-300" />
              Modo kiosco activo
            </div>
            <p>
              Introduce código de acceso + PIN del empleado y pulsa “Registrar entrada / salida”.
              El sistema alterna automáticamente entre entrada y salida según el estado actual.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KioscoPage;
