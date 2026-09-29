import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getLocations = async (params = {}) => {
  const response = await api.get('/api/locations', { params });
  return response.data;
};

export const getPredictions = async () => {
  const response = await api.get('/api/predictions');
  return response.data;
};

export const getPrediction = async (caseId) => {
  const response = await api.get(`/api/predictions/${caseId}`);
  return response.data;
};

export const getDashboardStats = async () => {
  const response = await api.get('/api/dashboard/stats');
  return response.data;
};

export const getCases = async () => {
  const response = await api.get('/api/cases');
  return response.data;
};

export const getCase = async (caseId) => {
  const response = await api.get(`/api/cases/${caseId}`);
  return response.data;
};

export const getAlerts = async (params = {}) => {
  const response = await api.get('/api/alerts', { params });
  return response.data;
};

export const getInvestigationNotes = async (caseId) => {
  const response = await api.get(`/api/investigations/cases/${caseId}/notes`);
  return response.data;
};

export const createInvestigationNote = async (caseId, data) => {
  const response = await api.post(`/api/investigations/cases/${caseId}/notes`, data);
  return response.data;
};

// Keep existing exports for backward compatibility
export const getCasePrediction = getPrediction;

export default api;
