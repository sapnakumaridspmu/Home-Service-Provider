import { Link } from 'react-router-dom';
import { inr, ServiceIcon } from './ui';

/** Contents of a service "paint chip": colour block + icon on top, name and price below. */
export function SwatchFace({ s, size = 40 }) {
  return (
    <>
      <div className="swatch-top"><ServiceIcon name={s.icon} size={size} /></div>
      <div className="swatch-body">
        <h3>{s.name}</h3>
        <div className="small muted">from <span className="price" style={{ color: 'var(--ink)' }}>{inr(s.price)}</span></div>
      </div>
    </>
  );
}

export default function Swatch({ s, to = `/services/${s.slug}` }) {
  return <Link to={to} className="swatch" style={{ '--chip': s.color }}><SwatchFace s={s} /></Link>;
}
