import { useState } from 'react';
import { Link } from 'react-router-dom';
import { CalendarDays, MapPin, Phone } from 'lucide-react';
import { api } from '../../api';
import { useAuth } from '../../auth';
import BookingDetail from '../../BookingDetail';
import { Badge, Empty, inr, fmtDate, Load, PageHead, Stat, useConfirm, useLoad, useToast } from '../../ui';

function Pending() {
  return (
    <div className="alert warn" role="status">
      <strong>Waiting for admin approval.</strong> You can update your profile now. Once an admin approves your account, jobs matching your services will appear here.
    </div>
  );
}

export function ProviderOverview() {
  const { user } = useAuth();
  const q = useLoad(() => api('/provider/stats'));
  return (
    <>
      <PageHead title={`Hello, ${user.name.split(' ')[0]}`} sub="Your jobs and earnings at a glance.">
        {user.approved && <Link className="btn cta" to="/provider/available">Find jobs</Link>}
      </PageHead>
      {!user.approved && <Pending />}
      <Load state={q}>{(s) => (
        <>
          <div className="stats">
            <Stat label="Jobs available to you" value={s.available} alertish={s.available > 0} />
            <Stat label="In progress" value={s.active} hint={`${inr(s.upcoming_earnings)} expected`} />
            <Stat label="Completed" value={s.completed} />
            <Stat label="Total earned" value={inr(s.earnings)} hint={`After the ${s.fee_percent}% platform fee`} />
          </div>
          <div className="panel">
            <h3>How jobs work</h3>
            <p className="muted" style={{ marginBottom: 0 }}>Customers pay first, then the job appears under Available jobs for providers with a matching service. The first provider to accept it gets it; the customer's address and phone number are revealed after you accept.</p>
          </div>
        </>
      )}</Load>
    </>
  );
}

function JobCard({ j, mode, act }) {
  const [open, setOpen] = useState(false);
  return (
    <article className="bk">
      <div>
        <h3>{j.service_name}</h3>
        <div className="meta">
          <span><CalendarDays size={15} /> {fmtDate(j.date)}, {j.slot}</span>
          <span><MapPin size={15} /> {mode === 'available' ? (j.city || 'Location shared after you accept') : j.address}</span>
          {j.contact && <a href={`tel:${j.contact}`} className="row" style={{ gap: '.35rem' }}><Phone size={15} /> {j.contact}</a>}
        </div>
        {j.notes && <p className="small" style={{ margin: '.5rem 0 0' }}>“{j.notes}”</p>}
      </div>
      <div className="side">
        <span className="amount">{inr(j.provider_earning)}</span>
        <span className="small muted">you earn</span>
        {mode === 'mine' && <Badge value={j.status} />}
      </div>
      <div className="actions">
        {mode === 'available' && <button className="btn cta sm" onClick={() => act(j, 'accept')}>Accept job</button>}
        {mode === 'mine' && j.status === 'Accepted' && <>
          <button className="btn sm" onClick={() => act(j, 'In Progress')}>Start job</button>
          <button className="btn danger sm" onClick={() => act(j, 'release')}>Release</button>
        </>}
        {mode === 'mine' && ['Accepted', 'In Progress'].includes(j.status) && <button className="btn ghost sm" onClick={() => act(j, 'Completed')}>Mark completed</button>}
        {mode === 'mine' && <button className="btn plain sm" onClick={() => setOpen(true)}>Details</button>}
      </div>
      {open && <BookingDetail b={{ ...j, payment_status: j.payment_status }} showCustomer onClose={() => setOpen(false)} />}
    </article>
  );
}

export function ProviderJobs({ mode }) {
  const { user } = useAuth();
  const toast = useToast();
  const [confirmEl, ask] = useConfirm();
  const q = useLoad(() => (user.approved || mode === 'mine' ? api(mode === 'available' ? '/provider/jobs/available' : '/provider/jobs') : Promise.resolve({ jobs: [] })), [mode, user.approved]);
  const [tab, setTab] = useState('Active');

  const act = async (j, what) => {
    try {
      if (what === 'release' && !(await ask('Release this job?', 'It goes back to the pool for other providers.', 'Release job', 'Keep job'))) return;
      if (what === 'accept') await api(`/provider/jobs/${j.id}/accept`, { method: 'POST' });
      else if (what === 'release') await api(`/provider/jobs/${j.id}/release`, { method: 'POST' });
      else await api(`/provider/jobs/${j.id}/status`, { method: 'POST', body: { status: what } });
      toast(what === 'accept' ? 'Job accepted. Customer details are now visible in My jobs.' : 'Job updated.', 'ok');
    } catch (e) { toast(e.message, 'error'); }
    q.reload();
  };

  return (
    <>
      <PageHead title={mode === 'available' ? 'Available jobs' : 'My jobs'} sub={mode === 'available' ? 'Paid jobs that match the services you offer.' : undefined} />
      {!user.approved && <Pending />}
      {mode === 'mine' && (
        <div className="filter-tabs">
          {['Active', 'Completed', 'Cancelled'].map((t) => <button key={t} className="chip-toggle" aria-pressed={tab === t} onClick={() => setTab(t)}>{t}</button>)}
        </div>
      )}
      <Load state={q}>{({ jobs }) => {
        const rows = mode === 'mine' ? jobs.filter((j) => (tab === 'Active' ? ['Accepted', 'In Progress'].includes(j.status) : j.status === tab)) : jobs;
        return rows.length
          ? <div className="cards">{rows.map((j) => <JobCard key={j.id} j={j} mode={mode} act={act} />)}</div>
          : <Empty title={mode === 'available' ? 'No open jobs right now' : 'No jobs here yet'}>{mode === 'available' ? 'New paid bookings for your services will show up here.' : <Link to="/provider/available">Browse available jobs</Link>}</Empty>;
      }}</Load>
      {confirmEl}
    </>
  );
}
