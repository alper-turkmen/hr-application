import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Building2, Mail, Lock, LogIn, Loader2 } from 'lucide-react';
import ErrorDisplay from './ErrorDisplay';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      if (err.message.includes('Backend server is not available')) {
        setError('Backend server is not available. Please ensure the Django server is running on http://127.0.0.1:8000');
      } else if (err.message.includes('CORS')) {
        setError('CORS error: Please configure CORS settings in your Django backend');
      } else {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
      </div>
      
      <div className="login-content">
        <div className="login-card">
          <div className="login-header">
            <div className="login-brand">
              <h1 className="login-brand-text">WiseHire</h1>
            </div>
            <p className="login-subtitle">Welcome</p>
          </div>

          <div className="login-form-container">
            <ErrorDisplay error={error} />
            
            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group-modern">
                <label className="form-label-modern">
                  <Mail size={16} />
                  Email Address
                </label>
                <input
                  type="email"
                  className="form-control-modern"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div className="form-group-modern">
                <label className="form-label-modern">
                  <Lock size={16} />
                  Password
                </label>
                <input
                  type="password"
                  className="form-control-modern"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                />
              </div>

              <button
                type="submit"
                className="btn-modern btn-modern-primary "
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="spinner-modern" />
                    Signing in...
                  </>
                ) : (
                  <>
                    <LogIn size={18} />
                    Sign In
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="login-footer">
            <p className="login-footer-text">
              HR Management
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;