export type Role = 'CITIZEN' | 'INVESTIGATOR';

export interface User {
  id: number;
  name: string;
  email: string;
  role: Role;
  department?: string;
  avatar_url?: string;
}

export interface ReviewerProfile {
  id: number;
  user_id: number;
  user_name: string;
  reputation_score: number;
  total_reports: number;
  verified_reports: number;
  false_reports: number;
  rank: number;
  badges: string[];
}

export interface Vendor {
  id: number;
  name: string;
  registration_number: string;
  category: string;
  win_rate: number;
  total_contracts: number;
  total_contract_value: number;
  avg_delay_days: number;
  quality_score: number;
  complaint_rate: number;
  maintenance_cost_ratio: number;
  risk_level: string;
  city?: string;
  state?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  risk?: string;
  meta?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
  type: string;
  weight?: number;
}

export interface VendorNetwork {
  vendor_id: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Bid {
  id: number;
  tender_id: number;
  vendor_id: number;
  vendor_name: string;
  bid_amount: number;
  submission_time: string;
  rank: number;
  is_winning: boolean;
  technical_score: number;
  pricing_deviation_pct: number;
}

export interface Tender {
  id: number;
  tender_code: string;
  title: string;
  description?: string;
  department: string;
  category: string;
  estimated_value: number;
  publication_date: string;
  submission_deadline: string;
  status: string;
  winning_vendor_id?: number;
  winning_vendor_name?: string;
  winning_bid_amount?: number;
  location?: string;
  bids?: Bid[];
}

export interface Project {
  id: number;
  contract_id: number;
  name: string;
  description?: string;
  category: string;
  department: string;
  location_name: string;
  latitude?: number;
  longitude?: number;
  planned_duration_days: number;
  actual_duration_days: number;
  delay_days: number;
  planned_cost: number;
  actual_cost: number;
  cost_overrun_pct: number;
  execution_status: string;
  quality_status: string;
  vendor_id?: number;
  vendor_name?: string;
  created_at: string;
}

export interface ComplaintMedia {
  id: number;
  media_url: string;
  media_type: string;
  description?: string;
}

export interface Complaint {
  id: number;
  project_id?: number;
  tender_id?: string;
  project_name?: string;
  citizen_id: number;
  citizen_name: string;
  title: string;
  description: string;
  category: string;
  rating: number;
  location?: string;
  latitude?: number;
  longitude?: number;
  status: string;
  reviewer_credibility_weight: number;
  created_at: string;
  media: ComplaintMedia[];
}

export interface RiskSignal {
  id: number;
  signal_category: string;
  indicator_code?: string;
  title: string;
  description: string;
  severity: string;
  confidence: number;
  peer_benchmark_info?: string;
  supporting_evidence_json?: string;
}

export interface InvestigationNote {
  id: number;
  author_name: string;
  note_text: string;
  created_at: string;
}

export interface TimelineEvent {
  date: string;
  timestamp?: string;
  title: string;
  category: string;
  status: string;
  description: string;
}

export interface InspectionRecord {
  id: number;
  project_id: number;
  inspection_date: string;
  inspector_name: string;
  inspector_agency: string;
  result: string;
  specification_deviations?: string;
  notes?: string;
}

export interface QualityRecord {
  id: number;
  project_id: number;
  defect_category: string;
  severity: string;
  description: string;
  detected_date: string;
  resolved: boolean;
}

export interface MaintenanceRecord {
  id: number;
  project_id: number;
  maintenance_date: string;
  cost: number;
  vendor_id?: string;
  maintenance_type: string;
  benchmark_cost_ratio: number;
  description?: string;
}

export interface Alert {
  id: number;
  case_code: string;
  tender_id: number;
  tender_code?: string;
  vendor_id: number;
  vendor_code?: string;
  project_id?: number;
  project_name?: string;
  vendor_name?: string;
  priority_score: number;
  priority_tier: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'NEW' | 'UNDER_REVIEW' | 'EVIDENCE_GATHERING' | 'ESCALATED' | 'RESOLVED' | 'DISMISSED' | 'MONITORING';
  assigned_investigator_name?: string;
  main_signal: string;
  procurement_risk: number;
  network_risk: number;
  price_risk: number;
  execution_risk: number;
  quality_risk: number;
  feedback_risk: number;
  maintenance_risk: number;
  confidence_score: number;
  ai_summary?: string;
  created_at: string;
  updated_at: string;
  signals_count?: number;
}

export interface AlertDetail extends Alert {
  signals: RiskSignal[];
  notes: InvestigationNote[];
  project_detail?: Project;
  vendor_detail?: Vendor;
  tender_detail?: Tender;
  complaints?: Complaint[];
  inspections?: InspectionRecord[];
  quality_records?: QualityRecord[];
  maintenance?: MaintenanceRecord[];
  timeline?: TimelineEvent[];
}

export interface KPIs {
  tenders_analyzed: number;
  vendors_monitored: number;
  active_alerts: number;
  total_alerts?: number;
  critical_cases: number;
  citizen_reviews: number;
  projects_monitored: number;
  total_procurement_volume: number;
  average_investigation_priority: number;
  tier_distribution?: {
    Critical: number;
    High: number;
    Moderate?: number;
    Medium?: number;
    Low: number;
  };
}
