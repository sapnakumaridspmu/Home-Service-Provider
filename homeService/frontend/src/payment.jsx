import { useCallback, useState } from 'react';
import { api } from './api';
import { inr, Modal } from './ui';

let rzpLoading = null;
function loadRazorpay() {
  if (window.Razorpay) return Promise.resolve();
  rzpLoading ||= new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = 'https://checkout.razorpay.com/v1/checkout.js';
    s.onload = resolve;
    s.onerror = () => { rzpLoading = null; reject(new Error('Could not load the payment window. Check your connection.')); };
    document.body.appendChild(s);
  });
  return rzpLoading;
}

/**
 * usePayment() -> { pay(booking), modal }
 *   pay() resolves { paid: true, booking } or { paid: false } if the customer closed the window.
 *   Render {modal} once in the component (only used in demo mode).
 */
export function usePayment() {
  const [demo, setDemo] = useState(null);

  const pay = useCallback(async (booking) => {
    const order = await api('/payments/create-order', { method: 'POST', body: { booking_id: booking.id } });

    if (order.mode === 'demo') {
      return new Promise((resolve) => setDemo({ order, booking, resolve }));
    }

    await loadRazorpay();
    return new Promise((resolve, reject) => {
      const rzp = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: 'Home Service Provider',
        description: booking.service_name,
        prefill: order.prefill,
        theme: { color: '#0d6b6f' },
        // The signature is verified on the server — the browser can't mark a booking paid by itself.
        handler: async (resp) => {
          try {
            const v = await api('/payments/verify', { method: 'POST', body: resp });
            resolve({ paid: true, booking: v.booking });
          } catch (e) { reject(e); }
        },
        modal: { ondismiss: () => resolve({ paid: false }) },
      });
      rzp.open(); // failed attempts are shown (and retryable) inside Razorpay's own window
    });
  }, []);

  const modal = demo && <DemoPay {...demo} close={() => setDemo(null)} />;
  return { pay, modal };
}

function DemoPay({ order, booking, resolve, close }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const done = (r) => { close(); resolve(r); };
  const confirm = async () => {
    setBusy(true); setError('');
    try {
      const r = await api('/payments/demo-pay', { method: 'POST', body: { order_id: order.order_id } });
      done({ paid: true, booking: r.booking });
    } catch (e) { setError(e.message); setBusy(false); }
  };
  return (
    <Modal title="Demo payment" onClose={() => done({ paid: false })}
      footer={<>
        <button className="btn plain" onClick={() => done({ paid: false })}>Cancel</button>
        <button className="btn cta" onClick={confirm} disabled={busy}>{busy ? 'Processing…' : `Pay ${inr(booking.amount)}`}</button>
      </>}>
      <div className="alert info">Test mode: no real money moves. Add your Razorpay keys on the server to switch to live checkout.</div>
      {error && <div className="alert error">{error}</div>}
      <dl className="kv">
        <dt>Service</dt><dd>{booking.service_name}</dd>
        <dt>Amount</dt><dd>{inr(booking.amount)}</dd>
        <dt>Order</dt><dd className="small">{order.order_id}</dd>
      </dl>
    </Modal>
  );
}
