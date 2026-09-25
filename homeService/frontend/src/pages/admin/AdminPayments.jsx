import { api } from '../../api';
import { Badge, DataTable, Empty, fmtDateTime, inr, Load, PageHead, useLoad } from '../../ui';

export function AdminPayments() {
  const st = useLoad(() => api('/admin/payments'));
  const cols = [
    { label: 'Date', render: (p) => fmtDateTime(p.created_at), className: 'nowrap' },
    { label: 'Customer', render: (p) => p.user_name },
    { label: 'Service', render: (p) => p.service_name },
    { label: 'Amount', render: (p) => <strong>{inr(p.amount)}</strong> },
    { label: 'Status', render: (p) => <Badge value={p.status} /> },
    { label: 'Gateway', render: (p) => p.gateway },
    { label: 'Payment ID', render: (p) => <span className="small">{p.payment_id || p.order_id}</span> },
  ];
  return (
    <>
      <PageHead title="Payments" sub="Every payment attempt. “created” means the customer started but didn't finish paying." />
      <Load state={st}>{({ payments }) => <DataTable cols={cols} rows={payments} empty={<Empty title="No payments yet">Payments appear here as soon as a customer starts checkout.</Empty>} />}</Load>
    </>
  );
}
