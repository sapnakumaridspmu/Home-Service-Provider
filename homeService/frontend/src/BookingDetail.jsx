import { Modal, Badge, inr, fmtDate, fmtDateTime } from './ui';

export default function BookingDetail({ b, onClose, footer, showCustomer }) {
  return (
    <Modal title={b.service_name} onClose={onClose} footer={footer}>
      <div className="row" style={{ marginBottom: '1rem' }}>
        <Badge value={b.status} /><Badge value={b.payment_status} /><span className="amount" style={{ marginLeft: 'auto' }}>{inr(b.amount)}</span>
      </div>
      <dl className="kv">
        <dt>When</dt><dd>{fmtDate(b.date)}, {b.slot}</dd>
        <dt>Address</dt><dd>{b.address}{b.landmark ? ` (near ${b.landmark})` : ''}{b.city ? `, ${b.city}` : ''}</dd>
        {showCustomer && <><dt>Customer</dt><dd>{b.user_name} · <a href={`tel:${b.contact}`}>{b.contact}</a><br /><span className="small muted">{b.user_email}</span></dd></>}
        {!showCustomer && <><dt>Contact</dt><dd>{b.contact}</dd></>}
        <dt>Provider</dt><dd>{b.provider_name ? <>{b.provider_name} {b.provider_mobile && <a href={`tel:${b.provider_mobile}`}>· {b.provider_mobile}</a>}</> : 'Not assigned yet'}</dd>
        {b.notes && <><dt>Notes</dt><dd>{b.notes}</dd></>}
        {b.payment_id && <><dt>Payment ID</dt><dd className="small">{b.payment_id}</dd></>}
      </dl>
      <h3 style={{ marginTop: '1.25rem' }}>Progress</h3>
      <ul className="timeline">
        {(b.history || []).map((h, i) => (
          <li key={i}><strong>{h.status}</strong> <span className="small muted">· {fmtDateTime(h.at)}{h.by && h.by !== 'system' ? ` · ${h.by}` : ''}</span></li>
        ))}
      </ul>
    </Modal>
  );
}
