import { Navigate, Route, Routes, Link } from 'react-router-dom';
import { RequireRole } from './auth';
import { PublicLayout, DashLayout } from './layouts';
import Home from './pages/Home';
import { Services, ServiceDetail } from './pages/Services';
import { Login, Register, Forgot, Reset } from './pages/AuthPages';
import Book from './pages/Book';
import Profile from './pages/Profile';
import { UserOverview, UserBookings } from './pages/user/UserPages';
import { ProviderOverview, ProviderJobs } from './pages/provider/ProviderPages';
import { AdminOverview } from './pages/admin/AdminOverview';
import { AdminPeople } from './pages/admin/AdminPeople';
import { AdminBookings } from './pages/admin/AdminBookings';
import { AdminPayments } from './pages/admin/AdminPayments';
import { AdminServices } from './pages/admin/AdminServices';

const Guard = ({ role, children }) => <RequireRole roles={[role]}>{children}</RequireRole>;

function NotFound() {
  return (
    <div className="container section">
      <h1>Page not found</h1>
      <p className="muted">The page you're looking for doesn't exist or has moved.</p>
      <Link className="btn" to="/">Back to home</Link>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="services" element={<Services />} />
        <Route path="services/:slug" element={<ServiceDetail />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="forgot-password" element={<Forgot />} />
        <Route path="reset-password" element={<Reset />} />
        <Route path="book/:slug" element={<Guard role="user"><Book /></Guard>} />
        <Route path="*" element={<NotFound />} />
      </Route>

      <Route path="dashboard" element={<Guard role="user"><DashLayout /></Guard>}>
        <Route index element={<UserOverview />} />
        <Route path="bookings" element={<UserBookings />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      <Route path="provider" element={<Guard role="provider"><DashLayout /></Guard>}>
        <Route index element={<ProviderOverview />} />
        <Route path="available" element={<ProviderJobs mode="available" />} />
        <Route path="jobs" element={<ProviderJobs mode="mine" />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      <Route path="admin" element={<Guard role="admin"><DashLayout /></Guard>}>
        <Route index element={<AdminOverview />} />
        <Route path="bookings" element={<AdminBookings />} />
        <Route path="customers" element={<AdminPeople role="user" />} />
        <Route path="providers" element={<AdminPeople role="provider" />} />
        <Route path="payments" element={<AdminPayments />} />
        <Route path="services" element={<AdminServices />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      <Route path="home" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
