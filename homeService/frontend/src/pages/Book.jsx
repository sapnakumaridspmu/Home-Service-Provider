import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../auth';
import { usePayment } from '../payment';
import { Field, inr, Load, useLoad, useToast } from '../ui';

const todayIST = () => new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });

export default function Book() {
  const { slug } = useParams();
  const { user } = useAuth();
  const nav = useNavigate();
  const toast = useToast();
  const { pay, modal } = usePayment();
  const st = useLoad(() => api(`/services/${slug}`), [slug]);
  const cfg = useLoad(() => api('/config'));
  const [f, setF] = useState({ date: '', slot: '', address: '', landmark: '', city: user.city || 'Ranchi', contact: user.mobile || '', notes: '' });
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e, service) => {
    e.preventDefault(); setErr('');
    if (!f.slot) return setErr('Choose a time slot.');
    setBusy(true);
    let booking;
    try {
      booking = (await api('/bookings', { method: 'POST', body: { ...f, service_id: service.id } })).booking;
    } catch (ex) { setErr(ex.message); setBusy(false); return; }
    // The booking now exists (unpaid). Whatever happens next, it's safe in the dashboard.
    try {
      const r = await pay(booking);
      toast(r.paid ? 'Payment received. Your booking is confirmed.' : 'Booking saved. Complete payment to confirm it.', r.paid ? 'ok' : '');
    } catch (ex) { toast(ex.message, 'error'); }
    nav('/dashboard/bookings');
  };

  return (
    <div className="container section">
      <Load state={st}>{({ service: s }) => (
        <>
          <p className="small"><Link to={`/services/${s.slug}`}>← {s.name}</Link></p>
          <h1 style={{ fontSize: 'clamp(1.7rem,3vw+.5rem,2.4rem)' }}>Book {s.name}</h1>
          <div className="detail-grid" style={{ gridTemplateColumns: '1.3fr .7fr' }}>
            <form className="panel" onSubmit={(e) => submit(e, s)}>
              {err && <div className="alert error" role="alert">{err}</div>}
              <div className="form-grid">
                <Field label="Date"><input type="date" required min={todayIST()} value={f.date} onChange={set('date')} /></Field>
                <Field label="Time slot">
                  <select required value={f.slot} onChange={set('slot')}>
                    <option value="">Choose a slot</option>
                    {(cfg.data?.slots || []).map((sl) => <option key={sl}>{sl}</option>)}
                  </select>
                </Field>
              </div>
              <Field label="Full address"><textarea required minLength={8} value={f.address} onChange={set('address')} placeholder="House / flat, street, area" /></Field>
              <div className="form-grid">
                <Field label="Landmark (optional)"><input value={f.landmark} onChange={set('landmark')} /></Field>
                <Field label="City"><input required value={f.city} onChange={set('city')} /></Field>
              </div>
              <Field label="Contact number" hint="The provider will call this number."><input required inputMode="numeric" maxLength={10} pattern="[6-9][0-9]{9}" title="10-digit mobile number" value={f.contact} onChange={set('contact')} /></Field>
              <Field label="Anything the provider should know? (optional)"><textarea maxLength={500} value={f.notes} onChange={set('notes')} /></Field>
              <button className="btn cta block" disabled={busy}>{busy ? 'Please wait…' : `Continue to payment · ${inr(s.price)}`}</button>
            </form>
            <aside className="panel sticky">
              <h3>Order summary</h3>
              <dl className="kv" style={{ margin: '.75rem 0' }}>
                <dt>Service</dt><dd>{s.name}</dd>
                <dt>Duration</dt><dd>{s.duration}</dd>
                <dt>Total</dt><dd className="amount">{inr(s.price)}</dd>
              </dl>
              <p className="small muted row" style={{ gap: '.5rem', flexWrap: 'nowrap', alignItems: 'flex-start' }}>
                <ShieldCheck size={18} style={{ flex: 'none', color: 'var(--teal)' }} />
                Pay by UPI, card or net banking. Cancel before the job starts for a full refund.
              </p>
            </aside>
          </div>
        </>
      )}</Load>
      {modal}
    </div>
  );
}
