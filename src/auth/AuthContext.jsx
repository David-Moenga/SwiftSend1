import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import { apiUrl } from './api';

const AuthContext = createContext(null);
const SESSION_STORAGE_KEY = 'swiftsend.session';

const readSession = () => {
  try {
    const storedSession = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!storedSession) return null;

    const parsedSession = JSON.parse(storedSession);
    return parsedSession && parsedSession.authenticated === true ? parsedSession : null;
  } catch {
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  }
};

const normalizeRoles = (roles) => {
  if (Array.isArray(roles)) return roles;
  return typeof roles === 'string' ? [roles] : [];
};

const normalizeSession = (payload) => {
  const data = payload?.data ?? payload;
  const accessToken = data?.accessToken ?? data?.access_token ?? data?.access ?? data?.token ?? null;
  const refreshToken = data?.refreshToken ?? data?.refresh_token ?? data?.refresh ?? null;
  const user = data?.user ?? data?.account ?? data?.profile ?? null;

  if (!accessToken && !user && data?.authenticated !== true) {
    throw new Error('The sign-in response did not include an authenticated session.');
  }

  return {
    authenticated: true,
    accessToken: typeof accessToken === 'string' ? accessToken : null,
    refreshToken: typeof refreshToken === 'string' ? refreshToken : null,
    user,
    roles: normalizeRoles(data?.roles ?? user?.roles ?? user?.role),
  };
};

export const AuthProvider = ({ children }) => {
  const [session, setSession] = useState(readSession);

  const signIn = useCallback((payload) => {
    const nextSession = normalizeSession(payload);
    sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(nextSession));
    setSession(nextSession);
  }, []);

  const signOut = useCallback(async () => {
    try {
      const headers = new Headers();
      if (session?.accessToken) {
        headers.set('Authorization', `Bearer ${session.accessToken}`);
      }
      if (session?.refreshToken) {
        headers.set('Content-Type', 'application/json');
      }

      await fetch(apiUrl('/api/auth/logout/'), {
        method: 'POST',
        headers,
        credentials: 'include',
        body: session?.refreshToken ? JSON.stringify({ refresh: session.refreshToken }) : undefined,
      });
    } catch {
      // Clear the local session even if the server session has already expired.
    } finally {
      sessionStorage.removeItem(SESSION_STORAGE_KEY);
      setSession(null);
    }
  }, [session]);

  const authFetch = useCallback(
    (url, options = {}) => {
      const headers = new Headers(options.headers);

      if (session?.accessToken && !headers.has('Authorization')) {
        headers.set('Authorization', `Bearer ${session.accessToken}`);
      }

      return fetch(apiUrl(url), {
        ...options,
        headers,
        credentials: 'include',
      });
    },
    [session],
  );

  const value = useMemo(
    () => ({
      user: session?.user ?? null,
      roles: session?.roles ?? [],
      isAuthenticated: Boolean(session?.authenticated),
      signIn,
      signOut,
      authFetch,
    }),
    [authFetch, session, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider.');
  }

  return context;
};
