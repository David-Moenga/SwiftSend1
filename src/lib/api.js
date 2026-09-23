const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

const readJson = async (response) => {
  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
};

export const api = {
  baseUrl: API_BASE_URL,

  async register({ name, email, password }) {
    const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await readJson(response);

    if (!response.ok) {
      throw new Error(data?.detail || data?.name?.[0] || 'Registration failed.');
    }

    return data;
  },

  async login({ email, password }) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await readJson(response);

    if (!response.ok) {
      throw new Error(data?.detail || data?.non_field_errors?.[0] || 'Login failed.');
    }

    return data;
  },
};

export const saveAuthSession = ({ access, refresh, user }) => {
  localStorage.setItem('swiftsend_access', access || '');
  localStorage.setItem('swiftsend_refresh', refresh || '');
  localStorage.setItem('swiftsend_user', JSON.stringify(user || {}));
};

export const clearAuthSession = () => {
  localStorage.removeItem('swiftsend_access');
  localStorage.removeItem('swiftsend_refresh');
  localStorage.removeItem('swiftsend_user');
};
