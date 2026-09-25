import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import { useAuth, homeFor } from '../auth';
import { Field, useLoad, useToast } from '../ui';

function Card({ title, sub, children }) {
  return (
    <div className="container auth-wrap">
      <div className="panel auth-card">
        <h1 style={{ fontSize: '1.9rem' }}>{title}</h1>
        {sub && <p className="muted">{sub}</p>}
        {children}
      </div>
    </div>
  );
}

export function Login() {
  const { user, login } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const [f, setF] = useState({ email: '', password: '' });
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to={homeFor(user.role)} replace />;

  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('');
    try {
      const u = await login(f.email, f.password);
      const from = loc.state?.from; // e.g. they clicked "Book" while logged out
      nav(u.role === 'user' && from?.startsWith('/book/') ? from : homeFor(u.role), { replace: true });
    } catch (ex) { setErr(ex.message); setBusy(false); }
  };
  return (
    <Card title="Log in" sub="Customers, providers and admins all sign in here.">
      {err && <div className="alert error" role="alert">{err}</div>}
      <form onSubmit={submit}>
        <Field label="Email"><input type="email" required autoComplete="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></Field>
        <Field label="Password"><input type="password" required autoComplete="current-password" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></Field>
        <button className="btn block" disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
      </form>
      <p className="small" style={{ marginTop: '1rem' }}><Link to="/forgot-password">Forgot your password?</Link> · New here? <Link to="/register">Create an account</Link></p>
    </Card>
  );
}

export function Register() {
  const { user, register } = useAuth();
  const nav = useNavigate();
  const [sp] = useSearchParams();
  const [role, setRole] = useState(sp.get('role') === 'provider' ? 'provider' : 'user');
  const [f, setF] = useState({ name: '', email: '', mobile: '', city: 'Ranchi', password: '', bio: '' });
  const [skills, setSkills] = useState([]);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const svc = useLoad(() => api('/services'));
  if (user) return <Navigate to={homeFor(user.role)} replace />;

  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const toggle = (slug) => setSkills((s) => (s.includes(slug) ? s.filter((x) => x !== slug) : [...s, slug]));
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('');
    try {
      const u = await register({ ...f, role, skills: role === 'provider' ? skills : undefined });
      nav(homeFor(u.role), { replace: true });
    } catch (ex) { setErr(ex.message); setBusy(false); }
  };

  return (
    <Card title="Create your account">
      <div className="tabs" role="tablist">
        <button type="button" role="tab" aria-selected={role === 'user'} onClick={() => setRole('user')}>Service seeker</button>
        <button type="button" role="tab" aria-selected={role === 'provider'} onClick={() => setRole('provider')}>Service provider</button>
      </div>
      {role === 'provider' && <div className="alert info">Provider accounts are reviewed by our team before you can accept jobs.</div>}
      {err && <div className="alert error" role="alert">{err}</div>}
      <form onSubmit={submit}>
        <Field label="Full name"><input required autoComplete="name" value={f.name} onChange={set('name')} /></Field>
        <Field label="Email"><input type="email" required autoComplete="email" value={f.email} onChange={set('email')} /></Field>
        <div className="form-grid">
          <Field label="Mobile number"><input required inputMode="numeric" maxLength={10} pattern="[6-9][0-9]{9}" title="10-digit mobile number" autoComplete="tel-national" value={f.mobile} onChange={set('mobile')} /></Field>
          <Field label="City"><input value={f.city} onChange={set('city')} /></Field>
        </div>
        <Field label="Password" hint="At least 8 characters."><input type="password" required minLength={8} autoComplete="new-password" value={f.password} onChange={set('password')} /></Field>
        {role === 'provider' && (
          <>
            <div className="field"><span style={{ fontWeight: 600, fontSize: '.9rem' }}>Services you offer</span>
              <div className="chips" style={{ marginTop: '.4rem' }}>
                {(svc.data?.services || []).map((s) => (
                  <button type="button" key={s.id} className="chip-toggle" aria-pressed={skills.includes(s.slug)} onClick={() => toggle(s.slug)}>{s.name}</button>
                ))}
              </div>
            </div>
            <Field label="About you" hint="Experience, tools, areas you cover (optional)."><textarea maxLength={500} value={f.bio} onChange={set('bio')} /></Field>
          </>
        )}
        <button className="btn block" disabled={busy || (role === 'provider' && !skills.length)}>{busy ? 'Creating account…' : 'Create account'}</button>
      </form>
      <p className="small" style={{ marginTop: '1rem' }}>Already registered? <Link to="/login">Log in</Link></p>
    </Card>
  );
}

export function Forgot() {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('');
    try { setMsg((await api('/auth/forgot', { method: 'POST', body: { email } })).message); } catch (ex) { setErr(ex.message); }
    setBusy(false);
  };
  return (
    <Card title="Reset your password" sub="Enter your email and we'll send you a link to choose a new password.">
      {msg && <div className="alert ok" role="status">{msg}</div>}
      {err && <div className="alert error" role="alert">{err}</div>}
      <form onSubmit={submit}>
        <Field label="Email"><input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
        <button className="btn block" disabled={busy}>Send reset link</button>
      </form>
      <p className="small" style={{ marginTop: '1rem' }}><Link to="/login">Back to log in</Link></p>
    </Card>
  );
}

export function Reset() {
  const [sp] = useSearchParams();
  const nav = useNavigate();
  const toast = useToast();
  const [pw, setPw] = useState({ a: '', b: '' });
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault(); setErr('');
    if (pw.a !== pw.b) return setErr("The two passwords don't match.");
    setBusy(true);
    try {
      await api('/auth/reset', { method: 'POST', body: { token: sp.get('token'), password: pw.a } });
      toast('Password updated. Log in with your new password.', 'ok');
      nav('/login', { replace: true });
    } catch (ex) { setErr(ex.message); setBusy(false); }
  };
  return (
    <Card title="Choose a new password">
      {err && <div className="alert error" role="alert">{err}</div>}
      <form onSubmit={submit}>
        <Field label="New password" hint="At least 8 characters."><input type="password" required minLength={8} autoComplete="new-password" value={pw.a} onChange={(e) => setPw({ ...pw, a: e.target.value })} /></Field>
        <Field label="Confirm new password"><input type="password" required minLength={8} autoComplete="new-password" value={pw.b} onChange={(e) => setPw({ ...pw, b: e.target.value })} /></Field>
        <button className="btn block" disabled={busy}>Update password</button>
      </form>
    </Card>
  );
}
