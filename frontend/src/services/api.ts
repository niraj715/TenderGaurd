import { 
  User, Alert, AlertDetail, KPIs, Vendor, VendorNetwork, 
  Tender, Project, Complaint, ReviewerProfile 
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || (
  typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000/api'
    : '/api'
);

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('ps_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Auth
  async demoLogin(role: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/demo-login/${role.toLowerCase()}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      let msg = 'Demo login failed';
      try {
        const errData = await res.json();
        msg = errData.detail || msg;
      } catch {
        // ignore
      }
      throw new Error(msg);
    }
    const data = await res.json();
    localStorage.setItem('ps_token', data.access_token);
    localStorage.setItem('ps_user', JSON.stringify(data.user));
    return data;
  },

  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      let msg = 'Login failed';
      try {
        const errData = await res.json();
        msg = errData.detail || msg;
      } catch {
        // ignore
      }
      throw new Error(msg);
    }
    const data = await res.json();
    localStorage.setItem('ps_token', data.access_token);
    localStorage.setItem('ps_user', JSON.stringify(data.user));
    return data;
  },

  async register(name: string, email: string, password: string, role: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, role }),
    });
    if (!res.ok) {
      let msg = 'Registration failed';
      try {
        const errData = await res.json();
        msg = errData.detail || msg;
      } catch {
        // ignore
      }
      throw new Error(msg);
    }
    const data = await res.json();
    localStorage.setItem('ps_token', data.access_token);
    localStorage.setItem('ps_user', JSON.stringify(data.user));
    return data;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch user');
    return res.json();
  },

  logout() {
    localStorage.removeItem('ps_token');
    localStorage.removeItem('ps_user');
  },

  // Analytics KPIs
  async getKPIs(): Promise<KPIs> {
    const res = await fetch(`${API_BASE}/analytics/kpis`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch KPIs');
    return res.json();
  },

  async getRiskTrends(): Promise<any> {
    const res = await fetch(`${API_BASE}/analytics/risk-trends`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch risk trends');
    return res.json();
  },

  async getAuditTrail(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/analytics/audit-trail`, { headers: getHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  // Alerts & Investigation Queue
  async getAlerts(priority?: string, status?: string): Promise<Alert[]> {
    const params = new URLSearchParams();
    if (priority && priority !== 'ALL') params.append('priority', priority);
    if (status && status !== 'ALL') params.append('status', status);
    const res = await fetch(`${API_BASE}/alerts?${params.toString()}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async getAlertDetail(id: number): Promise<AlertDetail> {
    const res = await fetch(`${API_BASE}/alerts/${id}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch alert detail');
    return res.json();
  },

  async updateCaseStatus(alertId: number, status: string, note?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/investigations/${alertId}/status`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ status, note }),
    });
    if (!res.ok) throw new Error('Failed to update case status');
    return res.json();
  },

  async addCaseNote(alertId: number, note_text: string): Promise<any> {
    const res = await fetch(`${API_BASE}/investigations/${alertId}/notes`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ note_text }),
    });
    if (!res.ok) throw new Error('Failed to add note');
    return res.json();
  },

  // Tenders
  async getCategories(): Promise<string[]> {
    const res = await fetch(`${API_BASE}/tenders/categories`, { headers: getHeaders() });
    if (!res.ok) return ['Civil Construction', 'Road Infrastructure', 'Water & Sanitation', 'Electrical & Energy'];
    return res.json();
  },

  async getTenders(search?: string, category?: string, page: number = 1, pageSize: number = 20): Promise<{ items: Tender[]; total: number }> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (category && category !== 'ALL') params.append('category', category);
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    const res = await fetch(`${API_BASE}/tenders?${params.toString()}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch tenders');
    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.items || []);
    const mapped = items.map((t: any) => ({
      ...t,
      title: t.title || t.tender_title || `Tender ${t.tender_id}`,
      tender_code: t.tender_code || t.tender_id,
      department: t.department || t.buyer_name || 'Public Works',
      category: t.category || 'Civil Infrastructure',
      status: t.status || 'AWARDED',
      estimated_value: t.estimated_value || t.estimated_value_inr || 0,
      winning_bid_amount: t.winning_bid_amount || t.awarded_amount_inr || t.estimated_value_inr || 0,
      bids_count: t.bidders_count || (t.bids ? t.bids.length : 1),
    }));
    return {
      items: mapped,
      total: data.total || mapped.length
    };
  },

  async getTenderDetail(id: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/tenders/${id}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch tender detail');
    return res.json();
  },

  // Vendors & Network
  async getVendors(): Promise<Vendor[]> {
    const res = await fetch(`${API_BASE}/vendors`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch vendors');
    return res.json();
  },

  async getVendorNetwork(vendorId: number): Promise<VendorNetwork> {
    const res = await fetch(`${API_BASE}/vendors/${vendorId}/network`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch vendor network');
    return res.json();
  },

  // Projects
  async getProjects(search?: string): Promise<Project[]> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    const res = await fetch(`${API_BASE}/projects?${params.toString()}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch projects');
    return res.json();
  },

  // Complaints / Citizen Reviews
  async getComplaints(projectId?: number, tenderId?: string): Promise<Complaint[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId.toString());
    if (tenderId) params.append('tender_id', tenderId);
    const res = await fetch(`${API_BASE}/complaints?${params.toString()}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch complaints');
    return res.json();
  },

  async getMyReviews(): Promise<Complaint[]> {
    const res = await fetch(`${API_BASE}/complaints/my-reviews`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch my reviews');
    return res.json();
  },

  async createComplaint(data: {
    project_id?: number;
    tender_id?: string;
    title: string;
    description: string;
    category: string;
    rating: number;
    location?: string;
    media_url?: string;
  }): Promise<Complaint> {
    const res = await fetch(`${API_BASE}/complaints`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      let msg = 'Failed to submit review';
      try {
        const err = await res.json();
        msg = err.detail || msg;
      } catch {}
      throw new Error(msg);
    }
    return res.json();
  },

  async verifyComplaint(complaintId: number, status: 'VERIFIED' | 'UNVERIFIED'): Promise<Complaint> {
    const res = await fetch(`${API_BASE}/complaints/${complaintId}/verify`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to verify complaint');
    return res.json();
  },

  // Reviewers Leaderboard
  async getLeaderboard(): Promise<ReviewerProfile[]> {
    const res = await fetch(`${API_BASE}/reviewers/leaderboard`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch leaderboard');
    return res.json();
  },

  async getMyReviewerProfile(): Promise<ReviewerProfile> {
    const res = await fetch(`${API_BASE}/reviewers/me`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch reviewer profile');
    return res.json();
  }
};
