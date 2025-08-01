import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Users,
  Briefcase,
  Building2,
  Building,
  GitBranch,
  UserCheck,
  BarChart3,
  LogOut,
  User,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';

const Dashboard = () => {
  const { user, logout, isSuperuser } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  const navigationItems = [
    {
      path: '/dashboard/candidates',
      label: 'Candidates',
      icon: Users,
      show: true
    },
    {
      path: '/dashboard/jobs',
      label: 'Job Postings',
      icon: Briefcase,
      show: true
    },
    {
      path: '/dashboard/companies',
      label: 'Customer Companies',
      icon: Building2,
      show: isSuperuser
    },
    {
      path: '/dashboard/hr-companies',
      label: 'HR Companies',
      icon: Building,
      show: isSuperuser
    },
    {
      path: '/dashboard/flows',
      label: 'Candidate Flows',
      icon: GitBranch,
      show: true
    },
    {
      path: '/dashboard/hr-users',
      label: 'HR Users',
      icon: UserCheck,
      show: isSuperuser
    },
    {
      path: '/dashboard/reports',
      label: 'Reports',
      icon: BarChart3,
      show: isSuperuser
    }
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className="d-flex flex-column full-height">
      <nav className="modern-navbar">
        <div className="modern-navbar-container">
          <Link className="modern-navbar-brand" to="/dashboard">
            <div className="brand-icon">
              <Building2 size={24} />
            </div>
            <span className="brand-text">WiseHire</span>
          </Link>

          <div className="modern-navbar-nav desktop-nav">
            {navigationItems.filter(item => item.show).map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  className={`modern-nav-link ${isActive(item.path) ? 'active' : ''}`}
                  to={item.path}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          <div className="modern-navbar-user">
            <div className="user-info">
              <div className="user-avatar">
                <User size={18} />
              </div>
              <span className="user-name">
                {user?.first_name || user?.username}
              </span>
            </div>
            <button className="btn-modern btn-modern-secondary logout-btn" onClick={logout}>
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>

          <button className="mobile-menu-btn" onClick={toggleMobileMenu}>
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {isMobileMenuOpen && (
          <div className="mobile-nav">
            {navigationItems.filter(item => item.show).map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  className={`mobile-nav-link ${isActive(item.path) ? 'active' : ''}`}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
            <div className="mobile-user-section">
              <div className="mobile-user-info">
                <User size={18} />
                <span>{user?.first_name || user?.username}</span>
              </div>
              <button className="btn-modern btn-modern-danger" onClick={logout}>
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          </div>
        )}
      </nav>

      <div className="flex-grow-1 dashboard-content">
        <div className="container-fluid py-4">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;