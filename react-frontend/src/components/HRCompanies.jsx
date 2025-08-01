import { useState, useEffect } from 'react';
import apiService from '../services/api';
import ErrorDisplay from './ErrorDisplay';
import { useAuth } from '../contexts/AuthContext';

const HRCompanies = () => {
  const { isSuperuser } = useAuth();
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCompany, setEditingCompany] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    is_active: true
  });

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const response = await apiService.getHRCompanies();
      setCompanies(response.results || []);
    } catch (error) {
      console.error('Error loading HR companies:', error);
      setError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      if (editingCompany) {
        await apiService.updateHRCompany(editingCompany.id, formData);
      } else {
        await apiService.createHRCompany(formData);
      }
      setShowModal(false);
      setEditingCompany(null);
      resetForm();
      loadCompanies();
    } catch (error) {
      console.error('Error saving HR company:', error);
      setError(error);
    }
  };

  const handleEdit = (company) => {
    setEditingCompany(company);
    setFormData({
      name: company.name,
      code: company.code,
      is_active: company.is_active
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this HR company?')) {
      try {
        await apiService.deleteHRCompany(id);
        loadCompanies();
      } catch (error) {
        console.error('Error deleting HR company:', error);
        setError(error);
      }
    }
  };

  const handleToggleActive = async (company) => {
    try {
      await apiService.toggleHRCompanyActive(company.id, {
        ...company,
        is_active: !company.is_active
      });
      loadCompanies();
    } catch (error) {
      console.error('Error toggling HR company status:', error);
      setError(error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      is_active: true
    });
  };

  const openAddModal = () => {
    setEditingCompany(null);
    setError(null);
    resetForm();
    setShowModal(true);
  };

  if (loading) return <div className="text-center">Loading...</div>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>HR Companies</h2>
        {isSuperuser && (
          <button className="btn btn-primary" onClick={openAddModal}>
            Add HR Company
          </button>
        )}
      </div>

      <ErrorDisplay error={error} />

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Name</th>
              <th>Code</th>
              <th>Status</th>
              <th>Users Count</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {companies.map(company => (
              <tr key={company.id}>
                <td>{company.name}</td>
                <td>{company.code}</td>
                <td>
                  <span className={`badge ${company.is_active ? 'bg-success' : 'bg-secondary'}`}>
                    {company.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <span className="badge bg-info">
                    {company.hr_users_count || 0} users
                  </span>
                </td>
                <td>{new Date(company.created_at).toLocaleDateString()}</td>
                <td>
                  {isSuperuser ? (
                    <>
                      <button
                        className="btn btn-sm btn-outline-primary me-2"
                        onClick={() => handleEdit(company)}
                      >
                        Edit
                      </button>
                      <button
                        className={`btn btn-sm me-2 ${company.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`}
                        onClick={() => handleToggleActive(company)}
                      >
                        {company.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => handleDelete(company.id)}
                      >
                        Delete
                      </button>
                    </>
                  ) : (
                    <span className="text-muted">View Only</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {companies.length === 0 && (
        <div className="text-center py-5">
          <p className="text-muted">No HR companies found.</p>
        </div>
      )}

      {showModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingCompany ? 'Edit HR Company' : 'Add HR Company'}
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
                    <label className="form-label">Company Name</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                      placeholder="Enter company name"
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Company Code</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.code}
                      onChange={(e) => setFormData({...formData, code: e.target.value})}
                      required
                      placeholder="Enter unique company code"
                    />
                  </div>
                  
                  <div className="mb-3 form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="is_active"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    />
                    <label className="form-check-label" htmlFor="is_active">
                      Active
                    </label>
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
                    {editingCompany ? 'Update' : 'Create'}
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

export default HRCompanies;