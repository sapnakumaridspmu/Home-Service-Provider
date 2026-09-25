import { useState } from 'react';
import { Link } from 'react-router-dom';
import { CalendarDays, MapPin, Phone, UserRound } from 'lucide-react';
import { api } from '../../api';
import { useAuth } from '../../auth';
import { usePayment } from '../../payment';
import BookingDetail from '../../BookingDetail';
import Swatch from '../../Swatch';
import { Badge, Empty, inr, fmtDate, Load, PageHead, Stat, useConfirm, useLoad, useToast } from '../../ui';

const ACTIVE = ['Pending', 'Accepted', 'In Progress'];

function BookingCard({ b, reload }) {
  const toast = useToast();
  const { pay, modal } = usePayment();
  const [confirmEl, ask] = useConfirm();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const payNow = async () => {
    setBusy(true);
    try {
      const r = await pay(b);
      if (r.paid) toast('Payment received. Your booking is confirmed.', 'ok');
    } catch (e) { toast(e.message, 'error'); }
    setBusy(false); reload();
  };
  const cancel = async () => {
    const paid = b.payment_status === 'Paid';
    if (!(await ask('Cancel this booking?', paid ? `You paid ${inr(b.amount)}. It will be refunded to your original payment method.` : 'This booking has not been paid for yet.', 'Cancel booking'))) return;
    try {
      const r = await api(`/bookings/${b.id}/cancel`, { method: 'POST' });
      toast(r.refund.ok ? (paid ? 'Booking cancelled. Your refund has started.' : 'Booking cancelled.') : 'Booking cancelled. Your refund is pending — our team will process it shortly.', r.refund.ok ? 'ok' : '');
    } catch (e) { toast(e.message, 'error'); }
    reload();
  };
  const canCancel = ['Pending', 'Accepted'].includes(b.status);
  return (
    <article className="bk">
      <div>
        <h3>{b.service_name}</h3>
        <div className="meta">
          <span><CalendarDays size={15} /> {fmtDate(b.date)}, {b.slot}</span>
          <span><MapPin size={15} /> {b.address}</span>
          {b.provider_name && <span><UserRound size={15} /> {b.provider_name}</span>}
          {b.provider_mobile && <a href={`tel:${b.provider_mobile}`} className="row" style={{ gap: '.35rem' }}><Phone size={15} /> {b.provider_mobile}</a>}
        </div>
      </div>
      <div className="side">
        <span className="amount">{inr(b.amount)}</span>
        <div className="row" style={{ gap: '.4rem' }}><Badge value={b.status} /><Badge value={b.payment_status} /></div>
      </div>
      <div className="actions">
        {b.payment_status === 'Unpaid' && b.status !== 'Cancelled' && <button className="btn cta sm" disabled={busy} onClick={payNow}>Pay {inr(b.amount)}</button>}
        {canCancel && <button className="btn danger sm" onClick={cancel}>Cancel</button>}
        <button className="btn plain sm" onClick={() => setOpen(true)}>Details</button>
      </div>
      {open && <BookingDetail b={b} onClose={() => setOpen(false)} />}
      {confirmEl}{modal}
    </article>
  );
}

export function UserOverview() {
  const { user } = useAuth();
  const q = useLoad(() => api('/bookings'));
  const svc = useLoad(() => api('/services'));
  return (
    <>
      <PageHead title={`Hello, ${user.name.split(' ')[0]}`} sub="Here's what's happening with your bookings.">
        <Link className="btn cta" to="/services">Book a service</Link>
      </PageHead>
      <Load state={q}>{({ bookings }) => {
        const live = bookings.filter((b) => ACTIVE.includes(b.status));
        const unpaid = bookings.filter((b) => b.payment_status === 'Unpaid' && b.status !== 'Cancelled');
        return (
          <>
            <div className="stats">
              <Stat label="Upcoming" value={live.length} />
              <Stat label="Waiting for payment" value={unpaid.length} alertish={unpaid.length > 0} />
              <Stat label="Completed" value={bookings.filter((b) => b.status === 'Completed').length} />
              <Stat label="Total paid" value={inr(bookings.filter((b) => b.payment_status === 'Paid').reduce((s, b) => s + b.amount, 0))} />
            </div>
            {unpaid.length > 0 && <div className="alert warn">You have {unpaid.length} booking{unpaid.length > 1 ? 's' : ''} waiting for payment. Providers can only see a job once it's paid. <Link to="/dashboard/bookings">Pay now</Link></div>}
            <h2 style={{ fontSize: '1.3rem' }}>Upcoming</h2>
            {live.length ? <div className="cards">{live.slice(0, 3).map((b) => <BookingCard key={b.id} b={b} reload={q.reload} />)}</div>
              : <Empty title="Nothing booked yet">Pick a service below and a provider will be on the way.</Empty>}
          </>
        );
      }}</Load>
      <h2 style={{ fontSize: '1.3rem', marginTop: '2rem' }}>Book again</h2>
      <Load state={svc}>{(d) => <div className="grid-swatches">{d.services.slice(0, 4).map((s) => <Swatch key={s.id} s={s} to={`/book/${s.slug}`} />)}</div>}</Load>
    </>
  );
}

const FILTERS = { All: () => true, Active: (b) => ACTIVE.includes(b.status), Completed: (b) => b.status === 'Completed', Cancelled: (b) => b.status === 'Cancelled' };

export function UserBookings() {
  const q = useLoad(() => api('/bookings'));
  const [tab, setTab] = useState('All');
  return (
    <>
      <PageHead title="My bookings"><Link className="btn cta" to="/services">New booking</Link></PageHead>
      <div className="filter-tabs">
        {Object.keys(FILTERS).map((t) => <button key={t} className="chip-toggle" aria-pressed={tab === t} onClick={() => setTab(t)}>{t}</button>)}
      </div>
      <Load state={q}>{({ bookings }) => {
        const rows = bookings.filter(FILTERS[tab]);
        return rows.length ? <div className="cards">{rows.map((b) => <BookingCard key={b.id} b={b} reload={q.reload} />)}</div>
          : <Empty title="No bookings here">{tab === 'All' ? <Link to="/services">Book your first service</Link> : 'Nothing matches this filter.'}</Empty>;
      }}</Load>
    </>
  );
}
