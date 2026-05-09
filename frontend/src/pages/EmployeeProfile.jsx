import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { asistenciaAPI } from '../services/api';
import EmployeeHorariosTab from './EmployeeHorariosTab';
import {
  ArrowLeft, Search, User, Briefcase, FileText, Calendar, Target,
  ClipboardList, Clock, CheckSquare, BarChart3, Settings, Shield,
  Users, GraduationCap, Map, Lock, Zap, Edit2, Save, X, ChevronDown
} from 'lucide-react';

// Mock employee data (ampliado con campos de perfil)
const mockEmployeesData = [
  {
    id: "1",
    name: "María García López",
    email: "maria@empresa.com",
    position: "Tech Lead",
    department: "Tecnología",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face",
    // Datos personales
    firstName: "María",
    lastName: "García",
    secondLastName: "López",
    primaryIdType: "DNI",
    secondaryIdType: "",
    nationality: "España",
    maritalStatus: "Casada",
    birthDate: "1990-05-15",
    gender: "Femenino",
    shareBirthday: true,
    address: "Calle Gran Vía 123",
    postalCode: "28013",
    colony: "Centro",
    municipality: "Madrid"
  },
  {
    id: "2",
    name: "Juan Rodríguez",
    email: "juan@empresa.com",
    position: "Senior Developer",
    department: "Desarrollo",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    firstName: "Juan",
    lastName: "Rodríguez",
    secondLastName: "Pérez",
    primaryIdType: "DNI",
    secondaryIdType: "",
    nationality: "España",
    maritalStatus: "Soltero",
    birthDate: "1995-08-22",
    gender: "Masculino",
    shareBirthday: true,
    address: "Avenida de América 456",
    postalCode: "28002",
    colony: "Salamanca",
    municipality: "Madrid"
  },
  {
    id: "3",
    name: "Laura Sánchez",
    email: "laura@empresa.com",
    position: "Sales Manager",
    department: "Ventas",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
    firstName: "Laura",
    lastName: "Sánchez",
    secondLastName: "Martín",
    primaryIdType: "DNI",
    secondaryIdType: "",
    nationality: "España",
    maritalStatus: "Casada",
    birthDate: "1988-03-10",
    gender: "Femenino",
    shareBirthday: false,
    address: "Calle Serrano 789",
    postalCode: "28006",
    colony: "Retiro",
    municipality: "Madrid"
  },
  {
    id: "4",
    name: "Carlos Mendoza",
    email: "carlos@empresa.com",
    position: "Developer",
    department: "Tecnología",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    firstName: "Carlos",
    lastName: "Mendoza",
    secondLastName: "García",
    primaryIdType: "DNI",
    secondaryIdType: "",
    nationality: "México",
    maritalStatus: "Soltero",
    birthDate: "1993-11-30",
    gender: "Masculino",
    shareBirthday: true,
    address: "Plaza Mayor 12",
    postalCode: "28012",
    colony: "Sol",
    municipality: "Madrid"
  },
  {
    id: "5",
    name: "Ana Martínez",
    email: "ana@empresa.com",
    position: "Junior Developer",
    department: "Tecnología",
    avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face",
    firstName: "Ana",
    lastName: "Martínez",
    secondLastName: "Ruiz",
    primaryIdType: "DNI",
    secondaryIdType: "",
    nationality: "España",
    maritalStatus: "Soltera",
    birthDate: "1997-07-18",
    gender: "Femenino",
    shareBirthday: true,
    address: "Calle Alcalá 234",
    postalCode: "28009",
    colony: "Retiro",
    municipality: "Madrid"
  }
];

// Mock data para fichajes
const mockFichajesData = {
  month: "Abril 2026",
  totalHours: "123h 59min",
  theoreticalHours: "160h",
  days: [
    { date: "Miércoles 1", hours: "7h 59min", theoretical: "8h 00min", segments: [{ type: "work", start: 9, duration: 8, color: "bg-teal-500" }] },
    { date: "Jueves 2", hours: "10h 00min", theoretical: "8h 00min", segments: [{ type: "work", start: 8, duration: 10, color: "bg-blue-500" }] },
    { date: "Viernes 3", hours: "9h 00min", theoretical: "8h 00min", segments: [
      { type: "work", start: 9, duration: 4, color: "bg-teal-500" },
      { type: "break", start: 13, duration: 1, color: "bg-orange-400" },
      { type: "work", start: 14, duration: 4, color: "bg-teal-500" }
    ]},
    { date: "Sábado 4", hours: "0h 00min", theoretical: "0h 00min", segments: [] },
    { date: "Domingo 5", hours: "0h 00min", theoretical: "0h 00min", segments: [] },
    { date: "Lunes 6", hours: "6h 00min", theoretical: "8h 00min", segments: [
      { type: "work", start: 10, duration: 4, color: "bg-teal-500" },
      { type: "break", start: 14, duration: 1, color: "bg-orange-400" },
      { type: "work", start: 15, duration: 1, color: "bg-teal-500" }
    ]},
    { date: "Martes 7", hours: "9h 00min", theoretical: "8h 00min", segments: [
      { type: "work", start: 8, duration: 4, color: "bg-teal-500" },
      { type: "break", start: 12, duration: 1, color: "bg-orange-400" },
      { type: "work", start: 13, duration: 4, color: "bg-blue-500" }
    ]},
    { date: "Miércoles 8", hours: "10h 00min", theoretical: "8h 00min", segments: [{ type: "work", start: 7, duration: 10, color: "bg-blue-500" }] },
    { date: "Jueves 9", hours: "9h 00min", theoretical: "8h 00min", segments: [
      { type: "work", start: 9, duration: 2, color: "bg-teal-500" },
      { type: "break", start: 11, duration: 1, color: "bg-orange-400" },
      { type: "work", start: 12, duration: 6, color: "bg-teal-500" }
    ]}
  ]
};

const EmployeeProfile = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  // Estado
  const [activeTab, setActiveTab] = useState('perfil');
  const [activeSidebarSection, setActiveSidebarSection] = useState('datos-personales');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [kioskAccess, setKioskAccess] = useState(null);
  const [kioskCodeDraft, setKioskCodeDraft] = useState('');
  const [kioskPinDraft, setKioskPinDraft] = useState('');
  const [kioskLoading, setKioskLoading] = useState(false);
  const [kioskBusy, setKioskBusy] = useState(false);
  const [registroPeriod, setRegistroPeriod] = useState('mensual');
  const [registros, setRegistros] = useState([]);
  const [registrosLoading, setRegistrosLoading] = useState(false);

  const [kioskError, setKioskError] = useState('');

  const [activeEvalTab, setActiveEvalTab] = useState('cuestionarios');

  // Obtener empleado actual
  const currentEmployee = mockEmployeesData.find(emp => emp.id === employeeId) || mockEmployeesData[0];
  
  // Estado del formulario
  const [formData, setFormData] = useState({
    firstName: currentEmployee.firstName,
    lastName: currentEmployee.lastName,
    secondLastName: currentEmployee.secondLastName,
    primaryIdType: currentEmployee.primaryIdType,
    secondaryIdType: currentEmployee.secondaryIdType,
    nationality: currentEmployee.nationality,
    maritalStatus: currentEmployee.maritalStatus,
    birthDate: currentEmployee.birthDate,
    gender: currentEmployee.gender,
    shareBirthday: currentEmployee.shareBirthday,
    address: currentEmployee.address,
    postalCode: currentEmployee.postalCode,
    colony: currentEmployee.colony,
    municipality: currentEmployee.municipality
  });

  // Actualizar formData cuando cambie el empleado
  useEffect(() => {
    setFormData({
      firstName: currentEmployee.firstName,
      lastName: currentEmployee.lastName,
      secondLastName: currentEmployee.secondLastName,
      primaryIdType: currentEmployee.primaryIdType,
      secondaryIdType: currentEmployee.secondaryIdType,
      nationality: currentEmployee.nationality,
      maritalStatus: currentEmployee.maritalStatus,
      birthDate: currentEmployee.birthDate,
      gender: currentEmployee.gender,
      shareBirthday: currentEmployee.shareBirthday,
      address: currentEmployee.address,
      postalCode: currentEmployee.postalCode,
      colony: currentEmployee.colony,
      municipality: currentEmployee.municipality,
    });
    setIsEditing(false);
  }, [employeeId]);

  const loadKioskAccess = async () => {
    setKioskLoading(true);
    setKioskError('');
    try {
      const data = await asistenciaAPI.getEmployeeKioskAccess(employeeId);
      setKioskAccess(data || null);
      setKioskCodeDraft((data?.access_code || '').replace(/\D/g, ''));
      setKioskPinDraft((data?.pin || '').replace(/\D/g, ''));
    } catch (e) {
      setKioskError(e.message);
    } finally {
      setKioskLoading(false);
    }
  };

  useEffect(() => {
    if (activeSidebarSection === 'accesos') {
      loadKioskAccess();
    }
  }, [activeSidebarSection, employeeId]);

  const saveKioskAccessChanges = async () => {
    const numericCode = kioskCodeDraft.replace(/\D/g, '');
    const numericPin = kioskPinDraft.replace(/\D/g, '');

    if (numericCode.length > 0 && numericCode.length < 4) {
      setKioskError('El código debe tener al menos 4 dígitos.');
      return;
    }

    if (numericPin.length > 0 && numericPin.length < 4) {
      setKioskError('El PIN debe tener al menos 4 dígitos.');
      return;
    }

    setKioskBusy(true);
    setKioskError('');
    try {
      let data;
      if (!numericCode && !kioskAccess) {
        data = await asistenciaAPI.generateEmployeeKioskAccess(employeeId, null);
      } else if (!kioskAccess) {
        data = await asistenciaAPI.generateEmployeeKioskAccess(employeeId, numericCode);
      } else {
        data = await asistenciaAPI.updateEmployeeKioskAccess(employeeId, numericCode || kioskAccess.access_code, numericPin || null);
      }

      if (!kioskAccess && numericPin) {
        data = await asistenciaAPI.updateEmployeeKioskAccess(employeeId, data.access_code, numericPin);
      }

      setKioskAccess(data);
      setKioskCodeDraft((data?.access_code || '').replace(/\D/g, ''));
      setKioskPinDraft((data?.pin || '').replace(/\D/g, ''));
    } catch (e) {
      setKioskError(e.message);
    } finally {
      setKioskBusy(false);
    }
  };

  const getRegistrosRange = () => {
    const now = new Date();
    if (registroPeriod === 'semanal') {
      const day = (now.getDay() + 6) % 7;
      const from = new Date(now);
      from.setDate(now.getDate() - day);
      const to = new Date(from);
      to.setDate(from.getDate() + 6);
      return { from, to };
    }
    const from = new Date(now.getFullYear(), now.getMonth(), 1);
    const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    return { from, to };
  };

  const loadRegistros = async () => {
    setRegistrosLoading(true);
    try {
      const { from, to } = getRegistrosRange();
      const pad = (n) => String(n).padStart(2, '0');
      const toISO = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
      const data = await asistenciaAPI.records({
        employeeId,
        dateFrom: toISO(from),
        dateTo: toISO(to),
      });
      setRegistros(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error('Error cargando registros:', e);
      setRegistros([]);
    } finally {
      setRegistrosLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'fichajes') {
      loadRegistros();
    }
  }, [activeTab, registroPeriod, employeeId]);

  // Filtrar empleados para búsqueda
  const filteredEmployees = mockEmployeesData.filter(emp => 
    emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Tabs principales
  const mainTabs = [
    { id: 'perfil', label: 'Perfil', icon: User },
    { id: 'fichajes', label: 'Registros', icon: Clock },
    { id: 'ausencias', label: 'Ausencias y vacaciones', icon: Calendar },
    { id: 'estadisticas', label: 'Estadísticas', icon: BarChart3 },
    { id: 'contratos', label: 'Contratos', icon: FileText },
    { id: 'documentos', label: 'Documentos', icon: FileText },
    { id: 'horarios', label: 'Horarios', icon: Clock },
    { id: 'tareas', label: 'Tareas', icon: CheckSquare },
    { id: 'evaluaciones', label: 'Evaluaciones', icon: Target }
  ];

  // Secciones del sidebar (solo para tab Perfil)
  const sidebarSections = [
    { id: 'datos-personales', label: 'Datos personales', icon: User },
    { id: 'datos-laborales', label: 'Datos laborales', icon: Briefcase },
    { id: 'datos-nomina', label: 'Datos nómina', icon: FileText },
    { id: 'campos-personalizados', label: 'Campos personalizados', icon: Settings },
    { id: 'formacion', label: 'Formación y habilidades', icon: GraduationCap },
    { id: 'journey', label: 'Journey', icon: Map },
    { id: 'accesos', label: 'Accesos', icon: Lock },
    { id: 'roles', label: 'Roles', icon: Shield },
    { id: 'automatizaciones', label: 'Automatizaciones', icon: Zap }
  ];

  const handleSaveChanges = () => {
    // Aquí iría la lógica para guardar en BD (por ahora solo mock)
    console.log('Guardando cambios:', formData);
    setIsEditing(false);
    // Mostrar notificación de éxito
    alert('Cambios guardados correctamente (MOCK)');
  };

  const handleCancelEdit = () => {
    // Restaurar datos originales
    setFormData({
      firstName: currentEmployee.firstName,
      lastName: currentEmployee.lastName,
      secondLastName: currentEmployee.secondLastName,
      primaryIdType: currentEmployee.primaryIdType,
      secondaryIdType: currentEmployee.secondaryIdType,
      nationality: currentEmployee.nationality,
      maritalStatus: currentEmployee.maritalStatus,
      birthDate: currentEmployee.birthDate,
      gender: currentEmployee.gender,
      shareBirthday: currentEmployee.shareBirthday,
      address: currentEmployee.address,
      postalCode: currentEmployee.postalCode,
      colony: currentEmployee.colony,
      municipality: currentEmployee.municipality
    });
    setIsEditing(false);
  };

  // Renderizar contenido del tab activo
  const renderTabContent = () => {
    switch (activeTab) {
      case 'perfil':
        return renderPerfilContent();
      case 'fichajes':
        return renderFichajesContent();
      case 'evaluaciones':
        return renderEvaluacionesContent();
      case 'horarios':
        return <EmployeeHorariosTab employeeId={employeeId} isAdmin={isAdmin} />;
      default:
        return renderUnderConstructionContent();
    }
  };

  // Contenido de Perfil
  const renderPerfilContent = () => {
    if (activeSidebarSection === 'datos-personales') {
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Información personal</h2>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-slate-900 text-white rounded-lg hover:bg-slate-800"
              >
                <Edit2 className="w-4 h-4" />
                Editar
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleCancelEdit}
                  className="flex items-center gap-2 px-4 py-2 text-sm border border-slate-200 rounded-lg hover:bg-slate-50"
                >
                  <X className="w-4 h-4" />
                  Cancelar
                </button>
                <button
                  onClick={handleSaveChanges}
                  className="flex items-center gap-2 px-4 py-2 text-sm bg-slate-900 text-white rounded-lg hover:bg-slate-800"
                >
                  <Save className="w-4 h-4" />
                  Guardar cambios
                </button>
              </div>
            )}
          </div>

          {/* Formulario */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Nombre *
              </label>
              <input
                type="text"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Apellido materno
              </label>
              <input
                type="text"
                value={formData.secondLastName}
                onChange={(e) => setFormData({ ...formData, secondLastName: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Apellido paterno *
              </label>
              <input
                type="text"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
            </div>

            <div className="invisible"></div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Tipo de identificación principal
              </label>
              <select
                value={formData.primaryIdType}
                onChange={(e) => setFormData({ ...formData, primaryIdType: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              >
                <option value="">Selecciona una opción</option>
                <option value="DNI">DNI</option>
                <option value="NIE">NIE</option>
                <option value="Pasaporte">Pasaporte</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Tipo de identificación secundaria
              </label>
              <select
                value={formData.secondaryIdType}
                onChange={(e) => setFormData({ ...formData, secondaryIdType: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              >
                <option value="">Selecciona una opción</option>
                <option value="DNI">DNI</option>
                <option value="NIE">NIE</option>
                <option value="Pasaporte">Pasaporte</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Nacionalidad
              </label>
              <select
                value={formData.nationality}
                onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              >
                <option value="España">España</option>
                <option value="México">México</option>
                <option value="Argentina">Argentina</option>
                <option value="Colombia">Colombia</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Estado civil
              </label>
              <select
                value={formData.maritalStatus}
                onChange={(e) => setFormData({ ...formData, maritalStatus: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              >
                <option value="">Selecciona una opción</option>
                <option value="Soltero">Soltero/a</option>
                <option value="Casado">Casado/a</option>
                <option value="Divorciado">Divorciado/a</option>
                <option value="Viudo">Viudo/a</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Fecha de nacimiento
              </label>
              <input
                type="date"
                value={formData.birthDate}
                onChange={(e) => setFormData({ ...formData, birthDate: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Género
              </label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                disabled={!isEditing}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
              >
                <option value="">Selecciona una opción</option>
                <option value="Masculino">Masculino</option>
                <option value="Femenino">Femenino</option>
                <option value="Otro">Otro</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.shareBirthday}
                  onChange={(e) => setFormData({ ...formData, shareBirthday: e.target.checked })}
                  disabled={!isEditing}
                  className="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900 disabled:opacity-50"
                />
                <span className="text-sm text-slate-700">Compartir cumpleaños</span>
              </label>
            </div>
          </div>

          {/* Dirección */}
          <div>
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Dirección</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Domicilio
                </label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
                  placeholder="C. de Primitivo Gallo 983"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Código postal
                </label>
                <input
                  type="text"
                  value={formData.postalCode}
                  onChange={(e) => setFormData({ ...formData, postalCode: e.target.value })}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Colonia
                </label>
                <input
                  type="text"
                  value={formData.colony}
                  onChange={(e) => setFormData({ ...formData, colony: e.target.value })}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Alcaldía / Municipio
                </label>
                <input
                  type="text"
                  value={formData.municipality}
                  onChange={(e) => setFormData({ ...formData, municipality: e.target.value })}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-500"
                />
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (activeSidebarSection === 'accesos') {
      return (
        <div className="space-y-6" data-testid="perfil-accesos-section">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">Accesos de kiosco</h2>
              <p className="text-sm text-slate-500 mt-1">
                Usa este código y PIN para registrar entrada/salida en la vista de kiosco.
              </p>
            </div>
            <button
              onClick={loadKioskAccess}
              className="px-3 py-2 text-sm border border-slate-200 rounded-lg hover:bg-slate-50"
              disabled={kioskLoading || kioskBusy}
            >
              Actualizar
            </button>
          </div>

          {kioskError && (
            <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {kioskError}
            </div>
          )}

          {kioskLoading ? (
            <div className="py-8 text-center text-slate-400">Cargando accesos…</div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Código de acceso (numérico)</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={kioskCodeDraft}
                    onChange={(e) => setKioskCodeDraft(e.target.value.replace(/\D/g, '').slice(0, 12))}
                    readOnly={!isAdmin}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-white disabled:bg-slate-50"
                    placeholder="Ej: 123456"
                    data-testid="profile-kiosk-code"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">PIN</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={kioskPinDraft}
                    onChange={(e) => setKioskPinDraft(e.target.value.replace(/\D/g, '').slice(0, 8))}
                    readOnly={!isAdmin}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-white tracking-[0.3em] font-semibold"
                    placeholder={kioskAccess ? '' : 'Auto-generado al guardar'}
                    data-testid="profile-kiosk-pin"
                  />
                </div>
              </div>

              {!kioskAccess && (
                <div className="text-sm text-slate-500">
                  Aún no hay credenciales creadas para este empleado.
                </div>
              )}

              {isAdmin ? (
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={saveKioskAccessChanges}
                    disabled={kioskBusy}
                    className="px-4 py-2 text-sm bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-60"
                    data-testid="profile-kiosk-save-all"
                  >
                    Guardar cambios
                  </button>
                </div>
              ) : (
                <div className="text-sm text-slate-500">
                  Solo el administrador puede editar estas credenciales.
                </div>
              )}
            </div>
          )}
        </div>
      );
    }
    
    return renderUnderConstructionContent();
  };

  // Contenido de Registros
  const renderFichajesContent = () => {
    const { from, to } = getRegistrosRange();
    const formatDate = (d) => d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const formatTime = (iso) => (iso ? new Date(iso).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }) : '--:--');
    const formatHours = (secs) => {
      const total = Math.max(0, Math.floor((secs || 0) / 60));
      const h = Math.floor(total / 60);
      const m = total % 60;
      return `${String(h).padStart(2, '0')}h ${String(m).padStart(2, '0')}m`;
    };

    const totalWorked = registros.reduce((acc, r) => acc + (r.duration_seconds || r.seconds_elapsed || 0), 0);

    return (
      <div className="space-y-6" data-testid="registros-tab">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <div className="text-sm text-slate-600 mb-1">Total trabajado</div>
            <div className="text-2xl font-bold text-slate-900">{formatHours(totalWorked)}</div>
            <div className="text-xs text-slate-500 mt-1">Rango: {formatDate(from)} - {formatDate(to)}</div>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={registroPeriod}
              onChange={(e) => setRegistroPeriod(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm"
              data-testid="registros-period-select"
            >
              <option value="mensual">Mensual</option>
              <option value="semanal">Semanal</option>
            </select>
            <button
              onClick={loadRegistros}
              className="px-4 py-2 border border-slate-200 rounded-lg text-sm hover:bg-slate-50"
            >
              Actualizar
            </button>
          </div>
        </div>

        {registrosLoading ? (
          <div className="py-10 text-center text-slate-400">Cargando registros…</div>
        ) : registros.length === 0 ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-xl">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Sin registros en este periodo</h3>
            <p className="text-sm text-slate-500">Cuando existan entradas/salidas aparecerán aquí.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {registros
              .slice()
              .sort((a, b) => String(b.clock_in || '').localeCompare(String(a.clock_in || '')))
              .map((row) => {
                const worked = row.duration_seconds || row.seconds_elapsed || 0;
                return (
                  <div key={row.id} className="bg-white border border-slate-200 rounded-xl p-4" data-testid={`registro-${row.id}`}>
                    <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
                      <div>
                        <div className="font-semibold text-slate-900">{row.date}</div>
                        <div className="text-xs text-slate-500">{row.schedule_name || 'Sin horario'}</div>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full border ${row.status === 'closed' ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : 'text-amber-700 bg-amber-50 border-amber-200'}`}>
                        {row.status === 'closed' ? 'Cerrado' : 'En curso'}
                      </span>
                    </div>

                    <div className="grid md:grid-cols-3 gap-2 text-sm">
                      <div className="rounded-lg px-3 py-2 bg-blue-50 border border-blue-200 text-blue-800">
                        <div className="text-xs uppercase tracking-wide text-blue-700">Entrada</div>
                        <div className="font-semibold">{formatTime(row.clock_in)}</div>
                      </div>
                      <div className="rounded-lg px-3 py-2 bg-violet-50 border border-violet-200 text-violet-800">
                        <div className="text-xs uppercase tracking-wide text-violet-700">Salida</div>
                        <div className="font-semibold">{formatTime(row.clock_out)}</div>
                      </div>
                      <div className="rounded-lg px-3 py-2 bg-emerald-50 border border-emerald-200 text-emerald-800">
                        <div className="text-xs uppercase tracking-wide text-emerald-700">Horas laboradas</div>
                        <div className="font-semibold">{formatHours(worked)}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        )}
      </div>
    );
  };

  // Contenido de Evaluaciones
  const renderEvaluacionesContent = () => {
    return (
      <div className="space-y-6">
        {/* Sub-tabs */}
        <div className="flex gap-4 border-b border-slate-200">
          <button
            onClick={() => setActiveEvalTab('cuestionarios')}
            className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
              activeEvalTab === 'cuestionarios'
                ? 'text-blue-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Cuestionarios respondidos
            {activeEvalTab === 'cuestionarios' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"></div>
            )}
          </button>
          <button
            onClick={() => setActiveEvalTab('resultados')}
            className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
              activeEvalTab === 'resultados'
                ? 'text-blue-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Resultados sobre mí
            {activeEvalTab === 'resultados' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"></div>
            )}
          </button>
        </div>

        {/* Filtros */}
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg">
            <span className="text-sm text-slate-600">01/01/2026 - 24/04/2026</span>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar"
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm"
            />
          </div>
        </div>

        {/* Estado vacío */}
        <div className="text-center py-16">
          <div className="mb-6">
            <svg className="mx-auto" width="120" height="120" viewBox="0 0 120 120" fill="none">
              <circle cx="60" cy="60" r="40" fill="#10B981" opacity="0.1"/>
              <rect x="55" y="30" width="10" height="40" rx="5" fill="#10B981"/>
              <circle cx="60" cy="75" r="5" fill="#10B981"/>
              <circle cx="30" cy="40" r="8" fill="#3B82F6" opacity="0.3"/>
              <circle cx="90" cy="50" r="6" fill="#8B5CF6" opacity="0.3"/>
              <path d="M40 90 L50 85 L45 95 Z" fill="#F59E0B" opacity="0.3"/>
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            Todavía no hay ningún cuestionario
          </h3>
          <p className="text-sm text-slate-500">
            Aquí puedes ver todos los cuestionarios que ha recibido tu empleado
          </p>
        </div>
      </div>
    );
  };

  // Contenido "En construcción"
  const renderUnderConstructionContent = () => {
    return (
      <div className="text-center py-20">
        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Settings className="w-8 h-8 text-slate-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-900 mb-2">En construcción</h3>
        <p className="text-sm text-slate-500">Esta sección estará disponible próximamente</p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-slate-600" />
              </button>
              <img
                src={currentEmployee.avatar}
                alt={currentEmployee.name}
                className="w-12 h-12 rounded-full object-cover"
              />
              <div>
                <h1 className="text-lg font-semibold text-slate-900">{currentEmployee.name}</h1>
                <p className="text-sm text-slate-500">{currentEmployee.position} - {currentEmployee.department}</p>
              </div>
            </div>

            {/* Buscador (solo para admin) */}
            {isAdmin && (
              <div className="relative">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Buscar empleado"
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      setIsSearchOpen(e.target.value.length > 0);
                    }}
                    onFocus={() => setIsSearchOpen(searchTerm.length > 0)}
                    className="w-80 pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                  />
                </div>

                {/* Dropdown de resultados */}
                {isSearchOpen && filteredEmployees.length > 0 && (
                  <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-lg shadow-lg max-h-96 overflow-y-auto z-50">
                    {filteredEmployees.map((emp) => (
                      <button
                        key={emp.id}
                        onClick={() => {
                          navigate(`/perfil/${emp.id}`);
                          setSearchTerm('');
                          setIsSearchOpen(false);
                        }}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 transition-colors text-left"
                      >
                        <img
                          src={emp.avatar}
                          alt={emp.name}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                        <div className="flex-1">
                          <div className="text-sm font-medium text-slate-900">{emp.name}</div>
                          <div className="text-xs text-slate-500">{emp.position}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Tabs principales */}
        <div className="container mx-auto px-8">
          <div className="flex gap-4 justify-start flex-wrap">
            {mainTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  if (tab.id === 'perfil') setActiveSidebarSection('datos-personales');
                }}
                className={`flex items-center gap-2 px-2 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="container mx-auto px-8 py-6">
        <div className="flex gap-6">
          {/* Sidebar (solo visible en tab Perfil) */}
          {activeTab === 'perfil' && (
            <div className="w-64 flex-shrink-0 space-y-4">
              {/* Foto y nombre del empleado */}
              <div className="flex flex-col items-center text-center">
                <div className="relative mb-4">
                  <img
                    src={currentEmployee.avatar}
                    alt={currentEmployee.name}
                    className="w-56 h-56 rounded-full object-cover border-4 border-white shadow-xl"
                  />
                  <button className="absolute bottom-2 right-2 w-12 h-12 bg-slate-900 text-white rounded-full flex items-center justify-center hover:bg-slate-800 transition-colors shadow-lg">
                    <Edit2 className="w-5 h-5" />
                  </button>
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-1">
                  {currentEmployee.name}
                </h3>
                <p className="text-sm text-slate-500 mb-4">
                  {currentEmployee.position}
                </p>
              </div>

              {/* Menú de secciones */}
              <div className="bg-white border border-slate-200 rounded-xl p-3 space-y-1">
                {sidebarSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSidebarSection(section.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${
                      activeSidebarSection === section.id
                        ? 'bg-slate-100 text-slate-900 font-medium'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                  >
                    <section.icon className="w-4 h-4" />
                    {section.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Contenido principal */}
          <div className="flex-1">
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>

      {/* Overlay para cerrar dropdown al hacer click fuera */}
      {isSearchOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsSearchOpen(false)}
        />
      )}
    </div>
  );
};

export default EmployeeProfile;
