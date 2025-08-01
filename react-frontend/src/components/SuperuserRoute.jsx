import { useAuth } from '../contexts/AuthContext';

const SuperuserRoute = ({ children }) => {
  const { user, isSuperuser, loading } = useAuth();

  if (loading) {
    return <div className="text-center">Loading...</div>;
  }

  if (!user) {
    return (
      <div className="alert alert-danger text-center">
        <h4>Access Denied</h4>
        <p>You must be logged in to access this page.</p>
      </div>
    );
  }

  if (!isSuperuser) {
    return (
      <div className="alert alert-danger text-center">
        <h4>Access Denied</h4>
        <p>You must be a superuser to access this page.</p>
        <p className="text-muted">Only superusers can manage HR companies, customer companies, HR users, and system-wide reports.</p>
      </div>
    );
  }

  return children;
};

export default SuperuserRoute;