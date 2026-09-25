import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import {
  Snowflake, Paintbrush, Zap, Droplets, Laptop, Scissors, Car, Sparkles, Wrench, X,
} from 'lucide-react';

/* ---------- formatting ---------- */
export const inr = (n) => '₹' + Number(n || 0).toLocaleString('en-IN');
export const fmtDate = (v) => {
  if (!v) return '—';
  const d = /^\d{4}-\d{2}-\d{2}$/.test(v) ? new Date(v + 'T00:00:00') : new Date(v);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
};
export const fmtDateTime = (v) => (v ? new Date(v).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }) : '—');
export const cls = (s) => String(s).replace(/\s+/g, '-');

/* ---------- icons ---------- */
const ICONS = { snowflake: Snowflake, paintbrush: Paintbrush, zap: Zap, droplets: Droplets, laptop: Laptop, scissors: Scissors, car: Car, sparkles: Sparkles, wrench: Wrench };
export const ICON_NAMES = Object.keys(ICONS);
export function ServiceIcon({ name, size = 40 }) {
  const I = ICONS[name] || Wrench;
  return <I size={size} strokeWidth={1.6} aria-hidden="true" />;
}

/* ---------- small components ---------- */
export const Spinner = () => <div className="spinner" role="status" aria-label="Loading" />;
export const Badge = ({ value }) => <span className={`badge ${cls(value)}`}>{value}</span>;

export function Empty({ title, children }) {
  return <div className="empty"><h3>{title}</h3>{children}</div>;
}

export function Stat({ label, value, hint, alertish }) {
  return (
    <div className={`stat ${alertish ? 'alertish' : ''}`}>
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {hint && <div className="hint">{hint}</div>}
    </div>
  );
}

export function Field({ label, hint, children }) {
  return <label className="field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

export function PageHead({ title, sub, children }) {
  return (
    <div className="page-head">
      <div><h1>{title}</h1>{sub && <p>{sub}</p>}</div>
      {children && <div className="row">{children}</div>}
    </div>
  );
}

export function Modal({ title, onClose, children, footer }) {
  const ref = useRef(null);
  useEffect(() => {
    const prev = document.activeElement;
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    ref.current?.focus();
    return () => { document.removeEventListener('keydown', onKey); prev?.focus?.(); };
  }, [onClose]);
  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title} tabIndex={-1} ref={ref}>
        <div className="row between" style={{ flexWrap: 'nowrap' }}>
          <h2>{title}</h2>
          <button className="btn plain sm" onClick={onClose} aria-label="Close"><X size={16} /></button>
        </div>
        {children}
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}

/** Table that turns into stacked label/value cards on phones. cols: [{label, render, className}] */
export function DataTable({ cols, rows, onRow, empty }) {
  if (!rows.length) return empty;
  return (
    <div className="table-wrap">
      <table className="data">
        <thead><tr>{cols.map((c) => <th key={c.label}>{c.label}</th>)}</tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className={onRow ? 'click' : ''} onClick={onRow ? () => onRow(r) : undefined}>
              {cols.map((c) => (
                <td key={c.label} data-label={c.label} className={c.className || ''} onClick={c.stop ? (e) => e.stopPropagation() : undefined}>
                  {c.render(r)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------- toasts ---------- */
const ToastCtx = createContext(() => {});
export const useToast = () => useContext(ToastCtx);
export function ToastProvider({ children }) {
  const [items, setItems] = useState([]);
  const push = useCallback((message, type = '') => {
    const id = Math.random();
    setItems((s) => [...s, { id, message, type }]);
    setTimeout(() => setItems((s) => s.filter((t) => t.id !== id)), 4500);
  }, []);
  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="toasts" aria-live="polite">{items.map((t) => <div key={t.id} className={`toast ${t.type}`}>{t.message}</div>)}</div>
    </ToastCtx.Provider>
  );
}

/* ---------- data loading ---------- */
export function useLoad(fn, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: '' });
  const run = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: '' }));
    fn().then((data) => setState({ data, loading: false, error: '' }))
      .catch((e) => setState({ data: null, loading: false, error: e.message }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(run, [run]);
  return { ...state, reload: run };
}

export function Load({ state, children }) {
  if (state.loading && !state.data) return <Spinner />;
  if (state.error) return <div className="alert error">{state.error} <button className="btn sm plain" onClick={state.reload}>Try again</button></div>;
  return children(state.data);
}

/* ---------- confirm dialog: const [confirmEl, ask] = useConfirm(); if (await ask(title, body, 'Cancel booking')) ... ---------- */
export function useConfirm() {
  const [s, setS] = useState(null);
  const ask = useCallback((title, body, label = 'Confirm', keep = 'Keep it') => new Promise((res) => setS({ title, body, label, keep, res })), []);
  const finish = (v) => { s.res(v); setS(null); };
  const el = s && (
    <Modal title={s.title} onClose={() => finish(false)}
      footer={<><button className="btn plain" onClick={() => finish(false)}>{s.keep}</button><button className="btn danger" onClick={() => finish(true)}>{s.label}</button></>}>
      <p>{s.body}</p>
    </Modal>
  );
  return [el, ask];
}
