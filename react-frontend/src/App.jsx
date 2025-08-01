import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Candidates from './components/Candidates';
import CandidateDetail from './components/CandidateDetail';
import JobPostings from './components/JobPostings';
import Companies from './components/Companies';
import HRCompanies from './components/HRCompanies';
import HRUsers from './components/HRUsers';
import Reports from './components/Reports';
import CandidateFlows from './components/CandidateFlows';
import Activities from './components/Activities';
import ProtectedRoute from './components/ProtectedRoute';
import SuperuserRoute from './components/SuperuserRoute';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <div className="full-height">
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }>
              <Route index element={
                <div className="dashboard-welcome">
                  <div className="welcome-header">
                    <h1 className="welcome-title">Welcome to WiseHire</h1>
                    <p className="welcome-subtitle">HR management solution</p>
                  </div>
                  
                  <div className="dashboard-stats">
                    <div className="stat-card">
                    
                      <div className="stat-content">
                        <h3 className="stat-title">Candidates</h3>
                        <p className="stat-description">Manage candidate profiles and applications</p>
                      </div>
                    </div>
                    
                    <div className="stat-card">
                    
                      <div className="stat-content">
                        <h3 className="stat-title">Job Postings</h3>
                        <p className="stat-description">Create and manage job opportunities</p>
                      </div>
                    </div>
                    
                    <div className="stat-card">
                      <div className="stat-content">
                        <h3 className="stat-title">Workflows</h3>
                        <p className="stat-description">Track candidate progress through flows</p>
                      </div>
                    </div>
                  </div>
                  
                  
                </div>
              } />
              <Route path="candidates" element={<Candidates />} />
              <Route path="candidates/:id" element={<CandidateDetail />} />
              <Route path="jobs" element={<JobPostings />} />
              <Route path="companies" element={
                <SuperuserRoute>
                  <Companies />
                </SuperuserRoute>
              } />
              <Route path="hr-companies" element={
                <SuperuserRoute>
                  <HRCompanies />
                </SuperuserRoute>
              } />
              <Route path="hr-users" element={
                <SuperuserRoute>
                  <HRUsers />
                </SuperuserRoute>
              } />
              <Route path="reports" element={
                <SuperuserRoute>
                  <Reports />
                </SuperuserRoute>
              } />
              <Route path="flows" element={<CandidateFlows />} />
              <Route path="flows/:flowId/activities" element={<Activities />} />
            </Route>
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </Router>
      </AuthProvider>
    </div>
  );
}

export default App;
