import { useState, useEffect } from 'react';
import apiService from '../services/api';
import ErrorDisplay from './ErrorDisplay';
import { useAuth } from '../contexts/AuthContext';

const Reports = () => {
  const { isSuperuser } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    report_type: 'weekly_activity',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const response = await apiService.getReports();
      setReports(response.results || []);
    } catch (error) {
      console.error('Error loading reports:', error);
      setError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      await apiService.createReport(formData);
      setShowModal(false);
      resetForm();
      loadReports();
    } catch (error) {
      console.error('Error creating report:', error);
      setError(error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      try {
        await apiService.deleteReport(id);
        loadReports();
      } catch (error) {
        console.error('Error deleting report:', error);
        setError(error);
      }
    }
  };

  const handleDownload = async (report) => {
    if (report.status !== 'completed') {
      alert('Report is not ready for download yet.');
      return;
    }
    
    try {
      const response = await apiService.downloadReport(report.id);
      
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `report_${report.id}_${report.report_type}.pdf`; 
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error downloading report:', error);
      setError(error);
    }
  };

  const handleGenerateWeekly = async () => {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - 7);
      
      await apiService.generateWeeklyReport({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        report_type: 'weekly_activity'
      });
      loadReports();
    } catch (error) {
      console.error('Error generating weekly report:', error);
      setError(error);
    }
  };

  const handleGenerateMonthly = async () => {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setMonth(endDate.getMonth() - 1);
      
      await apiService.generateMonthlyReport({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        report_type: 'monthly_activity'
      });
      loadReports();
    } catch (error) {
      console.error('Error generating monthly report:', error);
      setError(error);
    }
  };

  const resetForm = () => {
    setFormData({
      report_type: 'weekly_activity',
      start_date: '',
      end_date: ''
    });
  };

  const openAddModal = () => {
    setError(null);
    resetForm();
    setShowModal(true);
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'completed': return 'bg-success';
      case 'generating': return 'bg-warning';
      case 'pending': return 'bg-info';
      case 'failed': return 'bg-danger';
      default: return 'bg-secondary';
    }
  };

  const getReportTypeDisplay = (type) => {
    switch (type) {
      case 'weekly_activity': return 'Weekly Activity Report';
      case 'monthly_activity': return 'Monthly Activity Report';
      default: return type;
    }
  };

  if (loading) return <div className="text-center">Loading...</div>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Reports</h2>
        {isSuperuser && (
          <div>
            <button className="btn btn-outline-primary me-2" onClick={handleGenerateWeekly}>
              Generate Weekly Report
            </button>
            <button className="btn btn-outline-primary me-2" onClick={handleGenerateMonthly}>
              Generate Monthly Report
            </button>
            <button className="btn btn-primary" onClick={openAddModal}>
              Custom Report
            </button>
          </div>
        )}
      </div>

      <ErrorDisplay error={error} />

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Report Type</th>
              <th>Period</th>
              <th>Status</th>
              <th>Generated</th>
              <th>Completed</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(report => (
              <tr key={report.id}>
                <td>{getReportTypeDisplay(report.report_type)}</td>
                <td>
                  {new Date(report.start_date).toLocaleDateString()} - {new Date(report.end_date).toLocaleDateString()}
                </td>
                <td>
                  <span className={`badge ${getStatusBadgeClass(report.status)}`}>
                    {report.status_display || report.status}
                  </span>
                </td>
                <td>{new Date(report.generated_at).toLocaleString()}</td>
                <td>
                  {report.completed_at ? new Date(report.completed_at).toLocaleString() : 'N/A'}
                </td>
                <td>
                  {report.status === 'completed' && isSuperuser && (
                    <button
                      className="btn btn-sm btn-outline-success me-2"
                      onClick={() => handleDownload(report)}
                    >
                      Download
                    </button>
                  )}
                  {isSuperuser ? (
                    <button
                      className="btn btn-sm btn-outline-danger"
                      onClick={() => handleDelete(report.id)}
                    >
                      Delete
                    </button>
                  ) : (
                    <span className="text-muted">View Only</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {reports.length === 0 && (
        <div className="text-center py-5">
          <p className="text-muted">No reports found.</p>
          <p className="text-muted">Generate your first report using the buttons above.</p>
        </div>
      )}

      {showModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Generate Custom Report</h5>
                <button 
                  className="btn-close" 
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <ErrorDisplay error={error} />
                  
                  <div className="mb-3">
                    <label className="form-label">Report Type</label>
                    <select
                      className="form-select"
                      value={formData.report_type}
                      onChange={(e) => setFormData({...formData, report_type: e.target.value})}
                      required
                    >
                      <option value="weekly_activity">Weekly Activity Report</option>
                      <option value="monthly_activity">Monthly Activity Report</option>
                    </select>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Start Date</label>
                    <input
                      type="date"
                      className="form-control"
                      value={formData.start_date}
                      onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">End Date</label>
                    <input
                      type="date"
                      className="form-control"
                      value={formData.end_date}
                      onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                      required
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
                    Generate Report
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

export default Reports;