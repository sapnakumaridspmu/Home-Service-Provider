import { useState } from 'react';
import { api } from '../api';
import { useAuth } from '../auth';
import { Field, PageHead, useLoad, useToast } from '../ui';

export default function Profile() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const svc = useLoad(() => api('/services'));
  const [f, setF] = useState({ name: user.name, mobile: user.mobile, city: user.city || '', bio: user.bio || '' });
  const [skills, setSkills] = useState(user.skills || []);
  const [pw, setPw] = useState({ current_password: '', new_password: '' });
  const [err, setErr] = useState('');
  const [pwErr, setPwErr] = useState('');
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault(); setErr('');
    try {
      const r = await api('/auth/me', { method: 'PUT', body: { ...f, skills } });
      setUser(r.user); toast('Profile saved.', 'ok');
    } catch (ex) { setErr(ex.message); }
  };
  const changePw = async (e) => {
    e.preventDefault(); setPwErr('');
    try {
      await api('/auth/password', { method: 'PUT', body: pw });
      setPw({ current_password: '', new_password: '' }); toast('Password changed.', 'ok');
    } catch (ex) { setPwErr(ex.message); }
  };

  return (
    <>
      <PageHead title="Profile" sub={user.email} />
      <div className="two-col" style={{ gridTemplateColumns: 'minmax(0,1.2fr) minmax(0,1fr)' }}>
        <form className="panel" onSubmit={save}>
          <h3>Your details</h3>
          {err && <div className="alert error" role="alert">{err}</div>}
          <Field label="Full name"><input required value={f.name} onChange={set('name')} /></Field>
          <div className="form-grid">
            <Field label="Mobile number"><input required inputMode="numeric" maxLength={10} pattern="[6-9][0-9]{9}" value={f.mobile} onChange={set('mobile')} /></Field>
            <Field label="City"><input value={f.city} onChange={set('city')} /></Field>
          </div>
          {user.role === 'provider' && (
            <>
              <div className="field"><span style={{ fontWeight: 600, fontSize: '.9rem' }}>Services you offer</span>
                <div className="chips" style={{ marginTop: '.4rem' }}>
                  {(svc.data?.services || []).map((s) => (
                    <button type="button" key={s.id} className="chip-toggle" aria-pressed={skills.includes(s.slug)}
                      onClick={() => setSkills((x) => (x.includes(s.slug) ? x.filter((y) => y !== s.slug) : [...x, s.slug]))}>{s.name}</button>
                  ))}
                </div>
              </div>
              <Field label="About you"><textarea maxLength={500} value={f.bio} onChange={set('bio')} /></Field>
            </>
          )}
          <button className="btn">Save changes</button>
        </form>
        <form className="panel" onSubmit={changePw}>
          <h3>Change password</h3>
          {pwErr && <div className="alert error" role="alert">{pwErr}</div>}
          <Field label="Current password"><input type="password" required autoComplete="current-password" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} /></Field>
          <Field label="New password" hint="At least 8 characters."><input type="password" required minLength={8} autoComplete="new-password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} /></Field>
          <button className="btn plain">Update password</button>
        </form>
      </div>
    </>
  );
}
