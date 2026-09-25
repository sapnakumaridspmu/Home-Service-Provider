import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  Menu, X, LayoutDashboard, CalendarCheck, UserRound, Briefcase, Inbox, Users, HardHat, CreditCard, Wrench, LogOut, ShieldCheck,
} from 'lucide-react';
import { useAuth, homeFor } from './auth';
import { api } from './api';

export function Logo({ light }) {
  return (
    <Link to="/" className="brand" aria-label="Home Service Provider — home">
      <svg width="34" height="34" viewBox="0 0 32 32" aria-hidden="true">
        <rect width="32" height="32" rx="8" fill={light ? '#f4b41a' : '#0d6b6f'} />
        <path d="M6 15.5 16 7l10 8.5V25a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1z" fill={light ? '#14232b' : '#f4b41a'} />
        <path d="m11.5 17.5 3.2 3.2 6-6.2" fill="none" stroke={light ? '#f4b41a' : '#0d6b6f'} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span>Home Service Provider</span>
    </Link>
  );
}

/* ---------------- public site ---------------- */
export function PublicLayout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const loc = useLocation();
  const nav = useNavigate();
  useEffect(() => { setOpen(false); window.scrollTo(0, 0); }, [loc.pathname]);

  return (
    <>
      <a href="#main" className="sr-only">Skip to content</a>
      <header className="site-header">
        <div className="container">
          <Logo />
          <button className="nav-toggle" aria-label="Menu" aria-expanded={open} onClick={() => setOpen(!open)}>
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
          <nav className={`nav ${open ? 'open' : ''}`} aria-label="Main">
            <NavLink className="link" to="/services">Services</NavLink>
            <NavLink className="link" to="/register?role=provider">Become a provider</NavLink>
            {user ? (
              <>
                <Link className="btn sm" to={homeFor(user.role)}>My dashboard</Link>
                <button className="btn sm plain" onClick={() => { logout(); nav('/'); }}>Log out</button>
              </>
            ) : (
              <>
                <Link className="btn sm ghost" to="/login">Log in</Link>
                <Link className="btn sm cta" to="/register">Sign up</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main id="main"><Outlet /></main>
      <footer className="site-footer">
        <div className="container">
          <div className="footer-grid">
            <div>
              <Logo light />
              <p style={{ marginTop: '1rem', maxWidth: '26rem' }}>Find, book and pay for home maintenance and repair services in one place — with verified technicians and fixed prices.</p>
            </div>
            <div>
              <h4>Contact</h4>
              <p>Lalpur, behind Apsara Hotel<br />Ranchi, Jharkhand, India<br />
                <a href="tel:+919335634355">+91 93356 34355</a><br />
                <a href="mailto:homeservices@gmail.com">homeservices@gmail.com</a></p>
            </div>
            <div>
              <h4>Hours</h4>
              <ul><li>Mon–Fri: 8:00 am – 5:00 pm</li><li>Saturday: 8:00 am</li><li>Commercial: open 24/7</li></ul>
            </div>
          </div>
          <div className="copyright">© {new Date().getFullYear()} Home Service Provider. All rights reserved.</div>
        </div>
      </footer>
    </>
  );
}

/* ---------------- dashboards ---------------- */
const NAV = {
  user: [
    { to: '/dashboard', label: 'Overview', icon: LayoutDashboard, end: true },
    { to: '/dashboard/bookings', label: 'My bookings', icon: CalendarCheck },
    { to: '/dashboard/profile', label: 'Profile', icon: UserRound },
  ],
  provider: [
    { to: '/provider', label: 'Overview', icon: LayoutDashboard, end: true },
    { to: '/provider/available', label: 'Available jobs', icon: Inbox },
    { to: '/provider/jobs', label: 'My jobs', icon: Briefcase },
    { to: '/provider/profile', label: 'Profile', icon: UserRound },
  ],
  admin: [
    { to: '/admin', label: 'Overview', icon: LayoutDashboard, end: true },
    { to: '/admin/bookings', label: 'Bookings', icon: CalendarCheck },
    { label: 'People', group: true },
    { to: '/admin/customers', label: 'Service seekers', icon: Users },
    { to: '/admin/providers', label: 'Providers', icon: HardHat, badge: 'pending_providers' },
    { label: 'Business', group: true },
    { to: '/admin/payments', label: 'Payments', icon: CreditCard },
    { to: '/admin/services', label: 'Services', icon: Wrench },
    { to: '/admin/profile', label: 'My account', icon: ShieldCheck },
  ],
};
const TITLES = { user: 'Service seeker', provider: 'Service provider', admin: 'Admin' };

export function DashLayout() {
  const { user, logout, setUser } = useAuth();
  const [open, setOpen] = useState(false);
  const [badges, setBadges] = useState({});
  const loc = useLocation();
  const nav = useNavigate();
  useEffect(() => { setOpen(false); }, [loc.pathname]);
  useEffect(() => {
    if (user.role === 'admin') api('/admin/stats').then((s) => setBadges(s)).catch(() => {});
    // keep provider approval status fresh (an admin may have just approved them)
    if (user.role === 'provider') api('/auth/me').then((r) => setUser(r.user)).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user.role, loc.pathname]);

  return (
    <div className="dash">
      <div className={`scrim ${open ? 'open' : ''}`} onClick={() => setOpen(false)} />
      <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Dashboard menu">
        <Logo light />
        <nav>
          {NAV[user.role].map((n) => n.group
            ? <div key={n.label} className="nav-label">{n.label}</div>
            : (
              <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => `side-link ${isActive ? 'active' : ''}`}>
                <n.icon size={18} aria-hidden="true" /> {n.label}
                {n.badge && badges[n.badge] > 0 && <span className="count" aria-label={`${badges[n.badge]} waiting`}>{badges[n.badge]}</span>}
              </NavLink>
            ))}
        </nav>
        <div className="me">
          <div className="small">{TITLES[user.role]} account</div>
          <strong>{user.name}</strong>
          <div className="small" style={{ wordBreak: 'break-all' }}>{user.email}</div>
          <button className="side-link" style={{ background: 'none', border: 0, width: '100%', cursor: 'pointer', marginTop: '.5rem', padding: '.65rem 0' }}
            onClick={() => { logout(); nav('/login'); }}>
            <LogOut size={18} aria-hidden="true" /> Log out
          </button>
        </div>
      </aside>
      <div className="dash-main">
        <div className="dash-top">
          <button className="menu-btn" aria-label="Open menu" onClick={() => setOpen(true)}><Menu size={20} /></button>
          <strong>{TITLES[user.role]} dashboard</strong>
        </div>
        <div className="dash-content"><Outlet /></div>
      </div>
    </div>
  );
}
