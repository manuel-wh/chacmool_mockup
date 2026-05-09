import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Plus, Search, MoreVertical, Trash2, Edit2, ChevronDown,
  Calendar, Smartphone, MapPin, QrCode, Camera, Hash, ScanFace, Fingerprint, Copy, ExternalLink,
} from 'lucide-react';
import { asistenciaAPI } from '../services/api';
import { DAY_SHORT, MONTH_LABELS, minutesToHHMM, computeWeeklyHours } from '../utils/asistencia';
import HorarioEditor from './HorarioEditor';

/**
 * Vista de Configuración (admin): pestañas tipo Sesame
 *  - Horarios (jornadas)
 *  - Dispositivos
 *  (Otras tabs como Empresa/Calendarios/Automatizaciones/Plan -> placeholder)
 */
const AsistenciaConfig = () => {
  const navigate = useNavigate();
  const [tab, setTab] = useState('horarios');

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto" data-testid="asistencia-config">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate('/asistencia')}
          className="p-2 rounded-lg hover:bg-slate-100 text-slate-600"
          data-testid="back-btn"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-3xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>
          Configuración
        </h1>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
        {/* Tabs */}
        <div className="border-b border-slate-200 px-6 flex gap-1 overflow-x-auto">
          {[
            { id: 'empresa', label: 'Empresa' },
            { id: 'horarios', label: 'Horarios' },
            { id: 'calendarios', label: 'Calendarios' },
            { id: 'automatizaciones', label: 'Automatizaciones' },
            { id: 'dispositivos', label: 'Dispositivos' },
            { id: 'plan', label: 'Plan' },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              data-testid={`tab-${t.id}`}
              className={`px-4 py-3.5 text-sm font-medium whitespace-nowrap transition border-b-2 -mb-px ${
                tab === t.id
                  ? 'text-indigo-600 border-indigo-500'
                  : 'text-slate-500 border-transparent hover:text-slate-900'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Contenido */}
        <div className="p-6">
          {tab === 'horarios' && <HorariosTab />}
          {tab === 'dispositivos' && <DispositivosTab />}
          {tab !== 'horarios' && tab !== 'dispositivos' && (
            <div className="py-16 text-center text-slate-400">
              <Calendar className="w-12 h-12 mx-auto mb-3 text-slate-200" />
              Sección "{tab}" próximamente.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ============== HORARIOS TAB ==============

const HorariosTab = () => {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showEditor, setShowEditor] = useState(false);
  const [editing, setEditing] = useState(null);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const list = await asistenciaAPI.listSchedules();
      setItems(list || []);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchItems(); }, [fetchItems]);

  const handleSave = async (data) => {
    try {
      if (editing?.id) await asistenciaAPI.updateSchedule(editing.id, data);
      else await asistenciaAPI.createSchedule(data);
      setShowEditor(false);
      setEditing(null);
      await fetchItems();
    } catch (e) {
      alert(e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este horario? Los empleados asignados quedarán sin horario.')) return;
    try {
      await asistenciaAPI.deleteSchedule(id);
      await fetchItems();
    } catch (e) {
      alert(e.message);
    }
  };

  const filtered = items.filter((s) => s.name.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div data-testid="horarios-tab">
      <p className="text-sm text-slate-600 mb-5">
        Crea las distintas jornadas laborales para poder asignarlas a los usuarios. Podrás crear tantos horarios como necesites.
      </p>

      <div className="flex items-center justify-between gap-3 mb-5 flex-wrap">
        <div className="flex-1 max-w-sm relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filtrar"
            className="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-full text-sm bg-slate-50/50"
            data-testid="filter-horarios"
          />
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="bg-slate-900 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-slate-800 inline-flex items-center gap-2"
          data-testid="add-horario-btn"
        >
          <Plus className="w-4 h-4" /> Añadir jornada
        </button>
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-xs text-slate-500 uppercase tracking-wide">
            <tr className="border-b border-slate-100">
              <th className="text-left py-3 font-medium">Nombre del horario</th>
              <th className="text-left py-3 font-medium">Horas semanales</th>
              <th className="text-left py-3 font-medium">Días semanales</th>
              <th className="text-left py-3 font-medium">Resumen de las jornadas</th>
              <th className="text-left py-3 font-medium">Descansos</th>
              <th className="text-left py-3 font-medium">Tipo</th>
              <th className="text-left py-3 font-medium">Creada el</th>
              <th className="w-12"></th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={8} className="py-10 text-center text-slate-400">Cargando…</td></tr>
            )}
            {!loading && filtered.length === 0 && (
              <tr><td colSpan={8} className="py-10 text-center text-slate-400">Sin horarios. Crea el primero.</td></tr>
            )}
            {filtered.map((s) => (
              <ScheduleRow key={s.id} s={s} onEdit={() => { setEditing(s); setShowEditor(true); }} onDelete={() => handleDelete(s.id)} />
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal: elegir tipo */}
      {showCreate && (
        <CreateScheduleTypeModal
          onClose={() => setShowCreate(false)}
          onPick={({ type, template_kind }) => {
            setShowCreate(false);
            setEditing({ name: '', type, days: null, template_kind });
            setShowEditor(true);
          }}
        />
      )}

      {/* Editor */}
      {showEditor && (
        <HorarioEditor
          initial={editing && editing.id ? editing : (editing && !editing.id ? { name: editing.name, type: editing.type, days: null, template_kind: editing.template_kind } : null)}
          onCancel={() => { setShowEditor(false); setEditing(null); }}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

const ScheduleRow = ({ s, onEdit, onDelete }) => {
  const [open, setOpen] = useState(false);
  const [menu, setMenu] = useState(false);
  const dateStr = s.created_at ? new Date(s.created_at).toISOString().slice(0, 10) : '—';

  return (
    <>
      <tr className="border-b border-slate-100 hover:bg-slate-50/40" data-testid={`row-${s.id}`}>
        <td className="py-4 font-semibold text-slate-900">
          <button onClick={() => setOpen((o) => !o)} className="inline-flex items-center gap-2">
            <ChevronDown className={`w-4 h-4 transition ${open ? 'rotate-180' : ''}`} />
            {s.name}
          </button>
        </td>
        <td className="py-4 text-slate-700">{minutesToHHMM(s.weekly_hours * 60)}</td>
        <td className="py-4 text-slate-700">{s.weekly_days} días</td>
        <td className="py-4">
          <div className="flex gap-1">
            {DAY_SHORT.map((d, i) => (
              <span
                key={i}
                className={`w-6 h-6 rounded-full text-[10px] font-semibold flex items-center justify-center ${
                  (s.days?.[i]?.enabled) ? 'bg-indigo-600 text-white' : 'bg-indigo-50 text-indigo-300'
                }`}
              >
                {d}
              </span>
            ))}
          </div>
        </td>
        <td className="py-4 text-slate-700">{s.breaks_count}</td>
        <td className="py-4 text-slate-700 capitalize">Horario {s.type}</td>
        <td className="py-4 text-slate-500">{dateStr}</td>
        <td className="py-4 relative">
          <button
            onClick={() => setMenu((m) => !m)}
            className="p-1.5 hover:bg-slate-100 rounded-lg"
            data-testid={`menu-${s.id}`}
          >
            <MoreVertical className="w-4 h-4" />
          </button>
          {menu && (
            <div className="absolute right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-10 min-w-[140px] overflow-hidden">
              <button
                onClick={() => { setMenu(false); onEdit(); }}
                className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 inline-flex items-center gap-2"
                data-testid={`edit-${s.id}`}
              >
                <Edit2 className="w-3.5 h-3.5" /> Editar
              </button>
              <button
                onClick={() => { setMenu(false); onDelete(); }}
                className="w-full text-left px-3 py-2 text-sm hover:bg-red-50 text-red-600 inline-flex items-center gap-2"
                data-testid={`delete-${s.id}`}
              >
                <Trash2 className="w-3.5 h-3.5" /> Eliminar
              </button>
            </div>
          )}
        </td>
      </tr>
      {open && (
        <tr className="bg-slate-50/40">
          <td colSpan={8} className="px-6 py-3 text-sm text-slate-600">
            <div className="space-y-1">
              {(s.days || []).filter(d => d.enabled).map((d) => (
                <div key={d.day} className="flex gap-3">
                  <span className="font-semibold text-slate-800 w-24">{['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'][d.day]}</span>
                  <span>{(d.ranges || []).map(r => `${r.start}–${r.end}`).join(', ')}</span>
                </div>
              ))}
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

const CreateScheduleTypeModal = ({ onClose, onPick }) => (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="create-type-modal">
    <div className="bg-white rounded-2xl w-full max-w-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <h3 className="text-xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>
          Crear nueva jornada
        </h3>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl">×</button>
      </div>
      <div className="divide-y divide-slate-100">
        <button
          onClick={() => onPick({ type: 'fijo', template_kind: 'jornada_continua' })}
          className="w-full text-left p-6 hover:bg-slate-50 transition"
          data-testid="pick-jornada-continua"
        >
          <h4 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit' }}>Jornada continua</h4>
          <p className="text-sm text-slate-600 mb-1">Una sola franja de trabajo continua para cada día laboral activo.</p>
          <p className="text-xs text-slate-400">Ejemplo: de 09:00 a 18:00</p>
        </button>
        <button
          onClick={() => onPick({ type: 'fijo', template_kind: 'jornada_partida' })}
          className="w-full text-left p-6 hover:bg-slate-50 transition"
          data-testid="pick-jornada-partida"
        >
          <h4 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit' }}>Jornada partida</h4>
          <p className="text-sm text-slate-600 mb-1">Dos franjas de trabajo separadas por una pausa en medio.</p>
          <p className="text-xs text-slate-400">Ejemplo: 09:00-13:00 y 14:00-18:00</p>
        </button>
      </div>
    </div>
  </div>
);

// ============== DISPOSITIVOS TAB ==============

const DispositivosTab = () => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copyOk, setCopyOk] = useState(false);

  const kioskUrl = `${window.location.origin}/kiosco`;

  const fetchConfig = useCallback(async () => {
    setLoading(true);
    try {
      const c = await asistenciaAPI.getDevices();
      setConfig(c);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchConfig(); }, [fetchConfig]);

  const toggle = async (key) => {
    if (key === 'panel_web_enabled') {
      return;
    }
    try {
      const updated = await asistenciaAPI.updateDevices({ [key]: !config[key] });
      setConfig(updated);
    } catch (e) {
      alert(e.message);
    }
  };

  const copyUrl = async () => {
    try {
      await navigator.clipboard.writeText(kioskUrl);
      setCopyOk(true);
      setTimeout(() => setCopyOk(false), 1800);
    } catch (e) {
      alert('No se pudo copiar la URL.');
    }
  };

  if (loading || !config) return <div className="py-10 text-center text-slate-400">Cargando…</div>;

  return (
    <div data-testid="dispositivos-tab">
      <p className="text-sm text-slate-600 mb-6">
        Elige los dispositivos desde los que tus empleados podrán registrar su jornada laboral.
      </p>

      <div className="grid lg:grid-cols-3 gap-4 mb-4">
        <DeviceCard
          title="Panel web"
          description="Permite a los empleados registrarse desde cualquier navegador."
          enabled={config.panel_web_enabled}
          onToggle={() => toggle('panel_web_enabled')}
          icons={[<MapPin key="m" className="w-5 h-5" />]}
          footer="Ir al panel web"
          locked
          testId="card-panel-web"
        />
        <DeviceCard
          title="Celular"
          description="Permite a los empleados realizar sus registros desde la app móvil."
          enabled={config.mobile_enabled}
          onToggle={() => toggle('mobile_enabled')}
          icons={[<MapPin key="m" className="w-5 h-5" />, <QrCode key="q" className="w-5 h-5" />]}
          footer="App Store · Google Play"
          comingSoon
          testId="card-celular"
        />
        <DeviceCard
          title="Kiosco"
          description="Habilita un punto fijo de fichaje con código + PIN para tablet o teléfono."
          enabled={config.kiosco_enabled}
          onToggle={() => toggle('kiosco_enabled')}
          icons={[<QrCode key="q" className="w-5 h-5" />, <Camera key="c" className="w-5 h-5" />, <Hash key="h" className="w-5 h-5" />, <ScanFace key="s" className="w-5 h-5" />]}
          footer="URL de kiosco"
          testId="card-kiosco"
        />
      </div>

      {config.kiosco_enabled && (
        <div className="border border-emerald-200 bg-emerald-50 rounded-2xl p-5 mb-4" data-testid="kiosk-url-box">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
            <h4 className="font-semibold text-emerald-900" style={{ fontFamily: 'Outfit' }}>Kiosco habilitado</h4>
            <a
              href={kioskUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs text-emerald-700 hover:text-emerald-800"
            >
              Abrir kiosco <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
          <p className="text-sm text-emerald-900 mb-3">
            Deja esta URL abierta en una tablet o teléfono para fichar con código de acceso y PIN.
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <code className="px-3 py-2 rounded-lg bg-white border border-emerald-200 text-sm text-emerald-900" data-testid="kiosk-url-value">
              {kioskUrl}
            </code>
            <button
              onClick={copyUrl}
              className="inline-flex items-center gap-1 px-3 py-2 text-sm rounded-lg border border-emerald-200 bg-white text-emerald-800 hover:bg-emerald-100"
              data-testid="copy-kiosk-url"
            >
              <Copy className="w-4 h-4" /> {copyOk ? 'Copiada' : 'Copiar URL'}
            </button>
          </div>
        </div>
      )}

      <div className="border border-slate-200 rounded-2xl p-6 max-w-md">
        <div className="flex items-center gap-2 mb-2">
          <Fingerprint className="w-5 h-5 text-slate-700" />
          <h4 className="font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>Registro Biométrico</h4>
        </div>
        <p className="text-sm text-slate-600">
          Vincula dispositivos de control horario tradicional. Reconocimiento facial, huella, tarjetas, etc.
          <span className="text-slate-400 ml-1">(próximamente)</span>
        </p>
      </div>
    </div>
  );
};

const DeviceCard = ({ title, description, enabled, onToggle, icons, footer, locked, comingSoon, testId }) => (
  <div className="border border-slate-200 rounded-2xl p-5 flex flex-col" data-testid={testId}>
    <div className="flex items-center gap-3 mb-3">
      <button
        onClick={onToggle}
        disabled={locked}
        className={`relative w-11 h-6 rounded-full transition ${
          enabled ? 'bg-emerald-500' : 'bg-slate-200'
        } ${locked ? 'cursor-not-allowed opacity-90' : ''}`}
      >
        <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition ${enabled ? 'left-5' : 'left-0.5'}`} />
      </button>
      <h3 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Outfit' }}>{title}</h3>
      {comingSoon && <span className="text-[10px] text-amber-600 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full uppercase tracking-wide ml-auto">Próximamente</span>}
    </div>
    <p className="text-sm text-slate-600 flex-1 leading-relaxed">{description}</p>
    <div className="flex justify-center gap-2 my-6 text-indigo-300">
      {icons.map((ic, i) => (
        <div key={i} className="w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-400">{ic}</div>
      ))}
    </div>
    <div className="text-xs text-indigo-500 text-center border-t border-slate-100 pt-3 font-medium">
      {footer}
    </div>
  </div>
);

export default AsistenciaConfig;
