import axios from 'axios';

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return config;
});

// Redirect to auth on unauthorized responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401 && typeof window !== 'undefined') {
      try { localStorage.removeItem('token'); } catch {}
      if (!window.location.pathname.startsWith('/auth')) {
        window.location.href = '/auth';
      }
    }
    return Promise.reject(error);
  }
);

export async function apiGet<T>(path: string): Promise<T> {
  const { data } = await api.get<T>(path);
  return data;
}

export async function apiPost<T>(path: string, body: any, contentType: string = 'application/json'): Promise<T> {
  const headers = { 'Content-Type': contentType } as any;
  const { data } = await api.post<T>(path, contentType === 'application/json' ? body : body, { headers });
  return data;
}

// Enhanced version that returns both data and headers (useful for quota tracking)
export async function apiPostWithHeaders<T>(path: string, body: any, contentType: string = 'application/json'): Promise<{ data: T; usageCount?: number }> {
  const headers = { 'Content-Type': contentType } as any;
  const response = await api.post<T>(path, contentType === 'application/json' ? body : body, { headers });

  // Extract usage count from response headers
  const usageCount = response.headers['x-usage-count']
    ? parseInt(response.headers['x-usage-count'], 10)
    : undefined;

  return { data: response.data, usageCount };
}
