import { useState, useEffect } from 'react';
import apiService from '../services/api';
import ErrorDisplay from './ErrorDisplay';
import { useAuth } from '../contexts/AuthContext';

const HRUsers = () => {
  const { isSuperuser } = useAuth();
  const [users, setUsers] = useState([]);
  const [hrCompanies, setHrCompanies] = useState([]);
  const [customerCompanies, setCustomerCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    password: '',
    password_confirm: '',
    hr_company: '',
    authorized_customer_companies: [],
    is_active: true,
    is_staff: false,
    is_superuser: false
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [usersResponse, hrCompaniesResponse, customerCompaniesResponse] = await Promise.all([
        apiService.getHRUsers(),
        apiService.getHRCompanies(),
        apiService.getCustomerCompanies()
      ]);
      setUsers(usersResponse.results || []);
      setHrCompanies(hrCompaniesResponse.results || []);
      setCustomerCompanies(customerCompaniesResponse.results || []);
    } catch (error) {
      console.error('Error loading data:', error);
      setError(error);
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
        hr_company: formData.hr_company ? parseInt(formData.hr_company) : null,
        authorized_customer_companies: formData.authorized_customer_companies.map(id => parseInt(id))
      };

      if (editingUser) {
        if (!submitData.password) {
          delete submitData.password;
          delete submitData.password_confirm;
        }
        await apiService.updateHRUser(editingUser.id, submitData);
      } else {
        await apiService.createHRUser(submitData);
      }
      setShowModal(false);
      setEditingUser(null);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Error saving user:', error);
      setError(error);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      phone: user.phone || '',
      password: '',
      password_confirm: '',
      hr_company: user.hr_company || '',
      authorized_customer_companies: user.authorized_customer_companies || [],
      is_active: user.is_active,
      is_staff: user.is_staff,
      is_superuser: user.is_superuser
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await apiService.deleteHRUser(id);
        loadData();
      } catch (error) {
        console.error('Error deleting user:', error);
        setError(error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      phone: '',
      password: '',
      password_confirm: '',
      hr_company: '',
      authorized_customer_companies: [],
      is_active: true,
      is_staff: false,
      is_superuser: false
    });
  };

  const openAddModal = () => {
    setEditingUser(null);
    setError(null);
    resetForm();
    setShowModal(true);
  };

  const handleCompanySelection = (companyId, isSelected) => {
    if (isSelected) {
      setFormData({
        ...formData,
        authorized_customer_companies: [...formData.authorized_customer_companies, companyId]
      });
    } else {
      setFormData({
        ...formData,
        authorized_customer_companies: formData.authorized_customer_companies.filter(id => id !== companyId)
      });
    }
  };

  if (loading) return <div className="text-center">Loading...</div>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>HR Users</h2>
        {isSuperuser && (
          <button className="btn btn-primary" onClick={openAddModal}>
            Add User
          </button>
        )}
      </div>

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              <th>Email</th>
              <th>HR Company</th>
              <th>Status</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.username}</td>
                <td>{user.first_name} {user.last_name}</td>
                <td>{user.email}</td>
                <td>{user.hr_company_detail?.name || 'N/A'}</td>
                <td>
                  <span className={`badge ${user.is_active ? 'bg-success' : 'bg-secondary'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  {user.is_superuser ? (
                    <span className="badge bg-danger">Super Admin</span>
                  ) : user.is_staff ? (
                    <span className="badge bg-warning">Staff</span>
                  ) : (
                    <span className="badge bg-info">User</span>
                  )}
                </td>
                <td>
                  {isSuperuser ? (
                    <>
                      <button
                        className="btn btn-sm btn-outline-primary me-2"
                        onClick={() => handleEdit(user)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => handleDelete(user.id)}
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

      {users.length === 0 && (
        <div className="text-center py-5">
          <p className="text-muted">No users found.</p>
        </div>
      )}

      {showModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingUser ? 'Edit User' : 'Add User'}
                </h5>
                <button 
                  className="btn-close" 
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <ErrorDisplay error={error} />
                  
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Username</label>
                        <input
                          type="text"
                          className="form-control"
                          value={formData.username}
                          onChange={(e) => setFormData({...formData, username: e.target.value})}
                          required
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Email</label>
                        <input
                          type="email"
                          className="form-control"
                          value={formData.email}
                          onChange={(e) => setFormData({...formData, email: e.target.value})}
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">First Name</label>
                        <input
                          type="text"
                          className="form-control"
                          value={formData.first_name}
                          onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Last Name</label>
                        <input
                          type="text"
                          className="form-control"
                          value={formData.last_name}
                          onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Phone</label>
                        <input
                          type="text"
                          className="form-control"
                          value={formData.phone}
                          onChange={(e) => setFormData({...formData, phone: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">HR Company</label>
                        <select
                          className="form-select"
                          value={formData.hr_company}
                          onChange={(e) => setFormData({...formData, hr_company: e.target.value})}
                        >
                          <option value="">Select HR Company</option>
                          {hrCompanies.map(company => (
                            <option key={company.id} value={company.id}>
                              {company.name}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {!editingUser && (
                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Password</label>
                          <input
                            type="password"
                            className="form-control"
                            value={formData.password}
                            onChange={(e) => setFormData({...formData, password: e.target.value})}
                            required={!editingUser}
                            minLength="8"
                          />
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Confirm Password</label>
                          <input
                            type="password"
                            className="form-control"
                            value={formData.password_confirm}
                            onChange={(e) => setFormData({...formData, password_confirm: e.target.value})}
                            required={!editingUser}
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="mb-3">
                    <label className="form-label">Authorized Customer Companies</label>
                    <div className="border rounded p-3" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                      {customerCompanies.map(company => (
                        <div key={company.id} className="form-check">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id={`company-${company.id}`}
                            checked={formData.authorized_customer_companies.includes(company.id)}
                            onChange={(e) => handleCompanySelection(company.id, e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor={`company-${company.id}`}>
                            {company.name} ({company.code})
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="row">
                    <div className="col-md-4">
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
                    <div className="col-md-4">
                      <div className="mb-3 form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          id="is_staff"
                          checked={formData.is_staff}
                          onChange={(e) => setFormData({...formData, is_staff: e.target.checked})}
                        />
                        <label className="form-check-label" htmlFor="is_staff">
                          Staff
                        </label>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="mb-3 form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          id="is_superuser"
                          checked={formData.is_superuser}
                          onChange={(e) => setFormData({...formData, is_superuser: e.target.checked})}
                        />
                        <label className="form-check-label" htmlFor="is_superuser">
                          Super User
                        </label>
                      </div>
                    </div>
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
                    {editingUser ? 'Update' : 'Create'}
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

export default HRUsers;