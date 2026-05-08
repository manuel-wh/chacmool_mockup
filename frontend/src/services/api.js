const API_URL = process.env.REACT_APP_BACKEND_URL;

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

// Employees API
export const employeesAPI = {
  getAll: async (department = null) => {
    const url = department && department !== 'all' 
      ? `${API_URL}/api/employees?department=${department}`
      : `${API_URL}/api/employees`;
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch employees');
    return response.json();
  },

  getOne: async (id) => {
    const response = await fetch(`${API_URL}/api/employees/${id}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch employee');
    return response.json();
  },

  create: async (data) => {
    const response = await fetch(`${API_URL}/api/employees`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create employee');
    return response.json();
  },

  update: async (id, data) => {
    const response = await fetch(`${API_URL}/api/employees/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update employee');
    return response.json();
  },

  delete: async (id) => {
    const response = await fetch(`${API_URL}/api/employees/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete employee');
    return response.json();
  }
};

// Aciertos y Desaciertos API
export const aciertosAPI = {
  getAll: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.month && filters.month !== 'all') params.append('month', filters.month);
    if (filters.year && filters.year !== 'all') params.append('year', filters.year);
    if (filters.department && filters.department !== 'all') params.append('department', filters.department);
    if (filters.employee_id && filters.employee_id !== 'all') params.append('employee_id', filters.employee_id);
    
    const url = `${API_URL}/api/aciertos-desaciertos${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch evaluations');
    return response.json();
  },

  getOne: async (id) => {
    const response = await fetch(`${API_URL}/api/aciertos-desaciertos/${id}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch evaluation');
    return response.json();
  },

  create: async (data) => {
    const response = await fetch(`${API_URL}/api/aciertos-desaciertos`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create evaluation');
    return response.json();
  },

  update: async (id, data) => {
    const response = await fetch(`${API_URL}/api/aciertos-desaciertos/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update evaluation');
    return response.json();
  },

  delete: async (id) => {
    const response = await fetch(`${API_URL}/api/aciertos-desaciertos/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete evaluation');
    return response.json();
  }
};

// KPIs API
export const kpisAPI = {
  // Templates
  getTemplates: async () => {
    const response = await fetch(`${API_URL}/api/kpis/templates`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch KPI templates');
    return response.json();
  },

  getTemplate: async (id) => {
    const response = await fetch(`${API_URL}/api/kpis/templates/${id}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch KPI template');
    return response.json();
  },

  createTemplate: async (data) => {
    const response = await fetch(`${API_URL}/api/kpis/templates`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create KPI template');
    return response.json();
  },

  updateTemplate: async (id, data) => {
    const response = await fetch(`${API_URL}/api/kpis/templates/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update KPI template');
    return response.json();
  },

  deleteTemplate: async (id) => {
    const response = await fetch(`${API_URL}/api/kpis/templates/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete KPI template');
    return response.json();
  },

  // Assignments
  getAssignments: async () => {
    const response = await fetch(`${API_URL}/api/kpis/assignments`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch KPI assignments');
    return response.json();
  },

  createAssignment: async (data) => {
    const response = await fetch(`${API_URL}/api/kpis/assignments`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create KPI assignment');
    return response.json();
  },

  deleteAssignment: async (id) => {
    const response = await fetch(`${API_URL}/api/kpis/assignments/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete KPI assignment');
    return response.json();
  },

  // Evaluations
  getEvaluations: async () => {
    const response = await fetch(`${API_URL}/api/kpis/evaluations`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch KPI evaluations');
    return response.json();
  },

  createEvaluation: async (data) => {
    const response = await fetch(`${API_URL}/api/kpis/evaluations`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create KPI evaluation');
    return response.json();
  }
};

// Evaluations 360 API
export const eval360API = {
  // Templates
  getTemplates: async () => {
    const response = await fetch(`${API_URL}/api/evaluations360/templates`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch Eval360 templates');
    return response.json();
  },

  getTemplate: async (id) => {
    const response = await fetch(`${API_URL}/api/evaluations360/templates/${id}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch Eval360 template');
    return response.json();
  },

  createTemplate: async (data) => {
    const response = await fetch(`${API_URL}/api/evaluations360/templates`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create Eval360 template');
    return response.json();
  },

  updateTemplate: async (id, data) => {
    const response = await fetch(`${API_URL}/api/evaluations360/templates/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update Eval360 template');
    return response.json();
  },

  deleteTemplate: async (id) => {
    const response = await fetch(`${API_URL}/api/evaluations360/templates/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete Eval360 template');
    return response.json();
  },

  // Plans
  getPlans: async () => {
    const response = await fetch(`${API_URL}/api/evaluations360/plans`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch evaluation plans');
    return response.json();
  },

  createPlan: async (data) => {
    const response = await fetch(`${API_URL}/api/evaluations360/plans`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create evaluation plan');
    return response.json();
  },

  getPlan: async (id) => {
    const response = await fetch(`${API_URL}/api/evaluations360/plans/${id}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch evaluation plan');
    return response.json();
  },

  deletePlan: async (id) => {
    const response = await fetch(`${API_URL}/api/evaluations360/plans/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete evaluation plan');
    return response.json();
  },

  updatePlan: async (id, data) => {
    const response = await fetch(`${API_URL}/api/evaluations360/plans/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update evaluation plan');
    return response.json();
  },

  // Results
  getResults: async () => {
    const response = await fetch(`${API_URL}/api/evaluations360/results`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch evaluation results');
    return response.json();
  },

  submitEvaluation: async (data) => {
    const response = await fetch(`${API_URL}/api/evaluations360/submit-evaluation`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit evaluation');
    }
    return response.json();
  },


  // PDIs
  getPDIs: async () => {
    const response = await fetch(`${API_URL}/api/evaluations360/pdis`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch PDIs');
    return response.json();
  },

  createPDI: async (data) => {
    const response = await fetch(`${API_URL}/api/evaluations360/pdis`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create PDI');
    return response.json();
  },

  updatePDI: async (id, data) => {
    const response = await fetch(`${API_URL}/api/evaluations360/pdis/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update PDI');
    return response.json();
  }
};

// PDI API (simplified)
export const pdiAPI = {
  getAll: async () => {
    const response = await fetch(`${API_URL}/api/evaluations360/pdis`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch PDIs');
    return response.json();
  },

  getMyPDI: async () => {
    const response = await fetch(`${API_URL}/api/evaluations360/pdis`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch my PDI');
    const pdis = await response.json();
    return pdis.length > 0 ? pdis : [];
  },

  create: async (data) => {
    const response = await fetch(`${API_URL}/api/pdi/create-simple`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create PDI');
    }
    return response.json();
  }
};


// Empleado A Evaluations API
export const empleadoAAPI = {
  // Plans
  getPlans: async () => {
    const response = await fetch(`${API_URL}/api/empleado-a/plans`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch Empleado A plans');
    return response.json();
  },

  getPlan: async (id) => {
    const response = await fetch(`${API_URL}/api/empleado-a/plans/${id}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch Empleado A plan');
    return response.json();
  },

  createPlan: async (data) => {
    const response = await fetch(`${API_URL}/api/empleado-a/plans`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create Empleado A plan');
    return response.json();
  },

  deletePlan: async (id) => {
    const response = await fetch(`${API_URL}/api/empleado-a/plans/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete Empleado A plan');
    return response.json();
  },

  updatePlan: async (id, data) => {
    const response = await fetch(`${API_URL}/api/empleado-a/plans/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update Empleado A plan');
    return response.json();
  },

  // Votes
  submitVote: async (planId, voteData) => {
    const response = await fetch(`${API_URL}/api/empleado-a/plans/${planId}/vote`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(voteData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit vote');
    }
    return response.json();
  },

  getMyPendingEvaluations: async () => {
    const response = await fetch(`${API_URL}/api/empleado-a/my-pending-evaluations`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch pending evaluations');
    return response.json();
  },

  // Results
  getEmployeeResults: async (employeeId, period = null) => {
    const url = period 
      ? `${API_URL}/api/empleado-a/results/${employeeId}?period=${period}`
      : `${API_URL}/api/empleado-a/results/${employeeId}`;
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch employee results');
    return response.json();
  },

  getAllResults: async (period = null) => {
    const url = period 
      ? `${API_URL}/api/empleado-a/results?period=${period}`
      : `${API_URL}/api/empleado-a/results`;
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch all results');
    return response.json();
  },

  // Autoevaluación
  createAutoevaluacion: async (data) => {
    const response = await fetch(`${API_URL}/api/empleado-a/autoevaluacion`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create autoevaluacion');
    }
    return response.json();
  },

  getAutoevaluacion: async (employeeId, period = null) => {
    const url = period 
      ? `${API_URL}/api/empleado-a/autoevaluacion/${employeeId}?period=${period}`
      : `${API_URL}/api/empleado-a/autoevaluacion/${employeeId}`;
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch autoevaluacion');
    return response.json();
  }
};


// ============================================================
//                  ASISTENCIA / TIME TRACKING
// ============================================================
const _req = async (path, opts = {}) => {
  const res = await fetch(`${API_URL}${path}`, {
    headers: getAuthHeaders(),
    ...opts,
  });
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try { const j = await res.json(); msg = j.detail || msg; } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
};

export const asistenciaAPI = {
  // Schedules
  listSchedules: () => _req('/api/asistencia/schedules'),
  getSchedule: (id) => _req(`/api/asistencia/schedules/${id}`),
  createSchedule: (data) => _req('/api/asistencia/schedules', {
    method: 'POST', body: JSON.stringify(data),
  }),
  updateSchedule: (id, data) => _req(`/api/asistencia/schedules/${id}`, {
    method: 'PUT', body: JSON.stringify(data),
  }),
  deleteSchedule: (id) => _req(`/api/asistencia/schedules/${id}`, { method: 'DELETE' }),

  // Employee schedule
  getEmployeeSchedule: (employeeId) => _req(`/api/asistencia/employees/${employeeId}/schedule`),
  assignSchedule: (employeeId, scheduleId, assignedFrom = null) => _req(
    `/api/asistencia/employees/${employeeId}/schedule`,
    { method: 'POST', body: JSON.stringify({ schedule_id: scheduleId, assigned_from: assignedFrom }) }
  ),
  removeEmployeeSchedule: (employeeId) => _req(
    `/api/asistencia/employees/${employeeId}/schedule`, { method: 'DELETE' }
  ),

  // Attendance / fichaje
  current: () => _req('/api/asistencia/attendance/current'),
  clockIn: () => _req('/api/asistencia/attendance/clock-in', { method: 'POST' }),
  clockOut: () => _req('/api/asistencia/attendance/clock-out', { method: 'POST' }),
  pause: () => _req('/api/asistencia/attendance/pause', { method: 'POST' }),
  resume: () => _req('/api/asistencia/attendance/resume', { method: 'POST' }),
  records: ({ employeeId = null, dateFrom, dateTo } = {}) => {
    const qs = new URLSearchParams();
    if (employeeId) qs.set('employee_id', employeeId);
    if (dateFrom) qs.set('date_from', dateFrom);
    if (dateTo) qs.set('date_to', dateTo);
    return _req(`/api/asistencia/attendance/records?${qs.toString()}`);
  },
  summary: ({ employeeId = null, dateFrom, dateTo }) => {
    const qs = new URLSearchParams({ date_from: dateFrom, date_to: dateTo });
    if (employeeId) qs.set('employee_id', employeeId);
    return _req(`/api/asistencia/attendance/summary?${qs.toString()}`);
  },

  // Devices
  getDevices: () => _req('/api/asistencia/devices'),
  updateDevices: (data) => _req('/api/asistencia/devices', {
    method: 'PUT', body: JSON.stringify(data),
  }),
};
