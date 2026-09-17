import embeddedData from '../data/embeddedData.json';
import { 
  User, Alert, AlertDetail, KPIs, Vendor, VendorNetwork, 
  Tender, Project, Complaint, ReviewerProfile 
} from '../types';

interface Dataset {
  users: User[];
  kpis: KPIs;
  risk_trends: any;
  audit_trail: any[];
  categories: string[];
  alerts: Alert[];
  alert_details: Record<string, AlertDetail>;
  tenders: any[];
  tender_details: Record<string, any>;
  vendors: Vendor[];
  vendor_networks: Record<string, VendorNetwork>;
  projects: Project[];
  complaints: Complaint[];
  leaderboard: ReviewerProfile[];
}

const data = embeddedData as unknown as Dataset;

// Helper to get from localStorage with fallback
function getLocalItem<T>(key: string, fallback: T): T {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : fallback;
  } catch {
    return fallback;
  }
}

function setLocalItem<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore storage quota limits
  }
}

export const localApi = {
  async demoLogin(role: string): Promise<{ access_token: string; user: User }> {
    const roleUpper = role.toUpperCase();
    const user = data.users.find(u => u.role === roleUpper) || data.users[0];
    const token = `ps_live_token_${user.id}_${Date.now()}`;
    localStorage.setItem('ps_token', token);
    localStorage.setItem('ps_user', JSON.stringify(user));
    return { access_token: token, user };
  },

  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const emailNorm = (email || '').trim().toLowerCase();
    const user = data.users.find(u => u.email.toLowerCase() === emailNorm);
    
    // Accept password123 or demo password
    if (!user && !emailNorm.includes('chen') && !emailNorm.includes('verma')) {
      throw new Error('Incorrect email or password');
    }

    const matchedUser = user || (emailNorm.includes('verma') ? data.users[1] : data.users[0]);
    const token = `ps_live_token_${matchedUser.id}_${Date.now()}`;
    localStorage.setItem('ps_token', token);
    localStorage.setItem('ps_user', JSON.stringify(matchedUser));
    return { access_token: token, user: matchedUser };
  },

  async register(name: string, email: string, password: string, role: string): Promise<{ access_token: string; user: User }> {
    const newUser: User = {
      id: Date.now(),
      name,
      email,
      role: (role.toUpperCase() === 'CITIZEN' ? 'CITIZEN' : 'INVESTIGATOR') as any,
      department: role.toUpperCase() === 'CITIZEN' ? 'Public Infrastructure Watch' : 'Vigilance Directorate',
      avatar_url: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(name)}`
    };
    const token = `ps_live_token_${newUser.id}_${Date.now()}`;
    localStorage.setItem('ps_token', token);
    localStorage.setItem('ps_user', JSON.stringify(newUser));
    return { access_token: token, user: newUser };
  },

  async getMe(): Promise<User> {
    const stored = localStorage.getItem('ps_user');
    if (stored) {
      try { return JSON.parse(stored); } catch {}
    }
    return data.users[0];
  },

  logout(): void {
    localStorage.removeItem('ps_token');
    localStorage.removeItem('ps_user');
  },

  async getKPIs(): Promise<KPIs> {
    return data.kpis;
  },

  async getRiskTrends(): Promise<any> {
    return data.risk_trends;
  },

  async getAuditTrail(): Promise<any[]> {
    const customAudit = getLocalItem<any[]>('ps_custom_audit', []);
    return [...customAudit, ...data.audit_trail];
  },

  async getAlerts(priority?: string, status?: string): Promise<Alert[]> {
    const statusOverrides = getLocalItem<Record<number, string>>('ps_alert_status_map', {});
    let list = data.alerts.map(a => ({
      ...a,
      status: (statusOverrides[a.id] || a.status) as any
    }));

    if (priority && priority !== 'ALL') {
      list = list.filter(a => a.priority_tier === priority.toUpperCase());
    }
    if (status && status !== 'ALL') {
      list = list.filter(a => a.status === status.toUpperCase());
    }
    return list;
  },

  async getAlertDetail(id: number): Promise<AlertDetail> {
    const statusOverrides = getLocalItem<Record<number, string>>('ps_alert_status_map', {});
    const customNotes = getLocalItem<Record<number, any[]>>('ps_alert_notes_map', {});
    
    let detail = data.alert_details[String(id)] || data.alert_details[Object.keys(data.alert_details)[0]];
    if (!detail) {
      const fallbackAlert = data.alerts.find(a => a.id === id) || data.alerts[0];
      detail = {
        ...fallbackAlert,
        tender: data.tenders.find(t => t.id === fallbackAlert.tender_id) || data.tenders[0],
        vendor: data.vendors.find(v => v.id === fallbackAlert.vendor_id) || data.vendors[0],
        project: data.projects[0],
        signals: [],
        timeline: [],
        inspections: [],
        quality_records: [],
        maintenance: [],
        notes: []
      } as any;
    }

    const currentStatus = statusOverrides[id] || detail.status;
    const notes = [...(detail.notes || []), ...(customNotes[id] || [])];

    return {
      ...detail,
      status: currentStatus as any,
      notes
    };
  },

  async updateCaseStatus(alertId: number, status: string, note?: string): Promise<any> {
    const statusOverrides = getLocalItem<Record<number, string>>('ps_alert_status_map', {});
    statusOverrides[alertId] = status;
    setLocalItem('ps_alert_status_map', statusOverrides);

    if (note) {
      await this.addCaseNote(alertId, note);
    }

    const customAudit = getLocalItem<any[]>('ps_custom_audit', []);
    customAudit.unshift({
      id: Date.now(),
      action: `Status updated to ${status}`,
      timestamp: new Date().toISOString(),
      user: 'Sarah Chen (Lead Investigator)',
      details: `Investigation status changed for Alert #${alertId}`
    });
    setLocalItem('ps_custom_audit', customAudit.slice(0, 50));

    return { success: true, alert_id: alertId, new_status: status };
  },

  async addCaseNote(alertId: number, note_text: string): Promise<any> {
    const customNotes = getLocalItem<Record<number, any[]>>('ps_alert_notes_map', {});
    if (!customNotes[alertId]) customNotes[alertId] = [];
    const newNote = {
      id: Date.now(),
      author_name: 'Sarah Chen',
      note_text,
      created_at: new Date().toISOString()
    };
    customNotes[alertId].unshift(newNote);
    setLocalItem('ps_alert_notes_map', customNotes);
    return newNote;
  },

  async getCategories(): Promise<string[]> {
    return data.categories || ['Civil Construction', 'Road Infrastructure', 'Water & Sanitation', 'Electrical & Energy', 'Healthcare Equipment'];
  },

  async getTenders(search?: string, category?: string, page: number = 1, pageSize: number = 20): Promise<{ items: Tender[]; total: number }> {
    let list = data.tenders || [];
    if (category && category !== 'ALL') {
      list = list.filter(t => (t.category || '').toLowerCase() === category.toLowerCase());
    }
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(t => 
        (t.title || '').toLowerCase().includes(q) ||
        (t.tender_code || '').toLowerCase().includes(q) ||
        (t.department || '').toLowerCase().includes(q)
      );
    }

    const total = list.length;
    const start = (page - 1) * pageSize;
    const items = list.slice(start, start + pageSize).map((t: any) => ({
      ...t,
      title: t.title || t.tender_title || `Tender ${t.tender_id || t.id}`,
      tender_code: t.tender_code || t.tender_id || `T-${t.id}`,
      department: t.department || t.buyer_name || 'Public Works',
      category: t.category || 'Civil Infrastructure',
      status: t.status || 'AWARDED',
      estimated_value: t.estimated_value || t.estimated_value_inr || 10000000,
      winning_bid_amount: t.winning_bid_amount || t.awarded_amount_inr || t.estimated_value || 9500000,
      bids_count: t.bidders_count || (t.bids ? t.bids.length : 3),
    }));

    return { items, total };
  },

  async getTenderDetail(id: string | number): Promise<any> {
    const detail = data.tender_details[String(id)] || data.tender_details[Object.keys(data.tender_details)[0]];
    if (detail) return detail;
    const t = data.tenders.find(x => String(x.id) === String(id)) || data.tenders[0];
    return {
      ...t,
      bids: [
        { id: 101, vendor_name: 'Apex Infra Projects', bid_amount: t.estimated_value * 0.95, rank: 1, is_winning: true },
        { id: 102, vendor_name: 'Shree Balaji Constructions', bid_amount: t.estimated_value * 1.02, rank: 2, is_winning: false },
        { id: 103, vendor_name: 'Bharat Earthworks Ltd', bid_amount: t.estimated_value * 1.08, rank: 3, is_winning: false }
      ]
    };
  },

  async getVendors(): Promise<Vendor[]> {
    return data.vendors;
  },

  async getVendorNetwork(vendorId: number): Promise<VendorNetwork> {
    const net = data.vendor_networks[String(vendorId)];
    if (net && net.nodes && net.nodes.length > 0) return net;
    
    // Fallback realistic network
    const v = data.vendors.find(x => x.id === vendorId) || data.vendors[0];
    return {
      vendor_id: vendorId,
      nodes: [
        { id: `v_${v.id}`, label: v.name, type: 'vendor', risk: v.risk_level },
        { id: 'dir_1', label: 'R. K. Agarwal (Director)', type: 'director' },
        { id: 'addr_1', label: '14/B Nariman Point (Shared Address)', type: 'address' },
        { id: 'v_peer', label: 'Metro Civil Build Corp', type: 'vendor', risk: 'HIGH' }
      ],
      edges: [
        { source: `v_${v.id}`, target: 'dir_1', label: 'Directorship', type: 'directorship' },
        { source: 'dir_1', target: 'v_peer', label: 'Common Director', type: 'directorship' },
        { source: `v_${v.id}`, target: 'addr_1', label: 'Registered Office', type: 'address' },
        { source: 'v_peer', target: 'addr_1', label: 'Shared Registered Address', type: 'address' }
      ]
    };
  },

  async getProjects(search?: string): Promise<Project[]> {
    let list = data.projects;
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(p => p.name.toLowerCase().includes(q) || (p.department || '').toLowerCase().includes(q));
    }
    return list;
  },

  async getComplaints(projectId?: number, tenderId?: string): Promise<Complaint[]> {
    const customComplaints = getLocalItem<Complaint[]>('ps_custom_complaints', []);
    let list = [...customComplaints, ...data.complaints];
    if (projectId) {
      list = list.filter(c => c.project_id === projectId);
    }
    if (tenderId) {
      list = list.filter(c => String(c.tender_id) === String(tenderId));
    }
    return list;
  },

  async getMyReviews(): Promise<Complaint[]> {
    const customComplaints = getLocalItem<Complaint[]>('ps_custom_complaints', []);
    const storedUser = localStorage.getItem('ps_user');
    const user = storedUser ? JSON.parse(storedUser) : data.users[1];
    const all = [...customComplaints, ...data.complaints];
    return all.filter(c => c.citizen_id === user.id || c.citizen_name === user.name || user.role === 'CITIZEN');
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
    const customComplaints = getLocalItem<Complaint[]>('ps_custom_complaints', []);
    const storedUser = localStorage.getItem('ps_user');
    const user = storedUser ? JSON.parse(storedUser) : data.users[1];

    const newC: Complaint = {
      id: Date.now(),
      project_id: dataInput.project_id || 1,
      tender_id: dataInput.tender_id || 'T001',
      citizen_id: user.id,
      citizen_name: user.name,
      title: dataInput.title,
      description: dataInput.description,
      category: dataInput.category,
      rating: dataInput.rating,
      location: dataInput.location || 'Reported Geo-tag Zone',
      status: 'SUBMITTED',
      reviewer_credibility_weight: 0.95,
      created_at: new Date().toISOString(),
      media: dataInput.media_url ? [{ id: Date.now(), media_type: 'IMAGE', media_url: dataInput.media_url, description: 'Citizen Evidence Upload' }] : []
    };

    customComplaints.unshift(newC);
    setLocalItem('ps_custom_complaints', customComplaints);
    return newC;
  },

  async verifyComplaint(complaintId: number, status: 'VERIFIED' | 'UNVERIFIED'): Promise<Complaint> {
    const customComplaints = getLocalItem<Complaint[]>('ps_custom_complaints', []);
    const target = customComplaints.find(c => c.id === complaintId) || data.complaints.find(c => c.id === complaintId);
    if (target) {
      target.status = status;
      setLocalItem('ps_custom_complaints', customComplaints);
      return target;
    }
    return { ...data.complaints[0], id: complaintId, status };
  },

  async getLeaderboard(): Promise<ReviewerProfile[]> {
    return data.leaderboard;
  },

  async getMyReviewerProfile(): Promise<ReviewerProfile> {
    return data.leaderboard[0];
  }
};
