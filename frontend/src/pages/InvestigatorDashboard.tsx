import React, { useState, useEffect } from 'react';
import { 
  FileText, Building2, Bell, MessageSquare, ArrowUpRight, 
  ChevronRight, AlertTriangle, Filter, ShieldAlert, CheckCircle2 
} from 'lucide-react';
import { Alert, KPIs } from '../types';
import { api } from '../services/api';

interface InvestigatorDashboardProps {
  kpis: KPIs | null;
  onSelectCase: (alertId: number) => void;
  onViewAllAlerts?: () => void;
}

export const InvestigatorDashboard: React.FC<InvestigatorDashboardProps> = ({
  kpis,
  onSelectCase,
  onViewAllAlerts
}) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState<'ALL' | 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'>('ALL');

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const data = await api.getAlerts(priorityFilter === 'ALL' ? undefined : priorityFilter);
        setAlerts(data);
      } catch (err) {
        console.error('Failed to load alerts', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, [priorityFilter]);

  // Dynamic Tier Breakdown
  const criticalCount = kpis?.tier_distribution?.Critical ?? alerts.filter(a => a.priority_tier === 'CRITICAL').length;
  const highCount = kpis?.tier_distribution?.High ?? alerts.filter(a => a.priority_tier === 'HIGH').length;
  const mediumCount = (kpis?.tier_distribution?.Medium ?? kpis?.tier_distribution?.Moderate) ?? alerts.filter(a => a.priority_tier === 'MEDIUM').length;
  const lowCount = kpis?.tier_distribution?.Low ?? alerts.filter(a => a.priority_tier === 'LOW').length;
  
  const totalTierAlerts = criticalCount + highCount + mediumCount + lowCount || (kpis?.active_alerts || 1);

  // Calculate SVG Donut stroke percentages
  // Perimeter of radius 38 is 2 * PI * 38 ≈ 238.76
  const C = 238.76;
  const critPct = criticalCount / totalTierAlerts;
  const highPct = highCount / totalTierAlerts;
  const medPct = mediumCount / totalTierAlerts;
  const lowPct = lowCount / totalTierAlerts;

  const critDash = critPct * C;
  const highDash = highPct * C;
  const medDash = medPct * C;
  const lowDash = lowPct * C;

  const riskCounts = [
    { label: 'Critical', count: criticalCount, color: '#EF4444', text: 'text-red-600', filter: 'CRITICAL' as const },
    { label: 'High', count: highCount, color: '#F97316', text: 'text-orange-500', filter: 'HIGH' as const },
    { label: 'Medium', count: mediumCount, color: '#EAB308', text: 'text-amber-500', filter: 'MEDIUM' as const },
    { label: 'Low', count: lowCount, color: '#10B981', text: 'text-emerald-600', filter: 'LOW' as const },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* 4 Stat KPI Cards - Driven dynamically by database */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Tenders Analysed */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <p className="text-2xl font-black text-slate-900 tracking-tight">
              {kpis?.tenders_analyzed ? kpis.tenders_analyzed.toLocaleString('en-IN') : '500'}
            </p>
            <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-xs font-bold text-slate-500">Tenders Analysed</p>
            <p className="text-[11px] font-semibold text-teal-700 flex items-center gap-0.5 mt-0.5">
              <span>Full Dataset Ground Truth</span>
            </p>
          </div>
        </div>

        {/* Card 2: Vendors Monitored */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <p className="text-2xl font-black text-slate-900 tracking-tight">
              {kpis?.vendors_monitored ? kpis.vendors_monitored.toLocaleString('en-IN') : '50'}
            </p>
            <div className="w-9 h-9 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
              <Building2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-xs font-bold text-slate-500">Vendors Monitored</p>
            <p className="text-[11px] font-semibold text-sky-700 flex items-center gap-0.5 mt-0.5">
              <span>Directorship & Bidding Nexus</span>
            </p>
          </div>
        </div>

        {/* Card 3: Active Alerts */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <p className="text-2xl font-black text-slate-900 tracking-tight text-red-600">
              {kpis?.active_alerts ? kpis.active_alerts.toLocaleString('en-IN') : '42'}
            </p>
            <div className="w-9 h-9 rounded-xl bg-red-50 text-red-600 flex items-center justify-center">
              <Bell className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-xs font-bold text-slate-500">Priority Anomaly Alerts</p>
            <p className="text-[11px] font-bold text-red-600 flex items-center gap-0.5 mt-0.5">
              <span>{kpis?.critical_cases || 0} Critical</span>
              <span className="font-normal text-slate-400">requiring action</span>
            </p>
          </div>
        </div>

        {/* Card 4: Citizen Reviews */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <p className="text-2xl font-black text-slate-900 tracking-tight">
              {kpis?.citizen_reviews ? kpis.citizen_reviews.toLocaleString('en-IN') : '40'}
            </p>
            <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-xs font-bold text-slate-500">Citizen Defect Audits</p>
            <p className="text-[11px] font-semibold text-teal-700 flex items-center gap-0.5 mt-0.5">
              <span>Empaneled Citizen Network</span>
            </p>
          </div>
        </div>
      </div>

      {/* Main Section: Priority Queue & Live Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column (8 cols): Investigation Priority Queue */}
        <div className="lg:col-span-8 p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-black text-slate-900 tracking-tight">
                Investigation Priority Queue
              </h3>
              <p className="text-xs text-slate-500">
                Sorted by Automated Algorithmic Risk Priority Score
              </p>
            </div>

            {/* Filter Pills */}
            <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs overflow-x-auto">
              {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((tier) => (
                <button
                  key={tier}
                  onClick={() => setPriorityFilter(tier)}
                  className={`px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all whitespace-nowrap ${
                    priorityFilter === tier
                      ? 'bg-white text-slate-900 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {tier}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600 min-w-[550px]">
              <thead>
                <tr className="border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="pb-3 pr-4">Case #</th>
                  <th className="pb-3 px-3">Project / Tender</th>
                  <th className="pb-3 px-3">Target Vendor</th>
                  <th className="pb-3 px-3">Flagged Pattern</th>
                  <th className="pb-3 px-3 text-center">Score</th>
                  <th className="pb-3 pl-3 text-right">Tier</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="py-10 text-center text-slate-400">
                      <div className="inline-block animate-spin rounded-full h-5 w-5 border-2 border-teal-500 border-t-transparent mb-1"></div>
                      <p className="text-xs">Loading investigation queue...</p>
                    </td>
                  </tr>
                ) : alerts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-10 text-center text-slate-400">
                      No cases match priority filter: {priorityFilter}
                    </td>
                  </tr>
                ) : (
                  alerts.slice(0, 10).map((a) => (
                    <tr 
                      key={a.id}
                      onClick={() => onSelectCase(a.id)}
                      className="hover:bg-slate-50/80 cursor-pointer transition-colors group"
                    >
                      <td className="py-3.5 pr-4 font-mono font-bold text-slate-800 text-xs">
                        {a.case_code ? a.case_code.replace('CASE-2024-', '') : `#${a.id}`}
                      </td>
                      <td className="py-3.5 px-3 max-w-[200px]">
                        <p className="font-bold text-slate-900 group-hover:text-teal-600 transition-colors truncate">
                          {a.project_name || `Tender #${a.tender_id}`}
                        </p>
                      </td>
                      <td className="py-3.5 px-3 text-slate-600 font-medium truncate max-w-[140px]">
                        {a.vendor_name || 'Vendor'}
                      </td>
                      <td className="py-3.5 px-3 text-slate-500 truncate max-w-[160px]">
                        {a.main_signal || 'Price & Collusion Pattern'}
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        <span className={`inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-bold ${
                          a.priority_score >= 85
                            ? 'bg-red-50 text-red-600 border border-red-200'
                            : a.priority_score >= 70
                            ? 'bg-orange-50 text-orange-600 border border-orange-200'
                            : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}>
                          {Math.round(a.priority_score)}
                        </span>
                      </td>
                      <td className="py-3.5 pl-3 text-right">
                        <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                          a.priority_tier === 'CRITICAL' ? 'bg-red-50 text-red-700 border-red-200' :
                          a.priority_tier === 'HIGH' ? 'bg-orange-50 text-orange-700 border-orange-200' :
                          'bg-amber-50 text-amber-800 border-amber-200'
                        }`}>
                          {a.priority_tier}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="pt-2 flex justify-between items-center text-xs text-slate-400">
            <span>Showing {Math.min(alerts.length, 10)} of {alerts.length} cases</span>
            {onViewAllAlerts && (
              <button
                onClick={onViewAllAlerts}
                className="font-bold text-teal-600 hover:text-teal-700 flex items-center gap-1 group"
              >
                <span>View all in alerts tab</span>
                <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </button>
            )}
          </div>
        </div>

        {/* Right Column (4 cols): Dynamic Risk Distribution Donut */}
        <div className="lg:col-span-4 p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-black text-slate-900 tracking-tight">
              Risk Distribution
            </h3>
            <span className="text-[11px] font-semibold text-slate-400">
              Active Tiers
            </span>
          </div>

          {/* SVG Donut Chart dynamically calculated */}
          <div className="relative flex items-center justify-center py-4">
            <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 100 100">
              {/* Background circle */}
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="transparent"
                stroke="#F1F5F9"
                strokeWidth="14"
              />
              {/* Critical slice */}
              {critDash > 0 && (
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="transparent"
                  stroke="#EF4444"
                  strokeWidth="14"
                  strokeDasharray={`${critDash} ${C - critDash}`}
                  strokeDashoffset="0"
                />
              )}
              {/* High slice */}
              {highDash > 0 && (
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="transparent"
                  stroke="#F97316"
                  strokeWidth="14"
                  strokeDasharray={`${highDash} ${C - highDash}`}
                  strokeDashoffset={`${-critDash}`}
                />
              )}
              {/* Medium slice */}
              {medDash > 0 && (
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="transparent"
                  stroke="#EAB308"
                  strokeWidth="14"
                  strokeDasharray={`${medDash} ${C - medDash}`}
                  strokeDashoffset={`${-(critDash + highDash)}`}
                />
              )}
              {/* Low slice */}
              {lowDash > 0 && (
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="transparent"
                  stroke="#10B981"
                  strokeWidth="14"
                  strokeDasharray={`${lowDash} ${C - lowDash}`}
                  strokeDashoffset={`${-(critDash + highDash + medDash)}`}
                />
              )}
            </svg>

            {/* Center Label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <p className="text-2xl font-black text-slate-900 leading-none">
                {kpis?.active_alerts ?? alerts.length}
              </p>
              <p className="text-[10px] font-bold text-slate-400 mt-1 uppercase tracking-wider">
                Total Alerts
              </p>
            </div>
          </div>

          {/* Donut Legend */}
          <div className="grid grid-cols-2 gap-2.5 pt-2 border-t border-slate-100">
            {riskCounts.map((rc) => (
              <button
                key={rc.label}
                onClick={() => setPriorityFilter(rc.filter)}
                className={`flex items-center justify-between p-2 rounded-xl transition-colors border ${
                  priorityFilter === rc.filter
                    ? 'bg-slate-100 border-slate-300'
                    : 'bg-slate-50 border-slate-100 hover:bg-slate-100/60'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: rc.color }} />
                  <span className="text-xs font-semibold text-slate-700">{rc.label}</span>
                </div>
                <span className={`text-xs font-bold ${rc.text}`}>{rc.count}</span>
              </button>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};
