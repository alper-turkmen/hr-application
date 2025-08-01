import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const CandidateDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [educations, setEducations] = useState([]);
  const [workExperiences, setWorkExperiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');
  const [showEducationModal, setShowEducationModal] = useState(false);
  const [showExperienceModal, setShowExperienceModal] = useState(false);
  const [editingEducation, setEditingEducation] = useState(null);
  const [editingExperience, setEditingExperience] = useState(null);

  const [educationForm, setEducationForm] = useState({
    school_name: '',
    department: '',
    degree: '',
    start_date: '',
    end_date: '',
    is_current: false,
    gpa: ''
  });

  const [experienceForm, setExperienceForm] = useState({
    company_name: '',
    position: '',
    description: '',
    start_date: '',
    end_date: '',
    is_current: false
  });

  useEffect(() => {
    if (id) {
      loadCandidateData();
    }
  }, [id]);

  const loadCandidateData = async () => {
    try {
      const [candidateResponse, educationsResponse, experiencesResponse] = await Promise.all([
        apiService.request(`/api/candidates/candidates/${id}/`),
        apiService.getEducations(id),
        apiService.getWorkExperiences(id)
      ]);
      
      setCandidate(candidateResponse);
      setEducations(educationsResponse.results || []);
      setWorkExperiences(experiencesResponse.results || []);
    } catch (error) {
      console.error('Error loading candidate data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEducationSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...educationForm, candidate: parseInt(id) };
      if (editingEducation) {
        await apiService.updateEducation(editingEducation.id, data);
      } else {
        await apiService.createEducation(data);
      }
      setShowEducationModal(false);
      setEditingEducation(null);
      resetEducationForm();
      loadCandidateData();
    } catch (error) {
      console.error('Error saving education:', error);
    }
  };

  const handleExperienceSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...experienceForm, candidate: parseInt(id) };
      if (editingExperience) {
        await apiService.updateWorkExperience(editingExperience.id, data);
      } else {
        await apiService.createWorkExperience(data);
      }
      setShowExperienceModal(false);
      setEditingExperience(null);
      resetExperienceForm();
      loadCandidateData();
    } catch (error) {
      console.error('Error saving experience:', error);
    }
  };

  const resetEducationForm = () => {
    setEducationForm({
      school_name: '',
      department: '',
      degree: '',
      start_date: '',
      end_date: '',
      is_current: false,
      gpa: ''
    });
  };

  const resetExperienceForm = () => {
    setExperienceForm({
      company_name: '',
      position: '',
      description: '',
      start_date: '',
      end_date: '',
      is_current: false
    });
  };

  const editEducation = (education) => {
    setEditingEducation(education);
    setEducationForm({
      school_name: education.school_name,
      department: education.department,
      degree: education.degree,
      start_date: education.start_date,
      end_date: education.end_date || '',
      is_current: education.is_current,
      gpa: education.gpa || ''
    });
    setShowEducationModal(true);
  };

  const editExperience = (experience) => {
    setEditingExperience(experience);
    setExperienceForm({
      company_name: experience.company_name,
      position: experience.position,
      description: experience.description || '',
      start_date: experience.start_date,
      end_date: experience.end_date || '',
      is_current: experience.is_current
    });
    setShowExperienceModal(true);
  };

  const deleteEducation = async (educationId) => {
    if (window.confirm('Are you sure?')) {
      try {
        await apiService.deleteEducation(educationId);
        loadCandidateData();
      } catch (error) {
        console.error('Error deleting education:', error);
      }
    }
  };

  const deleteExperience = async (experienceId) => {
    if (window.confirm('Are you sure?')) {
      try {
        await apiService.deleteWorkExperience(experienceId);
        loadCandidateData();
      } catch (error) {
        console.error('Error deleting experience:', error);
      }
    }
  };

  if (loading) return <div className="text-center">Loading...</div>;
  if (!candidate) return <div className="text-center">Candidate not found</div>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{candidate.first_name} {candidate.last_name}</h2>
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard/candidates')}>
          Back to Candidates
        </button>
      </div>

      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'info' ? 'active' : ''}`}
            onClick={() => setActiveTab('info')}
          >
            Basic Info
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'education' ? 'active' : ''}`}
            onClick={() => setActiveTab('education')}
          >
            Education
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'experience' ? 'active' : ''}`}
            onClick={() => setActiveTab('experience')}
          >
            Work Experience
          </button>
        </li>
      </ul>

      {activeTab === 'info' && (
        <div className="card">
          <div className="card-body">
            <div className="row">
              <div className="col-md-6">
                <p><strong>Email:</strong> {candidate.email}</p>
                <p><strong>Phone:</strong> {candidate.phone}</p>
              </div>
              <div className="col-md-6">
                <p><strong>Address:</strong> {candidate.address || 'Not provided'}</p>
                <p><strong>Status:</strong> 
                  <span className={`badge ms-2 ${candidate.is_active ? 'bg-success' : 'bg-secondary'}`}>
                    {candidate.is_active ? 'Active' : 'Inactive'}
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'education' && (
        <div>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h4>Education</h4>
            <button 
              className="btn btn-primary"
              onClick={() => {
                setEditingEducation(null);
                resetEducationForm();
                setShowEducationModal(true);
              }}
            >
              Add Education
            </button>
          </div>
          
          {educations.length === 0 ? (
            <p className="text-muted">No education records found.</p>
          ) : (
            <div className="row">
              {educations.map(education => (
                <div key={education.id} className="col-md-6 mb-3">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">{education.school_name}</h6>
                      <p className="card-text">
                        <strong>{education.degree}</strong> in {education.department}<br/>
                        {education.start_date} - {education.is_current ? 'Present' : education.end_date}<br/>
                        {education.gpa && <span>GPA: {education.gpa}</span>}
                      </p>
                      <button 
                        className="btn btn-sm btn-outline-primary me-2"
                        onClick={() => editEducation(education)}
                      >
                        Edit
                      </button>
                      <button 
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => deleteEducation(education.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'experience' && (
        <div>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h4>Work Experience</h4>
            <button 
              className="btn btn-primary"
              onClick={() => {
                setEditingExperience(null);
                resetExperienceForm();
                setShowExperienceModal(true);
              }}
            >
              Add Experience
            </button>
          </div>
          
          {workExperiences.length === 0 ? (
            <p className="text-muted">No work experience records found.</p>
          ) : (
            <div className="row">
              {workExperiences.map(experience => (
                <div key={experience.id} className="col-md-6 mb-3">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">{experience.position}</h6>
                      <p className="card-text">
                        <strong>{experience.company_name}</strong><br/>
                        {experience.start_date} - {experience.is_current ? 'Present' : experience.end_date}<br/>
                        {experience.description && <span>{experience.description}</span>}
                      </p>
                      <button 
                        className="btn btn-sm btn-outline-primary me-2"
                        onClick={() => editExperience(experience)}
                      >
                        Edit
                      </button>
                      <button 
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => deleteExperience(experience.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {showEducationModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingEducation ? 'Edit Education' : 'Add Education'}
                </h5>
                <button className="btn-close" onClick={() => setShowEducationModal(false)}></button>
              </div>
              <form onSubmit={handleEducationSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">School Name</label>
                    <input
                      type="text"
                      className="form-control"
                      value={educationForm.school_name}
                      onChange={(e) => setEducationForm({...educationForm, school_name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Department</label>
                    <input
                      type="text"
                      className="form-control"
                      value={educationForm.department}
                      onChange={(e) => setEducationForm({...educationForm, department: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Degree</label>
                    <input
                      type="text"
                      className="form-control"
                      value={educationForm.degree}
                      onChange={(e) => setEducationForm({...educationForm, degree: e.target.value})}
                      required
                    />
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Start Date</label>
                        <input
                          type="date"
                          className="form-control"
                          value={educationForm.start_date}
                          onChange={(e) => setEducationForm({...educationForm, start_date: e.target.value})}
                          required
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">End Date</label>
                        <input
                          type="date"
                          className="form-control"
                          value={educationForm.end_date}
                          onChange={(e) => setEducationForm({...educationForm, end_date: e.target.value})}
                          disabled={educationForm.is_current}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">GPA</label>
                    <input
                      type="number"
                      step="0.01"
                      className="form-control"
                      value={educationForm.gpa}
                      onChange={(e) => setEducationForm({...educationForm, gpa: e.target.value})}
                    />
                  </div>
                  <div className="mb-3 form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={educationForm.is_current}
                      onChange={(e) => setEducationForm({...educationForm, is_current: e.target.checked})}
                    />
                    <label className="form-check-label">Currently studying</label>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowEducationModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingEducation ? 'Update' : 'Add'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showExperienceModal && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingExperience ? 'Edit Experience' : 'Add Experience'}
                </h5>
                <button className="btn-close" onClick={() => setShowExperienceModal(false)}></button>
              </div>
              <form onSubmit={handleExperienceSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Company Name</label>
                    <input
                      type="text"
                      className="form-control"
                      value={experienceForm.company_name}
                      onChange={(e) => setExperienceForm({...experienceForm, company_name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Position</label>
                    <input
                      type="text"
                      className="form-control"
                      value={experienceForm.position}
                      onChange={(e) => setExperienceForm({...experienceForm, position: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Description</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      value={experienceForm.description}
                      onChange={(e) => setExperienceForm({...experienceForm, description: e.target.value})}
                    />
                  </div>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Start Date</label>
                        <input
                          type="date"
                          className="form-control"
                          value={experienceForm.start_date}
                          onChange={(e) => setExperienceForm({...experienceForm, start_date: e.target.value})}
                          required
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">End Date</label>
                        <input
                          type="date"
                          className="form-control"
                          value={experienceForm.end_date}
                          onChange={(e) => setExperienceForm({...experienceForm, end_date: e.target.value})}
                          disabled={experienceForm.is_current}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="mb-3 form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={experienceForm.is_current}
                      onChange={(e) => setExperienceForm({...experienceForm, is_current: e.target.checked})}
                    />
                    <label className="form-check-label">Currently working</label>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowExperienceModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingExperience ? 'Update' : 'Add'}
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

export default CandidateDetail;