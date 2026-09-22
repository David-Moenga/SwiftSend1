const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export const apiUrl = (path) => (
  /^https?:\/\//i.test(path) ? path : `${API_BASE_URL}${path}`
);
