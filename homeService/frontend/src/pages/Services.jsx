import { useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Clock3, BadgeCheck } from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../auth';
import { Empty, inr, Load, useLoad } from '../ui';
import Swatch from '../Swatch';

export function Services() {
  const svc = useLoad(() => api('/services'));
  const [q, setQ] = useState('');
  return (
    <div className="container section">
      <div className="section-head">
        <h1>All services</h1>
        <p>Choose a service to see what's included and book a visit.</p>
      </div>
      <div className="toolbar">
        <input type="search" placeholder="Search services" aria-label="Search services" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <Load state={svc}>{(d) => {
        const rows = d.services.filter((s) => (s.name + s.description).toLowerCase().includes(q.toLowerCase()));
        return rows.length
          ? <div className="grid-swatches">{rows.map((s) => <Swatch key={s.id} s={s} />)}</div>
          : <Empty title="No matching service">Try a different word, like "AC" or "plumber".</Empty>;
      }}</Load>
    </div>
  );
}

export function ServiceDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const nav = useNavigate();
  const st = useLoad(() => api(`/services/${slug}`), [slug]);
  const all = useLoad(() => api('/services'));
  const others = useMemo(() => (all.data?.services || []).filter((s) => s.slug !== slug).slice(0, 4), [all.data, slug]);

  const book = () => {
    if (!user) return nav('/login', { state: { from: `/book/${slug}` } });
    if (user.role !== 'user') return; // providers/admins don't book
    nav(`/book/${slug}`);
  };

  return (
    <div className="container section">
      <Load state={st}>{({ service: s }) => (
        <>
          <p className="small"><Link to="/services">All services</Link> / {s.name}</p>
          <div className="detail-grid">
            <div className="stack">
              <img className="detail-img" style={{ '--chip': s.color }} src={s.image} alt={s.name} loading="lazy" onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }} />
              <h1 style={{ fontSize: 'clamp(1.8rem,3vw+.5rem,2.6rem)' }}>{s.name}</h1>
              <p style={{ fontSize: '1.08rem', maxWidth: '40rem' }}>{s.description}</p>
              <div className="row muted">
                <span className="row" style={{ gap: '.4rem' }}><Clock3 size={18} /> Usually {s.duration}</span>
                <span className="row" style={{ gap: '.4rem' }}><BadgeCheck size={18} /> Admin-approved providers</span>
              </div>
            </div>
            <aside className="panel sticky">
              <div className="muted small">Starting price</div>
              <div className="price-big">{inr(s.price)}</div>
              <p className="small muted">Pay online when you book. Free cancellation until the job starts, with a full refund.</p>
              {user && user.role !== 'user'
                ? <div className="alert info">Log in with a service seeker account to book this service.</div>
                : <button className="btn cta block" onClick={book}>Book this service</button>}
            </aside>
          </div>
          {others.length > 0 && (
            <section style={{ marginTop: '3rem' }}>
              <h2>Other services</h2>
              <div className="grid-swatches">{others.map((o) => <Swatch key={o.id} s={o} />)}</div>
            </section>
          )}
        </>
      )}</Load>
    </div>
  );
}
