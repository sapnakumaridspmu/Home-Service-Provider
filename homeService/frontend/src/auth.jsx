import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { api, getToken, setToken, setUnauthorizedHandler } from './api';
import { Spinner } from './ui';

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);
export const homeFor = (role) => ({ admin: '/admin', provider: '/provider' }[role] || '/dashboard');

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!getToken());

  const logout = useCallback(() => { setToken(null); setUser(null); }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    if (!getToken()) return;
    api('/auth/me').then((r) => setUser(r.user)).catch(logout).finally(() => setLoading(false));
  }, [logout]);

  const value = useMemo(() => ({
    user, loading, logout, setUser,
    async login(email, password) {
      const r = await api('/auth/login', { method: 'POST', body: { email, password } });
      setToken(r.token); setUser(r.user); return r.user;
    },
    async register(payload) {
      const r = await api('/auth/register', { method: 'POST', body: payload });
      setToken(r.token); setUser(r.user); return r.user;
    },
  }), [user, loading, logout]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

/** Route guard. Sends visitors to login and everyone else to their own dashboard. */
export function RequireRole({ roles, children }) {
  const { user, loading } = useAuth();
  const loc = useLocation();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" replace state={{ from: loc.pathname }} />;
  if (!roles.includes(user.role)) return <Navigate to={homeFor(user.role)} replace />;
  return children;
}
