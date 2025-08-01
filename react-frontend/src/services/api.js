const BASE_URL = 'http://0.0.0.0:8000';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const config = {
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          this.logout();
          throw new Error('Authentication failed');
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          const error = new Error(`HTTP error! status: ${response.status}`);
          error.details = errorData;
          error.status = response.status;
          throw error;
        }
        
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json();
      }
      return {};
    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Backend server is not available. Please check if the Django server is running on http://127.0.0.1:8000');
      }
      throw error;
    }
  }

  async login(email, password) {
    const response = await this.request('/api/auth/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (response.access) {
      this.token = response.access;
      localStorage.setItem('token', response.access);
    }
    
    return response;
  }

  async getProfile() {
    return this.request('/api/auth/auth/profile/');
  }

  async getCandidates(page = 1) {
    return this.request(`/api/candidates/candidates/?page=${page}`);
  }

  async createCandidate(data) {
    return this.request('/api/candidates/candidates/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCandidate(id, data) {
    return this.request(`/api/candidates/candidates/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCandidate(id) {
    return this.request(`/api/candidates/candidates/${id}/`, {
      method: 'DELETE',
    });
  }

  async getJobPostings(page = 1) {
    return this.request(`/api/jobs/job-postings/?page=${page}`);
  }

  async createJobPosting(data) {
    return this.request('/api/jobs/job-postings/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateJobPosting(id, data) {
    return this.request(`/api/jobs/job-postings/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteJobPosting(id) {
    return this.request(`/api/jobs/job-postings/${id}/`, {
      method: 'DELETE',
    });
  }

  async getCustomerCompanies(page = 1) {
    return this.request(`/api/companies/customer-companies/?page=${page}`);
  }

  async createCustomerCompany(data) {
    return this.request('/api/companies/customer-companies/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCustomerCompany(id, data) {
    return this.request(`/api/companies/customer-companies/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCustomerCompany(id) {
    return this.request(`/api/companies/customer-companies/${id}/`, {
      method: 'DELETE',
    });
  }

  async getEducations(candidateId) {
    return this.request(`/api/candidates/educations/?candidate=${candidateId}`);
  }

  async createEducation(data) {
    return this.request('/api/candidates/educations/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateEducation(id, data) {
    return this.request(`/api/candidates/educations/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteEducation(id) {
    return this.request(`/api/candidates/educations/${id}/`, {
      method: 'DELETE',
    });
  }

  async getWorkExperiences(candidateId) {
    return this.request(`/api/candidates/work-experiences/?candidate=${candidateId}`);
  }

  async createWorkExperience(data) {
    return this.request('/api/candidates/work-experiences/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateWorkExperience(id, data) {
    return this.request(`/api/candidates/work-experiences/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteWorkExperience(id) {
    return this.request(`/api/candidates/work-experiences/${id}/`, {
      method: 'DELETE',
    });
  }

  async getCandidateFlows(filters = {}) {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    return this.request(`/api/flows/candidate-flows/?${params.toString()}`);
  }

  async createCandidateFlow(data) {
    return this.request('/api/flows/candidate-flows/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCandidateFlow(id, data) {
    return this.request(`/api/flows/candidate-flows/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCandidateFlow(id) {
    return this.request(`/api/flows/candidate-flows/${id}/`, {
      method: 'DELETE',
    });
  }

  async getCandidateFlow(id) {
    return this.request(`/api/flows/candidate-flows/${id}/`);
  }

  async getActivities(filters = {}) {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    return this.request(`/api/flows/activities/?${params.toString()}`);
  }

  async createActivity(data) {
    return this.request('/api/flows/activities/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateActivity(id, data) {
    return this.request(`/api/flows/activities/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteActivity(id) {
    return this.request(`/api/flows/activities/${id}/`, {
      method: 'DELETE',
    });
  }

  async getActivityTypes() {
    return this.request('/api/flows/activity-types/');
  }

  async getStatuses(activityTypeId = null) {
    const params = activityTypeId ? `?activity_type=${activityTypeId}` : '';
    return this.request(`/api/flows/statuses/${params}`);
  }

  async getHRUsers(page = 1) {
    return this.request(`/api/auth/users/?page=${page}`);
  }

  async createHRUser(data) {
    return this.request('/api/auth/users/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateHRUser(id, data) {
    return this.request(`/api/auth/users/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteHRUser(id) {
    return this.request(`/api/auth/users/${id}/`, {
      method: 'DELETE',
    });
  }

  async getHRUser(id) {
    return this.request(`/api/auth/users/${id}/`);
  }

  async getHRCompanies(page = 1) {
    return this.request(`/api/companies/hr-companies/?page=${page}`);
  }

  async createHRCompany(data) {
    return this.request('/api/companies/hr-companies/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateHRCompany(id, data) {
    return this.request(`/api/companies/hr-companies/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteHRCompany(id) {
    return this.request(`/api/companies/hr-companies/${id}/`, {
      method: 'DELETE',
    });
  }

  async toggleHRCompanyActive(id, data) {
    return this.request(`/api/companies/hr-companies/${id}/toggle_active/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReports(page = 1) {
    return this.request(`/api/reports/?page=${page}`);
  }

  async createReport(data) {
    return this.request('/api/reports/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReport(id) {
    return this.request(`/api/reports/${id}/`);
  }

  async deleteReport(id) {
    return this.request(`/api/reports/${id}/`, {
      method: 'DELETE',
    });
  }

  async downloadReport(id) {
    const url = `${BASE_URL}/api/reports/${id}/download/`;
    const config = {
      mode: 'cors',
      credentials: 'include',
      headers: {},
    };

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          this.logout();
          throw new Error('Authentication failed');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response;
    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Backend server is not available. Please check if the Django server is running on http://127.0.0.1:8000');
      }
      throw error;
    }
  }

  async generateMonthlyReport(data) {
    return this.request('/api/reports/generate_monthly_report/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateWeeklyReport(data) {
    return this.request('/api/reports/generate_weekly_report/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  logout() {
    this.token = null;
    localStorage.removeItem('token');
  }
}

export default new ApiService();