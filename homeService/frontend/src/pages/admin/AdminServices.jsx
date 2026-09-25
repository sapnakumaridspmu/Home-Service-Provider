import { useState } from 'react';
import { api } from '../../api';
import { Badge, DataTable, Field, ICON_NAMES, inr, Load, Modal, PageHead, ServiceIcon, useLoad, useToast } from '../../ui';

const BLANK = { name: '', price: '', duration: '60–90 min', description: '', icon: 'wrench', color: '#d6e2fb', image: '', active: true };

export function AdminServices() {
  const st = useLoad(() => api('/admin/services'));
  const toast = useToast();
  const [edit, setEdit] = useState(null);
  const [err, setErr] = useState('');

  const save = async (e) => {
    e.preventDefault(); setErr('');
    const body = { ...edit, price: Number(edit.price) };
    try {
      await (edit.id ? api(`/admin/services/${edit.id}`, { method: 'PUT', body }) : api('/admin/services', { method: 'POST', body }));
      toast('Service saved.', 'ok'); setEdit(null); st.reload();
    } catch (ex) { setErr(ex.message); }
  };
  const toggle = async (s) => {
    try { await api(`/admin/services/${s.id}`, { method: 'PUT', body: { active: !s.active } }); } catch (e) { toast(e.message, 'error'); }
    st.reload();
  };
  const set = (k) => (e) => setEdit({ ...edit, [k]: e.target.value });

  const cols = [
    { label: 'Service', render: (s) => <span className="row" style={{ gap: '.6rem', flexWrap: 'nowrap' }}><span style={{ background: s.color, borderRadius: 8, padding: 6, display: 'inline-grid' }}><ServiceIcon name={s.icon} size={20} /></span><strong>{s.name}</strong></span> },
    { label: 'Price', render: (s) => inr(s.price) },
    { label: 'Duration', render: (s) => s.duration },
    { label: 'Status', render: (s) => <Badge value={s.active ? 'active' : 'inactive'} /> },
    { label: 'Actions', className: 'no-label', render: (s) => (
      <span className="row" style={{ gap: '.4rem', justifyContent: 'flex-end' }}>
        <button className="btn plain sm" onClick={() => { setErr(''); setEdit(s); }}>Edit</button>
        <button className="btn plain sm" onClick={() => toggle(s)}>{s.active ? 'Hide' : 'Show'}</button>
      </span>) },
  ];

  return (
    <>
      <PageHead title="Services & prices" sub="Prices are always taken from here when a booking is made.">
        <button className="btn cta" onClick={() => { setErr(''); setEdit(BLANK); }}>Add service</button>
      </PageHead>
      <Load state={st}>{({ services }) => <DataTable cols={cols} rows={services} empty={null} />}</Load>
      {edit && (
        <Modal title={edit.id ? `Edit ${edit.name}` : 'Add a service'} onClose={() => setEdit(null)}>
          <form onSubmit={save}>
            {err && <div className="alert error" role="alert">{err}</div>}
            <Field label="Name"><input required value={edit.name} onChange={set('name')} /></Field>
            <div className="form-grid">
              <Field label="Price (₹)"><input required type="number" min="1" step="1" value={edit.price} onChange={set('price')} /></Field>
              <Field label="Typical duration"><input value={edit.duration} onChange={set('duration')} /></Field>
            </div>
            <Field label="Description"><textarea value={edit.description} onChange={set('description')} /></Field>
            <div className="form-grid">
              <Field label="Icon"><select value={edit.icon} onChange={set('icon')}>{ICON_NAMES.map((i) => <option key={i}>{i}</option>)}</select></Field>
              <Field label="Card colour"><input type="color" value={edit.color} onChange={set('color')} /></Field>
            </div>
            <Field label="Image path" hint="e.g. /img/plumber.jpg — files live in frontend/public/img."><input value={edit.image} onChange={set('image')} /></Field>
            <div className="modal-foot"><button type="button" className="btn plain" onClick={() => setEdit(null)}>Cancel</button><button className="btn">Save service</button></div>
          </form>
        </Modal>
      )}
    </>
  );
}
