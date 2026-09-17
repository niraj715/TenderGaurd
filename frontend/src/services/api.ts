import { 
  User, Alert, AlertDetail, KPIs, Vendor, VendorNetwork, 
  Tender, Project, Complaint, ReviewerProfile 
} from '../types';
import { localApi } from './localData';

const VITE_API = import.meta.env.VITE_API_BASE;
const isVercelHost = typeof window !== 'undefined' && (
  window.location.hostname.endsWith('vercel.app') ||
  window.location.hostname.includes('vercel')
);

// In Vercel without an external remote API configured, default to local client dataset
// to prevent static 405 Method Not Allowed errors on POST endpoints.
const useLocalDirectly = isVercelHost && (!VITE_API || VITE_API === '/api');

const API_BASE = VITE_API || (
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
    if (useLocalDirectly) {
      return localApi.demoLogin(role);
    }
    try {
      const res = await fetch(`${API_BASE}/auth/demo-login/${role.toLowerCase()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('ps_token', data.access_token);
        localStorage.setItem('ps_user', JSON.stringify(data.user));
        return data;
      }
    } catch {
      // fallback
    }
    return localApi.demoLogin(role);
  },

  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    if (useLocalDirectly) {
      return localApi.login(email, password);
    }
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('ps_token', data.access_token);
        localStorage.setItem('ps_user', JSON.stringify(data.user));
        return data;
      }
      if (res.status === 405 || res.status === 404 || res.status >= 500) {
        return localApi.login(email, password);
      }
      let msg = 'Login failed';
      try {
        const errData = await res.json();
        msg = errData.detail || msg;
      } catch {}
      throw new Error(msg);
    } catch (err: any) {
      if (err.message && err.message.includes('Incorrect')) {
        throw err;
      }
      return localApi.login(email, password);
    }
  },

  async register(name: string, email: string, password: string, role: string): Promise<{ access_token: string; user: User }> {
    if (useLocalDirectly) {
      return localApi.register(name, email, password, role);
    }
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, role }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('ps_token', data.access_token);
        localStorage.setItem('ps_user', JSON.stringify(data.user));
        return data;
      }
    } catch {
      // fallback
    }
    return localApi.register(name, email, password, role);
  },

  async getMe(): Promise<User> {
    if (useLocalDirectly) return localApi.getMe();
    try {
      const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getMe();
  },

  logout() {
    localApi.logout();
  },

  // Analytics KPIs
  async getKPIs(): Promise<KPIs> {
    if (useLocalDirectly) return localApi.getKPIs();
    try {
      const res = await fetch(`${API_BASE}/analytics/kpis`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getKPIs();
  },

  async getRiskTrends(): Promise<any> {
    if (useLocalDirectly) return localApi.getRiskTrends();
    try {
      const res = await fetch(`${API_BASE}/analytics/risk-trends`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getRiskTrends();
  },

  async getAuditTrail(): Promise<any[]> {
    if (useLocalDirectly) return localApi.getAuditTrail();
    try {
      const res = await fetch(`${API_BASE}/analytics/audit-trail`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getAuditTrail();
  },

  // Alerts & Investigation Queue
  async getAlerts(priority?: string, status?: string): Promise<Alert[]> {
    if (useLocalDirectly) return localApi.getAlerts(priority, status);
    try {
      const params = new URLSearchParams();
      if (priority && priority !== 'ALL') params.append('priority', priority);
      if (status && status !== 'ALL') params.append('status', status);
      const res = await fetch(`${API_BASE}/alerts?${params.toString()}`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getAlerts(priority, status);
  },

  async getAlertDetail(id: number): Promise<AlertDetail> {
    if (useLocalDirectly) return localApi.getAlertDetail(id);
    try {
      const res = await fetch(`${API_BASE}/alerts/${id}`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getAlertDetail(id);
  },

  async updateCaseStatus(alertId: number, status: string, note?: string): Promise<any> {
    if (useLocalDirectly) return localApi.updateCaseStatus(alertId, status, note);
    try {
      const res = await fetch(`${API_BASE}/investigations/${alertId}/status`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ status, note }),
      });
      if (res.ok) return res.json();
    } catch {}
    return localApi.updateCaseStatus(alertId, status, note);
  },

  async addCaseNote(alertId: number, note_text: string): Promise<any> {
    if (useLocalDirectly) return localApi.addCaseNote(alertId, note_text);
    try {
      const res = await fetch(`${API_BASE}/investigations/${alertId}/notes`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ note_text }),
      });
      if (res.ok) return res.json();
    } catch {}
    return localApi.addCaseNote(alertId, note_text);
  },

  // Tenders
  async getCategories(): Promise<string[]> {
    if (useLocalDirectly) return localApi.getCategories();
    try {
      const res = await fetch(`${API_BASE}/tenders/categories`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getCategories();
  },

  async getTenders(search?: string, category?: string, page: number = 1, pageSize: number = 20): Promise<{ items: Tender[]; total: number }> {
    if (useLocalDirectly) return localApi.getTenders(search, category, page, pageSize);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category && category !== 'ALL') params.append('category', category);
      params.append('page', page.toString());
      params.append('page_size', pageSize.toString());
      const res = await fetch(`${API_BASE}/tenders?${params.toString()}`, { headers: getHeaders() });
      if (res.ok) {
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
        return { items: mapped, total: data.total || mapped.length };
      }
    } catch {}
    return localApi.getTenders(search, category, page, pageSize);
  },

  async getTenderDetail(id: string | number): Promise<any> {
    if (useLocalDirectly) return localApi.getTenderDetail(id);
    try {
      const res = await fetch(`${API_BASE}/tenders/${id}`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getTenderDetail(id);
  },

  // Vendors & Network
  async getVendors(): Promise<Vendor[]> {
    if (useLocalDirectly) return localApi.getVendors();
    try {
      const res = await fetch(`${API_BASE}/vendors`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getVendors();
  },

  async getVendorNetwork(vendorId: number): Promise<VendorNetwork> {
    if (useLocalDirectly) return localApi.getVendorNetwork(vendorId);
    try {
      const res = await fetch(`${API_BASE}/vendors/${vendorId}/network`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getVendorNetwork(vendorId);
  },

  // Projects
  async getProjects(search?: string): Promise<Project[]> {
    if (useLocalDirectly) return localApi.getProjects(search);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      const res = await fetch(`${API_BASE}/projects?${params.toString()}`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getProjects(search);
  },

  // Complaints / Citizen Reviews
  async getComplaints(projectId?: number, tenderId?: string): Promise<Complaint[]> {
    if (useLocalDirectly) return localApi.getComplaints(projectId, tenderId);
    try {
      const params = new URLSearchParams();
      if (projectId) params.append('project_id', projectId.toString());
      if (tenderId) params.append('tender_id', tenderId);
      const res = await fetch(`${API_BASE}/complaints?${params.toString()}`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getComplaints(projectId, tenderId);
  },

  async getMyReviews(): Promise<Complaint[]> {
    if (useLocalDirectly) return localApi.getMyReviews();
    try {
      const res = await fetch(`${API_BASE}/complaints/my-reviews`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getMyReviews();
  },

  async createComplaint(dataInput: {
    project_id?: number;
    tender_id?: string;
    title: string;
    description: string;
    category: string;
    rating: number;
    location?: string;
    media_url?: string;
  }): Promise<Complaint> {
    if (useLocalDirectly) return localApi.createComplaint(dataInput);
    try {
      const res = await fetch(`${API_BASE}/complaints`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(dataInput),
      });
      if (res.ok) return res.json();
    } catch {}
    return localApi.createComplaint(dataInput);
  },

  async verifyComplaint(complaintId: number, status: 'VERIFIED' | 'UNVERIFIED'): Promise<Complaint> {
    if (useLocalDirectly) return localApi.verifyComplaint(complaintId, status);
    try {
      const res = await fetch(`${API_BASE}/complaints/${complaintId}/verify`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ status }),
      });
      if (res.ok) return res.json();
    } catch {}
    return localApi.verifyComplaint(complaintId, status);
  },

  // Reviewers Leaderboard
  async getLeaderboard(): Promise<ReviewerProfile[]> {
    if (useLocalDirectly) return localApi.getLeaderboard();
    try {
      const res = await fetch(`${API_BASE}/reviewers/leaderboard`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getLeaderboard();
  },

  async getMyReviewerProfile(): Promise<ReviewerProfile> {
    if (useLocalDirectly) return localApi.getMyReviewerProfile();
    try {
      const res = await fetch(`${API_BASE}/reviewers/me`, { headers: getHeaders() });
      if (res.ok) return res.json();
    } catch {}
    return localApi.getMyReviewerProfile();
  }
};
