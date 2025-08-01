import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const Activities = () => {
  const { flowId } = useParams();
  const navigate = useNavigate();
  const [flow, setFlow] = useState(null);
  const [activities, setActivities] = useState([]);
  const [activityTypes, setActivityTypes] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingActivity, setEditingActivity] = useState(null);
  const [formData, setFormData] = useState({
    activity_type: '',
    status: '',
    notes: ''
  });

  useEffect(() => {
    if (flowId) {
      loadData();
    }
  }, [flowId]);

  useEffect(() => {
    if (formData.activity_type) {
      loadStatusesForActivityType(formData.activity_type);
    }
  }, [formData.activity_type]);

  const loadData = async () => {
    try {
      const [flowResponse, activitiesResponse, activityTypesResponse] = await Promise.all([
        apiService.getCandidateFlow(flowId),
        apiService.getActivities({ candidate_flow: flowId }),
        apiService.getActivityTypes()
      ]);
      
      setFlow(flowResponse);
      setActivities(activitiesResponse.results || []);
      setActivityTypes(activityTypesResponse.results || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatusesForActivityType = async (activityTypeId) => {
    try {
      const response = await apiService.getStatuses(activityTypeId);
      setStatuses(response.results || []);
    } catch (error) {
      console.error('Error loading statuses:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        candidate_flow: parseInt(flowId),
        activity_type: parseInt(formData.activity_type),
        status: parseInt(formData.status)
      };
      
      if (editingActivity) {
        await apiService.updateActivity(editingActivity.id, submitData);
      } else {
        await apiService.createActivity(submitData);
      }
      setShowModal(false);
      setEditingActivity(null);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Error saving activity:', error);
    }
  };

  const handleEdit = (activity) => {
    setEditingActivity(activity);
    setFormData({
      activity_type: activity.activity_type,
      status: activity.status,
      notes: activity.notes || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure?')) {
      try {
        await apiService.deleteActivity(id);
        loadData();
      } catch (error) {
        console.error('Error deleting activity:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      activity_type: '',
      status: '',
      notes: ''
    });
    setStatuses([]);
  };

  const openAddModal = () => {
    setEditingActivity(null);
    resetForm();
    setShowModal(true);
  };

  const getActivityTypeOptions = () => {
    return [
      { id: 1, name: 'Phone Call' },
      { id: 2, name: 'Email Sent' },
      { id: 3, name: 'Test Sent' }
    ];
  };

  const getStatusOptions = (activityTypeId) => {
    const statusMap = {
      1: [ // Phone Call
        { id: 1, name: 'Activity Completed' },
        { id: 2, name: 'Positive' },
        { id: 3, name: 'Negative' },
        { id: 4, name: 'Unreachable' },
        { id: 5, name: 'Candidate wants to work in different field' }
      ],
      2: [ // Email Sent
        { id: 6, name: 'Activity Completed' },
        { id: 7, name: 'Positive' },
        { id: 8, name: 'Negative' },
        { id: 9, name: 'Revision email sent' }
      ],
      3: [ // Test Sent
        { id: 10, name: 'Activity Completed' },
        { id: 11, name: 'Successful' },
        { id: 12, name: 'Failed' }
      ]
    };
    return statusMap[activityTypeId] || [];
  };

  if (loading) return <div className="text-center">Loading...</div>;
  if (!flow) return <div className="text-center">Flow not found</div>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>Activities</h2>
          <p className="text-muted mb-0">
            {flow.candidate_detail?.first_name} {flow.candidate_detail?.last_name} - {flow.job_posting_detail?.title}
          </p>
        </div>
        <div>
          <button className="btn btn-primary me-2" onClick={openAddModal}>
            Add Activity
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/dashboard/flows')}>
            Back to Flows
          </button>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Candidate Information</h5>
            </div>
            <div className="card-body">
              <p><strong>Name:</strong> {flow.candidate_detail?.first_name} {flow.candidate_detail?.last_name}</p>
              <p><strong>Email:</strong> {flow.candidate_detail?.email}</p>
              <p><strong>Phone:</strong> {flow.candidate_detail?.phone}</p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Job Information</h5>
            </div>
            <div className="card-body">
              <p><strong>Title:</strong> {flow.job_posting_detail?.title}</p>
              <p><strong>Code:</strong> {flow.job_posting_detail?.code}</p>
              <p><strong>Company:</strong> {flow.job_posting_detail?.customer_company_detail?.name}</p>
              <p><strong>Flow Status:</strong> 
                <span className={`badge ms-2 ${
                  flow.flow_status === 'active' ? 'bg-success' :
                  flow.flow_status === 'completed' ? 'bg-primary' :
                  flow.flow_status === 'rejected' ? 'bg-danger' : 'bg-warning'
                }`}>
                  {flow.flow_status?.replace('_', ' ').toUpperCase()}
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Activity Timeline</h5>
        </div>
        <div className="card-body">
          {activities.length === 0 ? (
            <p className="text-muted">No activities recorded yet.</p>
          ) : (
            <div className="timeline">
              {activities.map((activity, index) => (
                <div key={activity.id} className="timeline-item mb-4">
                  <div className="d-flex">
                    <div className="timeline-marker me-3">
                      <div className="bg-primary rounded-circle" style={{ width: '12px', height: '12px' }}></div>
                    </div>
                    <div className="flex-grow-1">
                      <div className="card">
                        <div className="card-body">
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h6 className="card-title mb-1">
                                {activity.activity_type_detail?.name || `Activity Type ${activity.activity_type}`}
                              </h6>
                              <p className="card-text mb-2">
                                <span className="badge bg-info me-2">
                                  {activity.status_detail?.name || `Status ${activity.status}`}
                                </span>
                                <small className="text-muted">
                                  {new Date(activity.created_at).toLocaleString()}
                                </small>
                              </p>
                              {activity.notes && (
                                <p className="card-text">{activity.notes}</p>
                              )}
                              <small className="text-muted">
                                By: {activity.created_by_detail?.first_name} {activity.created_by_detail?.last_name}
                              </small>
                            </div>
                            <div>
                              <button 
                                className="btn btn-sm btn-outline-primary me-2"
                                onClick={() => handleEdit(activity)}
                              >
                                Edit
                              </button>
                              <button 
                                className="btn btn-sm btn-outline-danger"
                                onClick={() => handleDelete(activity.id)}
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingActivity ? 'Edit Activity' : 'Add Activity'}
                </h5>
                <button 
                  className="btn-close" 
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Activity Type</label>
                    <select
                      className="form-select"
                      value={formData.activity_type}
                      onChange={(e) => setFormData({...formData, activity_type: e.target.value, status: ''})}
                      required
                    >
                      <option value="">Select Activity Type</option>
                      {getActivityTypeOptions().map(type => (
                        <option key={type.id} value={type.id}>
                          {type.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  {formData.activity_type && (
                    <div className="mb-3">
                      <label className="form-label">Status</label>
                      <select
                        className="form-select"
                        value={formData.status}
                        onChange={(e) => setFormData({...formData, status: e.target.value})}
                        required
                      >
                        <option value="">Select Status</option>
                        {getStatusOptions(parseInt(formData.activity_type)).map(status => (
                          <option key={status.id} value={status.id}>
                            {status.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  
                  <div className="mb-3">
                    <label className="form-label">Notes</label>
                    <textarea
                      className="form-control"
                      rows="4"
                      value={formData.notes}
                      onChange={(e) => setFormData({...formData, notes: e.target.value})}
                      placeholder="Add any additional notes about this activity..."
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
                    {editingActivity ? 'Update' : 'Add'} Activity
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

export default Activities;