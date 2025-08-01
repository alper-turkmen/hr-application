import { useState, useEffect } from 'react';
import apiService from '../services/api';
import ErrorDisplay from './ErrorDisplay';

const JobPostings = () => {
  const [jobPostings, setJobPostings] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    code: '',
    description: '',
    customer_company: '',
    closing_date: '',
    status: 'active'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [jobsResponse, companiesResponse] = await Promise.all([
        apiService.getJobPostings(),
        apiService.getCustomerCompanies()
      ]);
      setJobPostings(jobsResponse.results || []);
      setCompanies(companiesResponse.results || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      const submitData = {
        ...formData,
        customer_company: parseInt(formData.customer_company)
      };
      
      if (editingJob) {
        await apiService.updateJobPosting(editingJob.id, submitData);
      } else {
        await apiService.createJobPosting(submitData);
      }
      setShowModal(false);
      setEditingJob(null);
      setFormData({
        title: '',
        code: '',
        description: '',
        customer_company: '',
        closing_date: '',
        status: 'active'
      });
      loadData();
    } catch (error) {
      console.error('Error saving job posting:', error);
      setError(error);
    }
  };

  const handleEdit = (job) => {
    setEditingJob(job);
    setFormData({
      title: job.title,
      code: job.code,
      description: job.description,
      customer_company: job.customer_company,
      closing_date: job.closing_date.split('T')[0],
      status: job.status
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure?')) {
      try {
        await apiService.deleteJobPosting(id);
        loadData();
      } catch (error) {
        console.error('Error deleting job posting:', error);
      }
    }
  };

  const openAddModal = () => {
    setEditingJob(null);
    setError(null);
    setFormData({
      title: '',
      code: '',
      description: '',
      customer_company: '',
      closing_date: '',
      status: 'active'
    });
    setShowModal(true);
  };

  if (loading) return <div className="text-center">Loading...</div>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Job Postings</h2>
        <button className="btn btn-primary" onClick={openAddModal}>
          Add Job Posting
        </button>
      </div>

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Title</th>
              <th>Code</th>
              <th>Company</th>
              <th>Status</th>
              <th>Closing Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobPostings.map(job => (
              <tr key={job.id}>
                <td>{job.title}</td>
                <td>{job.code}</td>
                <td>{job.customer_company_detail?.name}</td>
                <td>
                  <span className={`badge ${job.status === 'active' ? 'bg-success' : 'bg-secondary'}`}>
                    {job.status}
                  </span>
                </td>
                <td>{new Date(job.closing_date).toLocaleDateString()}</td>
                <td>
                  <button 
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => handleEdit(job)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(job.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingJob ? 'Edit Job Posting' : 'Add Job Posting'}
                </h5>
                <button 
                  className="btn-close" 
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <ErrorDisplay error={error} />
                  <div className="mb-3">
                    <label className="form-label">Title</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Code</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.code}
                      onChange={(e) => setFormData({...formData, code: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Company</label>
                    <select
                      className="form-control"
                      value={formData.customer_company}
                      onChange={(e) => setFormData({...formData, customer_company: e.target.value})}
                      required
                    >
                      <option value="">Select Company</option>
                      {companies.map(company => (
                        <option key={company.id} value={company.id}>
                          {company.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Description</label>
                    <textarea
                      className="form-control"
                      rows="4"
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Closing Date</label>
                    <input
                      type="date"
                      className="form-control"
                      value={formData.closing_date}
                      onChange={(e) => setFormData({...formData, closing_date: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Status</label>
                    <select
                      className="form-control"
                      value={formData.status}
                      onChange={(e) => setFormData({...formData, status: e.target.value})}
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
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
                    {editingJob ? 'Update' : 'Create'}
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

export default JobPostings;