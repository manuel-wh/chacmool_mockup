/* Helpers compartidos del módulo Asistencia */

export const DAY_LABELS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
export const DAY_SHORT = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];
export const MONTH_LABELS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
export const MONTH_SHORT = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

export const pad2 = (n) => String(n).padStart(2, '0');

export const minutesToHHMM = (mins) => {
  const m = Math.max(0, Math.round(mins));
  return `${pad2(Math.floor(m / 60))}:${pad2(m % 60)}`;
};

export const hhmmToMinutes = (s) => {
  if (!s) return 0;
  const [h, m] = s.split(':').map(Number);
  return (h || 0) * 60 + (m || 0);
};

export const secondsToHM = (s) => {
  const sec = Math.max(0, Math.round(s));
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  return `${h}h ${pad2(m)}min`;
};

export const secondsToHMS = (s) => {
  const sec = Math.max(0, Math.round(s));
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const ss = sec % 60;
  return `${pad2(h)}:${pad2(m)}:${pad2(ss)}`;
};

/** Formatea una fecha JS Date como YYYY-MM-DD usando hora local */
export const toISODate = (d) => `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;

/** Convierte JS getDay (0=Dom..6=Sáb) a nuestro estándar (0=Lun..6=Dom) */
export const isoWeekday = (d) => (d.getDay() + 6) % 7;

/** Devuelve el lunes (00:00) de la semana de la fecha dada */
export const startOfWeek = (d) => {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  x.setDate(x.getDate() - isoWeekday(x));
  return x;
};

export const addDays = (d, n) => {
  const x = new Date(d);
  x.setDate(x.getDate() + n);
  return x;
};

export const formatRangeShort = (from, to) => {
  const f = new Date(from);
  const t = new Date(to);
  return `${pad2(f.getDate())}/${pad2(f.getMonth() + 1)}/${f.getFullYear()} - ${pad2(t.getDate())}/${pad2(t.getMonth() + 1)}/${t.getFullYear()}`;
};

/** Plantilla por defecto: jornada continua L-V 09:00-18:00 */
export const TEMPLATE_JORNADA_CONTINUA = () =>
  Array.from({ length: 7 }, (_, i) => ({
    day: i,
    enabled: i < 5,
    ranges: i < 5 ? [{ start: '09:00', end: '18:00' }] : [],
  }));

/** Plantilla jornada partida L-V 09:00-13:00 + 14:00-18:00 */
export const TEMPLATE_JORNADA_PARTIDA = () =>
  Array.from({ length: 7 }, (_, i) => ({
    day: i,
    enabled: i < 5,
    ranges: i < 5
      ? [{ start: '09:00', end: '13:00' }, { start: '14:00', end: '18:00' }]
      : [],
  }));

export const computeWeeklyHours = (days) =>
  days.reduce((acc, d) => {
    if (!d.enabled) return acc;
    return acc + d.ranges.reduce((s, r) => s + (hhmmToMinutes(r.end) - hhmmToMinutes(r.start)), 0) / 60;
  }, 0);
