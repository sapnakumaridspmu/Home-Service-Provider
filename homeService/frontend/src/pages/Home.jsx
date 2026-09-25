import { Link } from 'react-router-dom';
import { ShieldCheck, BadgeIndianRupee, Clock3 } from 'lucide-react';
import { api } from '../api';
import { useAuth, homeFor } from '../auth';
import { Load, useLoad } from '../ui';
import Swatch, { SwatchFace } from '../Swatch';

export default function Home() {
  const { user } = useAuth();
  const svc = useLoad(() => api('/services'));
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <h1>A trusted technician at your door, booked in two minutes.</h1>
            <p className="lead">AC repair, plumbing, electrical, salon and more across Ranchi. Pick a service, see the price up front and pay securely online.</p>
            <div className="actions">
              <Link className="btn cta" to="/services">Book a service</Link>
              {!user && <Link className="btn ghost" to="/register?role=provider">Earn as a provider</Link>}
              {user && <Link className="btn ghost" to={homeFor(user.role)}>Go to my dashboard</Link>}
            </div>
            <div className="hero-proof">
              <span><BadgeIndianRupee size={18} /> Fixed prices</span>
              <span><ShieldCheck size={18} /> Secure online payment</span>
              <span><Clock3 size={18} /> Pick your time slot</span>
            </div>
          </div>
          <div className="fan" aria-hidden="true">
            {(svc.data?.services || []).slice(0, 4).map((s) => (
              <div key={s.id} className="swatch" style={{ '--chip': s.color }}><SwatchFace s={s} /></div>
            ))}
          </div>
        </div>
      </section>

      <section className="section" id="services">
        <div className="container">
          <div className="section-head">
            <h2>What do you need done?</h2>
            <p>Every service has a fixed starting price, so there are no surprises when the technician arrives.</p>
          </div>
          <Load state={svc}>{(d) => <div className="grid-swatches">{d.services.map((s) => <Swatch key={s.id} s={s} />)}</div>}</Load>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-head"><h2>How it works</h2></div>
          <div className="steps">
            <div className="step"><h3>Choose a service and a time</h3><p className="muted">Tell us the address, pick a date and a two-hour slot that suits you.</p></div>
            <div className="step"><h3>Pay securely online</h3><p className="muted">Pay with UPI, card or net banking. Cancel before the job starts and you're refunded.</p></div>
            <div className="step"><h3>A verified provider arrives</h3><p className="muted">A nearby, admin-approved technician accepts your job and you can track it from your dashboard.</p></div>
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="band">
            <div>
              <h2>Are you a technician?</h2>
              <p>Create a provider account, choose the services you offer and pick up paid jobs near you. You keep most of every job's price.</p>
            </div>
            <Link className="btn cta" to="/register?role=provider">Join as a provider</Link>
          </div>
        </div>
      </section>
    </>
  );
}
