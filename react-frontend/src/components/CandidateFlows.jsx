import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/api';

const CandidateFlows = () => {
  const [flows, setFlows] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [jobPostings, setJobPostings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingFlow, setEditingFlow] = useState(null);
  const [filters, setFilters] = useState({
    candidate: '',
    job_posting: '',
    flow_status: ''
  });
  const [formData, setFormData] = useState({
    candidate: '',
    job_posting: '',
    flow_status: 'active',
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadFlows();
  }, [filters]);

  const loadData = async () => {
    try {
      const [candidatesResponse, jobsResponse] = await Promise.all([
        apiService.getCandidates(),
        apiService.getJobPostings()
      ]);
      setCandidates(candidatesResponse.results || []);
      setJobPostings(jobsResponse.results || []);
      loadFlows();
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFlows = async () => {
    try {
      const cleanFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== '')
      );
      const response = await apiService.getCandidateFlows(cleanFilters);
      setFlows(response.results || []);
    } catch (error) {
      console.error('Error loading flows:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        candidate: parseInt(formData.candidate),
        job_posting: parseInt(formData.job_posting)
      };
      
      if (editingFlow) {
        await apiService.updateCandidateFlow(editingFlow.id, submitData);
      } else {
        await apiService.createCandidateFlow(submitData);
      }
      setShowModal(false);
      setEditingFlow(null);
      resetForm();
      loadFlows();
    } catch (error) {
      console.error('Error saving flow:', error);
    }
  };

  const handleEdit = (flow) => {
    setEditingFlow(flow);
    setFormData({
      candidate: flow.candidate,
      job_posting: flow.job_posting,
      flow_status: flow.flow_status,
      notes: flow.notes || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure?')) {
      try {
        await apiService.deleteCandidateFlow(id);
        loadFlows();
      } catch (error) {
        console.error('Error deleting flow:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      candidate: '',
      job_posting: '',
      flow_status: 'active',
      notes: ''
    });
  };

  const openAddModal = () => {
    setEditingFlow(null);
    resetForm();
    setShowModal(true);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      candidate: '',
      job_posting: '',
      flow_status: ''
    });
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'active': return 'bg-success';
      case 'completed': return 'bg-primary';
      case 'rejected': return 'bg-danger';
      case 'on_hold': return 'bg-warning';
      default: return 'bg-secondary';
    }
  };

  if (loading) return <div className="text-center">Loading...</div>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Candidate Flows</h2>
        <button className="btn btn-primary" onClick={openAddModal}>
          Start New Flow
        </button>
      </div>

      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Filters</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-3">
              <label className="form-label">Candidate</label>
              <select
                className="form-select"
                value={filters.candidate}
                onChange={(e) => handleFilterChange('candidate', e.target.value)}
              >
                <option value="">All Candidates</option>
                {candidates.map(candidate => (
                  <option key={candidate.id} value={candidate.id}>
                    {candidate.first_name} {candidate.last_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Job Posting</label>
              <select
                className="form-select"
                value={filters.job_posting}
                onChange={(e) => handleFilterChange('job_posting', e.target.value)}
              >
                <option value="">All Jobs</option>
                {jobPostings.map(job => (
                  <option key={job.id} value={job.id}>
                    {job.title} ({job.code})
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Status</label>
              <select
                className="form-select"
                value={filters.flow_status}
                onChange={(e) => handleFilterChange('flow_status', e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="rejected">Rejected</option>
                <option value="on_hold">On Hold</option>
              </select>
            </div>
            <div className="col-md-3 d-flex align-items-end">
              <button className="btn btn-outline-secondary" onClick={clearFilters}>
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Job Posting</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {flows.map(flow => (
              <tr key={flow.id}>
                <td>
                  <div>
                    <strong>{flow.candidate_name}</strong><br/>
                    <small className="text-muted">{flow.candidate_email}</small>
                  </div>
                </td>
                <td>
                  <div>
                    <strong>{flow.job_posting_title}</strong><br/>
                    <small className="text-muted">Code: {flow.job_posting_code}</small>
                  </div>
                </td>
                <td>
                  <span className={`badge ${getStatusBadgeClass(flow.flow_status)}`}>
                    {flow.flow_status.replace('_', ' ').toUpperCase()}
                  </span>
                </td>
                <td>{new Date(flow.created_at).toLocaleDateString()}</td>
                <td>
                  <Link 
                    to={`/dashboard/flows/${flow.id}/activities`}
                    className="btn btn-sm btn-outline-info me-2"
                  >
                    Activities
                  </Link>
                  <button 
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => handleEdit(flow)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(flow.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {flows.length === 0 && (
        <div className="text-center py-5">
          <p className="text-muted">No candidate flows found.</p>
        </div>
      )}

      {showModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingFlow ? 'Edit Candidate Flow' : 'Start New Candidate Flow'}
                </h5>
                <button 
                  className="btn-close" 
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Candidate</label>
                    <select
                      className="form-select"
                      value={formData.candidate}
                      onChange={(e) => setFormData({...formData, candidate: e.target.value})}
                      required
                    >
                      <option value="">Select Candidate</option>
                      {candidates.map(candidate => (
                        <option key={candidate.id} value={candidate.id}>
                          {candidate.first_name} {candidate.last_name} - {candidate.email}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Job Posting</label>
                    <select
                      className="form-select"
                      value={formData.job_posting}
                      onChange={(e) => setFormData({...formData, job_posting: e.target.value})}
                      required
                    >
                      <option value="">Select Job Posting</option>
                      {jobPostings.map(job => (
                        <option key={job.id} value={job.id}>
                          {job.title} ({job.code}) - {job.customer_company_detail?.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Status</label>
                    <select
                      className="form-select"
                      value={formData.flow_status}
                      onChange={(e) => setFormData({...formData, flow_status: e.target.value})}
                    >
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                      <option value="rejected">Rejected</option>
                      <option value="on_hold">On Hold</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Notes</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      value={formData.notes}
                      onChange={(e) => setFormData({...formData, notes: e.target.value})}
                      placeholder="Optional notes about this candidate flow..."
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={() => setShowModal(false)}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingFlow ? 'Update' : 'Start Flow'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CandidateFlows;