import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../../api';
import BookingDetail from '../../BookingDetail';
import { Badge, DataTable, Empty, inr, fmtDate, Load, PageHead, useConfirm, useLoad, useToast } from '../../ui';

const STATUSES = ['Pending', 'Accepted', 'In Progress', 'Completed', 'Cancelled'];

export function AdminBookings() {
  const [sp, setSp] = useSearchParams();
  const status = sp.get('status') || '';
  const [payment, setPayment] = useState('');
  const [q, setQ] = useState('');
  const [open, setOpen] = useState(null);
  const toast = useToast();
  const [confirmEl, ask] = useConfirm();
  const st = useLoad(() => api(`/admin/bookings?status=${status}&payment=${payment}&q=${encodeURIComponent(q)}`), [status, payment, q]);
  const provs = useLoad(() => api('/admin/users?role=provider'));
  const providers = (provs.data?.users || []).filter((u) => u.approved && u.is_active);

  const patch = async (b, body) => {
    try {
      if (body.status === 'Cancelled' && !(await ask('Cancel this booking?', b.payment_status === 'Paid' ? `The customer's ${inr(b.amount)} will be refunded.` : 'This booking is unpaid.', 'Cancel booking'))) return;
      const r = await api(`/admin/bookings/${b.id}`, { method: 'PATCH', body });
      toast(r.refund && !r.refund.ok ? `Updated, but the refund failed: ${r.refund.message}` : 'Booking updated.', r.refund && !r.refund.ok ? 'error' : 'ok');
    } catch (e) { toast(e.message, 'error'); }
    st.reload();
  };
  const retryRefund = async (b) => {
    try { await api(`/admin/bookings/${b.id}/refund`, { method: 'POST' }); toast('Refund processed.', 'ok'); } catch (e) { toast(e.message, 'error'); }
    st.reload();
  };

  const cols = [
    { label: 'Service', render: (b) => <><strong>{b.service_name}</strong><div className="small muted">{fmtDate(b.date)} · {b.slot}</div></> },
    { label: 'Customer', render: (b) => <>{b.user_name}<div className="small muted">{b.city || b.contact}</div></> },
    { label: 'Provider', stop: true, render: (b) => (
      <select className="inline" aria-label="Assign provider" value={b.provider_id || ''} onChange={(e) => patch(b, { provider_id: e.target.value || null })} disabled={['Completed', 'Cancelled'].includes(b.status)}>
        <option value="">Unassigned</option>
        {providers.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        {b.provider_id && !providers.some((p) => p.id === b.provider_id) && <option value={b.provider_id}>{b.provider_name}</option>}
      </select>) },
    { label: 'Status', stop: true, render: (b) => (
      <select className="inline" aria-label="Status" value={b.status} onChange={(e) => patch(b, { status: e.target.value })}>
        {STATUSES.map((s) => <option key={s}>{s}</option>)}
      </select>) },
    { label: 'Payment', render: (b) => <Badge value={b.payment_status} /> },
    { label: 'Amount', render: (b) => <strong>{inr(b.amount)}</strong> },
    { label: '', className: 'no-label', stop: true, render: (b) => b.payment_status === 'Refund Pending' && <button className="btn sm cta" onClick={() => retryRefund(b)}>Retry refund</button> },
  ];

  return (
    <>
      <PageHead title="Bookings" sub="Assign providers, change status and handle refunds." />
      <div className="toolbar">
        <input type="search" placeholder="Search customer, service, provider, city" aria-label="Search bookings" value={q} onChange={(e) => setQ(e.target.value)} />
        <select aria-label="Filter by status" value={status} onChange={(e) => setSp(e.target.value ? { status: e.target.value } : {})}>
          <option value="">All statuses</option>{STATUSES.map((s) => <option key={s}>{s}</option>)}
        </select>
        <select aria-label="Filter by payment" value={payment} onChange={(e) => setPayment(e.target.value)}>
          <option value="">Any payment</option>{['Unpaid', 'Paid', 'Refunded', 'Refund Pending'].map((s) => <option key={s}>{s}</option>)}
        </select>
      </div>
      <Load state={st}>{({ bookings }) => (
        <DataTable cols={cols} rows={bookings} onRow={setOpen} empty={<Empty title="No bookings found">Try clearing the filters.</Empty>} />
      )}</Load>
      {open && <BookingDetail b={(st.data?.bookings || []).find((x) => x.id === open.id) || open} showCustomer onClose={() => setOpen(null)} />}
      {confirmEl}
    </>
  );
}
