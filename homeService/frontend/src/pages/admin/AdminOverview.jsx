import { Link } from 'react-router-dom';
import { api } from '../../api';
import { inr, Load, PageHead, Stat, useLoad } from '../../ui';

export function AdminOverview() {
  const q = useLoad(() => api('/admin/stats'));
  return (
    <>
      <PageHead title="Admin overview" sub="Both sides of the marketplace in one place." />
      <Load state={q}>{(s) => {
        const maxB = Math.max(1, ...s.series.map((d) => d.bookings));
        const maxS = Math.max(1, ...Object.values(s.by_status));
        return (
          <>
            <div className="stats">
              <Stat label="Revenue (paid)" value={inr(s.revenue)} hint={`Platform fees earned: ${inr(s.platform_fees)}`} />
              <Stat label="Bookings" value={s.bookings} />
              <Stat label="Service seekers" value={s.users} />
              <Stat label="Approved providers" value={s.providers} />
            </div>
            {(s.pending_providers > 0 || s.unassigned_paid > 0 || s.refund_pending > 0) && (
              <div className="stats">
                {s.pending_providers > 0 && <Stat alertish label="Providers awaiting approval" value={<Link to="/admin/providers">{s.pending_providers}</Link>} />}
                {s.unassigned_paid > 0 && <Stat alertish label="Paid jobs with no provider" value={<Link to="/admin/bookings?status=Pending">{s.unassigned_paid}</Link>} hint="Assign one manually if needed" />}
                {s.refund_pending > 0 && <Stat alertish label="Refunds to retry" value={<Link to="/admin/bookings">{s.refund_pending}</Link>} />}
              </div>
            )}
            <div className="two-col">
              <section className="panel">
                <h3>Bookings, last 7 days</h3>
                <div className="chart" role="img" aria-label="Bookings per day for the last 7 days">
                  {s.series.map((d) => (
                    <div className="col" key={d.date} title={`${d.bookings} bookings · ${inr(d.revenue)} paid`}>
                      <span className="val">{d.bookings}</span>
                      <div className="bar" style={{ height: `${(d.bookings / maxB) * 100}%` }} />
                      <span className="day">{new Date(d.date + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'short' })}</span>
                    </div>
                  ))}
                </div>
                <p className="small muted" style={{ marginTop: '.75rem', marginBottom: 0 }}>Paid this week: {inr(s.series.reduce((a, d) => a + d.revenue, 0))}</p>
              </section>
              <section className="panel">
                <h3>By status</h3>
                <div className="status-bars">
                  {['Pending', 'Accepted', 'In Progress', 'Completed', 'Cancelled'].map((k) => [k, s.by_status[k] ?? 0]).map(([k, v]) => (
                    <div key={k}><span>{k}</span><div className="track"><div className="fill" style={{ width: `${(v / maxS) * 100}%` }} /></div><strong>{v}</strong></div>
                  ))}
                </div>
              </section>
            </div>
          </>
        );
      }}</Load>
    </>
  );
}
