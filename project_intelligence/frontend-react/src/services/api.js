import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth
export const login = async (credentials) => {
    const { data } = await api.post('/login/', credentials);
    return data;
};

export const register = async (userData) => {
    const { data } = await api.post('/register/', userData);
    return data;
};

export const getProfile = async () => {
    const { data } = await api.get('/profile/');
    return data;
};

// Dashboards
export const getManagerDashboard = async () => {
    const { data } = await api.get('/manager/dashboard/');
    return data;
};

export const getEmployeeDashboard = async () => {
    const { data } = await api.get('/employee/dashboard/');
    return data;
};

// Projects
export const getProjects = async () => {
    const { data } = await api.get('/projects/');
    return data;
};

export const createProject = async (projectData) => {
    const { data } = await api.post('/projects/', projectData);
    return data;
};

// Tasks
export const getTasks = async () => {
    const { data } = await api.get('/tasks/');
    return data;
};

export const createTask = async (taskData) => {
    const { data } = await api.post('/tasks/', taskData);
    return data;
};

export const updateTaskHours = async (taskId, hours) => {
    const { data } = await api.post(`/tasks/${taskId}/update_hours/`, { actual_hours: hours });
    return data;
};

export const updateTask = async (taskId, updates) => {
    const { data } = await api.patch(`/tasks/${taskId}/`, updates);
    return data;
};

// Sprints
export const getSprints = async () => {
    const { data } = await api.get('/sprints/');
    return data;
};

export const createSprint = async (sprintData) => {
    const { data } = await api.post('/sprints/', sprintData);
    return data;
};

// Employees
export const getEmployees = async () => {
    const { data } = await api.get('/employees/');
    return data;
};

// Task Assignment
export const assignTask = async (taskId, employeeId) => {
    const { data } = await api.post(`/tasks/${taskId}/assign/`, { employee_id: employeeId });
    return data;
};

// Meetings
export const getMeetings = async () => {
    const { data } = await api.get('/meetings/');
    return data;
};

export const createMeeting = async (meetingData) => {
    const { data } = await api.post('/meetings/', meetingData);
    return data;
};

export const getMeetingDetail = async (meetingId) => {
    const { data } = await api.get(`/meetings/${meetingId}/`);
    return data;
};

export const joinMeeting = async (meetingId) => {
    const { data } = await api.post(`/meetings/${meetingId}/join/`);
    return data;
};

export const startMeeting = async (meetingId) => {
    const { data } = await api.post(`/meetings/${meetingId}/start/`);
    return data;
};

export const completeMeeting = async (meetingId, notes) => {
    const { data } = await api.post(`/meetings/${meetingId}/complete/`, { notes });
    return data;
};

export const generateMeetingSummary = async (meetingId) => {
    const { data } = await api.post(`/meetings/${meetingId}/generate-summary/`);
    return data;
};

export const saveTranscript = async (meetingId, transcript) => {
    const { data } = await api.post(`/meetings/${meetingId}/save-transcript/`, { transcript });
    return data;
};

// GitHub Integration
export const linkGitHubRepo = async (projectId, payload) => {
    const { data } = await api.post(`/projects/${projectId}/link-github/`, payload);
    return data;
};

export const syncCommits = async (projectId) => {
    const { data } = await api.post(`/projects/${projectId}/sync-commits/`);
    return data;
};

export const getProjectCommits = async (projectId, limit = 20) => {
    const { data } = await api.get(`/projects/${projectId}/commits/?limit=${limit}`);
    return data;
};

export default api;
