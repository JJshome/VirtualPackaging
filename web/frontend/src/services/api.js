import axios from 'axios';

// Create axios instance with base URL and default headers
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication if needed
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Projects API
const projectsApi = {
  getProjects: (params) => api.get('/projects', { params }),
  getProject: (id) => api.get(`/projects/${id}`),
  createProject: (data) => api.post('/projects', data),
  updateProject: (id, data) => api.put(`/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/projects/${id}`),
};

// Capture API
const captureApi = {
  uploadImages: (projectId, formData) => api.post(`/capture/images/${projectId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  startReconstruction: (projectId, settings) => api.post(`/capture/reconstruct/${projectId}`, settings),
  getCaptureStatus: (captureId) => api.get(`/capture/status/${captureId}`),
  getModels: (projectId) => api.get(`/capture/models/${projectId}`),
  getModel: (projectId, modelId) => api.get(`/capture/models/${projectId}/${modelId}`),
};

// Design API
const designApi = {
  getPackageTypes: (params) => api.get('/design/package-types', { params }),
  getMaterials: (params) => api.get('/design/materials', { params }),
  generateDesign: (data) => api.post('/design/generate', data),
  getDesignStatus: (designId) => api.get(`/design/status/${designId}`),
  getDesigns: (projectId) => api.get(`/design/${projectId}`),
  getDesign: (projectId, designId) => api.get(`/design/${projectId}/${designId}`),
  provideFeedback: (data) => api.post('/design/feedback', data),
};

// Export API
const exportApi = {
  getFormats: () => api.get('/export/formats'),
  exportDesign: (data) => api.post('/export', data),
  getExportStatus: (exportId) => api.get(`/export/status/${exportId}`),
  getExportResults: (designId) => api.get(`/export/results/${designId}`),
  getExportResult: (designId, exportId) => api.get(`/export/results/${designId}/${exportId}`),
};

// LLM API
const llmApi = {
  generateText: (data) => api.post('/llm/generate-text', data),
  processInteraction: (data) => api.post('/llm/interaction', data),
  getConversation: (designId) => api.get(`/llm/conversation/${designId}`),
  getDesignSuggestions: (data) => api.post('/llm/design-suggestions', data),
};

export {
  projectsApi,
  captureApi,
  designApi,
  exportApi,
  llmApi,
};