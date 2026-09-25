import { useState } from 'react';
import { api } from '../../api';
import { Badge, DataTable, Empty, fmtDate, Load, PageHead, useConfirm, useLoad, useToast } from '../../ui';

export function AdminPeople({ role }) {
  const isProv = role === 'provider';
  const [q, setQ] = useState('');
  const [onlyPending, setOnlyPending] = useState(false);
  const toast = useToast();
  const [confirmEl, ask] = useConfirm();
  const st = useLoad(() => api(`/admin/users?role=${role}&q=${encodeURIComponent(q)}`), [role, q]);

  const patch = async (u, body, msg) => {
    try { await api(`/admin/users/${u.id}`, { method: 'PATCH', body }); toast(msg, 'ok'); } catch (e) { toast(e.message, 'error'); }
    st.reload();
  };
  const toggleActive = async (u) => {
    if (u.is_active && !(await ask(`Deactivate ${u.name}?`, 'They will be signed out and unable to log in until you reactivate them.', 'Deactivate', 'Cancel'))) return;
    patch(u, { is_active: !u.is_active }, u.is_active ? 'Account deactivated.' : 'Account reactivated.');
  };

  const cols = [
    { label: 'Name', render: (u) => <><strong>{u.name}</strong><div className="small muted">{u.email} · {u.mobile}</div></> },
    { label: 'City', render: (u) => u.city || '—' },
    isProv
      ? { label: 'Services', render: (u) => <span className="small">{(u.skills || []).join(', ') || '—'}</span> }
      : { label: 'Bookings', render: (u) => u.bookings ?? 0 },
    ...(isProv ? [{ label: 'Jobs done', render: (u) => u.jobs_done ?? 0 }] : []),
    { label: 'Status', render: (u) => (
      <span className="row" style={{ gap: '.3rem', justifyContent: 'flex-end' }}>
        <Badge value={u.is_active ? 'active' : 'inactive'} />
        {isProv && <Badge value={u.approved ? 'Approved' : 'Pending'} />}
      </span>) },
    { label: 'Joined', render: (u) => fmtDate(u.created_at), className: 'nowrap' },
    { label: 'Actions', className: 'no-label', stop: true, render: (u) => (
      <span className="row" style={{ gap: '.4rem', justifyContent: 'flex-end' }}>
        {isProv && !u.approved && u.is_active && <button className="btn sm" onClick={() => patch(u, { approved: true }, `${u.name} approved.`)}>Approve</button>}
        {isProv && u.approved && <button className="btn plain sm" onClick={() => patch(u, { approved: false }, 'Approval removed.')}>Revoke</button>}
        <button className={`btn sm ${u.is_active ? 'danger' : 'plain'}`} onClick={() => toggleActive(u)}>{u.is_active ? 'Deactivate' : 'Reactivate'}</button>
      </span>) },
  ];

  return (
    <>
      <PageHead title={isProv ? 'Service providers' : 'Service seekers'} sub={isProv ? 'Approve new providers and manage who can take jobs.' : 'People who book services.'} />
      <div className="toolbar">
        <input type="search" placeholder="Search name, email or mobile" aria-label="Search" value={q} onChange={(e) => setQ(e.target.value)} />
        {isProv && <label className="checkbox"><input type="checkbox" checked={onlyPending} onChange={(e) => setOnlyPending(e.target.checked)} /> Awaiting approval only</label>}
      </div>
      <Load state={st}>{({ users }) => (
        <DataTable cols={cols} rows={isProv && onlyPending ? users.filter((u) => !u.approved) : users}
          empty={<Empty title="No one here yet">{q ? 'No matches for that search.' : 'New sign-ups will appear here.'}</Empty>} />
      )}</Load>
      {confirmEl}
    </>
  );
}
