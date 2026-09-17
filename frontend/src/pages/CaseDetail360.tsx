import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, Share2, Download, AlertTriangle, CheckCircle2, 
  MapPin, Clock, DollarSign, Calendar, HardHat, FileText, 
  Layers, MessageSquare, TrendingUp, Send, User, ChevronRight, 
  X, Star, FileSpreadsheet, ShieldAlert, Check, Copy, AlertCircle
} from 'lucide-react';
import { AlertDetail, VendorNetwork } from '../types';
import { api } from '../services/api';
import { NetworkGraph } from '../components/NetworkGraph';

interface CaseDetail360Props {
  alertId: number;
  onBack: () => void;
}

export const CaseDetail360: React.FC<CaseDetail360Props> = ({ alertId, onBack }) => {
  const [detail, setDetail] = useState<AlertDetail | null>(null);
  const [network, setNetwork] = useState<VendorNetwork | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'procurement' | 'execution' | 'quality' | 'feedback' | 'maintenance'>('overview');
  
  // Note addition state
  const [newNote, setNewNote] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const d = await api.getAlertDetail(alertId || 1);
        setDetail(d);
        if (d.vendor_id) {
          const net = await api.getVendorNetwork(d.vendor_id);
          setNetwork(net);
        }
      } catch (err) {
        console.error('Failed to load alert detail', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [alertId]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim() || !detail) return;
    setSubmittingNote(true);
    try {
      await api.addCaseNote(detail.id, newNote);
      setNewNote('');
      const updated = await api.getAlertDetail(detail.id);
      setDetail(updated);
      showToast('Investigator note logged successfully');
    } catch (err) {
      console.error(err);
      showToast('Failed to log note');
    } finally {
      setSubmittingNote(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!detail) return;
    try {
      await api.updateCaseStatus(detail.id, newStatus, `Investigator changed status to ${newStatus}`);
      const updated = await api.getAlertDetail(detail.id);
      setDetail(updated);
      showToast(`Case status updated to ${newStatus}`);
    } catch (err) {
      console.error(err);
      showToast('Failed to update status');
    }
  };

  // Functional Share Handler
  const handleShare = async () => {
    if (!detail) return;
    const shareUrl = `${window.location.origin}${window.location.pathname}?tab=case-detail&id=${detail.id}`;
    const shareData = {
      title: `ProcureShield AI: Case ${detail.case_code}`,
      text: `Investigation dossier for ${detail.project_name || detail.tender_detail?.title} (Risk Score: ${Math.round(detail.priority_score)}/100)`,
      url: shareUrl,
    };

    if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
      try {
        await navigator.share(shareData);
        showToast('Case shared successfully!');
        return;
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          // fallback to clipboard
        } else {
          return;
        }
      }
    }

    try {
      await navigator.clipboard.writeText(shareUrl);
      showToast('Case URL copied to clipboard!');
    } catch {
      showToast('Unable to copy URL automatically.');
    }
  };

  // Functional JSON Export
  const handleExportJSON = () => {
    if (!detail) return;
    const jsonStr = JSON.stringify(detail, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ProcureShield-Case-${detail.case_code}-Dossier.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('JSON Dossier downloaded!');
    setExportModalOpen(false);
  };

  // Functional CSV Export
  const handleExportCSV = () => {
    if (!detail) return;
    
    // Build comprehensive CSV content
    const rows: string[][] = [
      ['PROCURESHIELD AI - INVESTIGATION DOSSIER'],
      ['Case Code', detail.case_code],
      ['Project Name', detail.project_name || detail.tender_detail?.title || ''],
      ['Tender Code', detail.tender_detail?.tender_code || ''],
      ['Winning Contractor', detail.vendor_name || ''],
      ['Priority Score', `${Math.round(detail.priority_score)}/100`],
      ['Priority Tier', detail.priority_tier],
      ['Workflow Status', detail.status],
      ['Exported At', new Date().toISOString()],
      [],
      ['RISK SIGNALS (C1-C20)'],
      ['Code', 'Title', 'Severity', 'Confidence', 'Description'],
    ];

    (detail.signals || []).forEach(sig => {
      rows.push([
        sig.indicator_code || '',
        `"${(sig.title || '').replace(/"/g, '""')}"`,
        sig.severity || '',
        `${Math.round((sig.confidence || 0) * 100)}%`,
        `"${(sig.description || '').replace(/"/g, '""')}"`
      ]);
    });

    rows.push([]);
    rows.push(['BIDDING PARTICIPATION & SPREAD']);
    rows.push(['Bidder', 'Bid Amount (INR)', 'Tech Score', 'Deviation %', 'Winner']);
    (detail.tender_detail?.bids || []).forEach(bid => {
      rows.push([
        `"${(bid.vendor_name || '').replace(/"/g, '""')}"`,
        `${bid.bid_amount}`,
        `${bid.technical_score}`,
        `${bid.pricing_deviation_pct}%`,
        bid.is_winning ? 'YES' : 'NO'
      ]);
    });

    rows.push([]);
    rows.push(['PROJECT TIMELINE']);
    rows.push(['Date', 'Title', 'Category', 'Status', 'Description']);
    (detail.timeline || []).forEach(ev => {
      rows.push([
        ev.date,
        `"${(ev.title || '').replace(/"/g, '""')}"`,
        ev.category,
        ev.status,
        `"${(ev.description || '').replace(/"/g, '""')}"`
      ]);
    });

    rows.push([]);
    rows.push(['CITIZEN AUDIT DEFECT REPORTS']);
    rows.push(['Citizen', 'Date', 'Rating', 'Category', 'Title', 'Status']);
    (detail.complaints || []).forEach(c => {
      rows.push([
        `"${(c.citizen_name || '').replace(/"/g, '""')}"`,
        c.created_at || '',
        `${c.rating}/5`,
        c.category,
        `"${(c.title || '').replace(/"/g, '""')}"`,
        c.status
      ]);
    });

    const csvContent = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ProcureShield-Case-${detail.case_code}-Data.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('CSV Data export downloaded!');
    setExportModalOpen(false);
  };

  if (loading || !detail) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-teal-500 border-t-transparent mb-3"></div>
        <p className="text-xs font-semibold text-slate-500">Loading 360° Case Dossier...</p>
      </div>
    );
  }

  const projectValue = detail.project_detail?.planned_cost || detail.tender_detail?.estimated_value || 0;
  const actualValue = detail.project_detail?.actual_cost || detail.tender_detail?.winning_bid_amount || 0;
  const locationDisplay = detail.project_detail?.location_name || detail.tender_detail?.location || 'India';
  const categoryDisplay = detail.project_detail?.category || detail.tender_detail?.category || 'Public Works';
  const awardedDateDisplay = detail.project_detail?.created_at || detail.tender_detail?.publication_date || '2023-03-15';

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-4 py-3 rounded-2xl shadow-xl border border-slate-800 flex items-center gap-2 text-xs font-semibold animate-fade-in">
          <Check className="w-4 h-4 text-teal-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Header Actions */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-slate-700 bg-white border border-slate-200/80 hover:bg-slate-50 transition-colors shadow-2xs"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Alerts Queue</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={handleShare}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-slate-700 bg-white border border-slate-200/80 hover:bg-slate-50 transition-colors shadow-2xs"
            title="Share Case Link"
          >
            <Share2 className="w-3.5 h-3.5 text-slate-500" />
            <span>Share Case</span>
          </button>
          <button
            onClick={() => setExportModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-slate-700 bg-white border border-slate-200/80 hover:bg-slate-50 transition-colors shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            <span>Export Dossier</span>
          </button>
        </div>
      </div>

      {/* Project Banner Card */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          {/* Thumbnail */}
          <div className="w-20 h-20 rounded-2xl overflow-hidden border border-slate-200 shrink-0 relative bg-slate-100 flex items-center justify-center">
            <img
              src="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=300&auto=format&fit=crop&q=80"
              alt="Project Construction"
              className="w-full h-full object-cover"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                detail.priority_tier === 'CRITICAL'
                  ? 'bg-red-50 text-red-700 border border-red-200'
                  : detail.priority_tier === 'HIGH'
                  ? 'bg-orange-50 text-orange-700 border border-orange-200'
                  : 'bg-amber-50 text-amber-800 border border-amber-200'
              }`}>
                <AlertTriangle className="w-3 h-3" />
                <span>{detail.priority_tier} Priority</span>
              </span>

              <span className="text-xs font-bold text-slate-400 font-mono">
                {detail.case_code}
              </span>
            </div>

            <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
              {detail.project_name || detail.tender_detail?.title || 'Public Infrastructure Project'}
            </h1>

            {/* Meta Chips */}
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 pt-0.5">
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>{locationDisplay}</span>
              </span>
              <span className="flex items-center gap-1">
                <HardHat className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>{categoryDisplay}</span>
              </span>
              <span className="flex items-center gap-1">
                <DollarSign className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>₹{(projectValue / 1000000).toFixed(2)} Million</span>
              </span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>Awarded: {awardedDateDisplay}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Priority Score on Right */}
        <div className="text-left md:text-right shrink-0">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
            Investigation Priority
          </p>
          <div className="inline-flex items-center justify-center px-4 py-2 rounded-2xl bg-gradient-to-br from-red-600 to-rose-600 text-white font-black text-xl tracking-tight shadow-md shadow-red-500/20">
            {Math.round(detail.priority_score)}/100
          </div>
          <p className="text-[10px] text-slate-400 mt-1 font-medium">
            Confidence: {Math.round(detail.confidence_score * 100)}%
          </p>
        </div>
      </div>

      {/* Horizontal Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 overflow-x-auto">
        {[
          { id: 'overview', label: `Overview & Signals (${detail.signals?.length || 0})` },
          { id: 'procurement', label: `Procurement & Bids (${detail.tender_detail?.bids?.length || 0})` },
          { id: 'execution', label: 'Execution & Delays' },
          { id: 'quality', label: `Quality & Inspections (${(detail.inspections?.length || 0) + (detail.quality_records?.length || 0)})` },
          { id: 'feedback', label: `Public Feedback (${detail.complaints?.length || 0})` },
          { id: 'maintenance', label: `Maintenance (${detail.maintenance?.length || 0})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`pb-3 px-4 text-xs font-bold whitespace-nowrap transition-all relative ${
              activeTab === tab.id
                ? 'text-teal-600'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <span>{tab.label}</span>
            {activeTab === tab.id && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-teal-600 rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* TAB 1: OVERVIEW & SIGNALS */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column (6 cols): Key Risk Signals */}
          <div className="lg:col-span-6 p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-black text-slate-900 tracking-tight">
                Anomalous Risk Signals (C1–C20)
              </h3>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {detail.signals?.length || 0} Indicators Triggered
              </span>
            </div>

            <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
              {detail.signals && detail.signals.length > 0 ? (
                detail.signals.map((sig, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100/70 transition-colors space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {sig.indicator_code && (
                          <span className="px-2 py-0.5 rounded-md text-[10px] font-black bg-slate-900 text-white font-mono">
                            {sig.indicator_code}
                          </span>
                        )}
                        <span className="text-xs font-bold text-slate-900">{sig.title || sig.signal_category}</span>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        sig.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                        sig.severity === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                        'bg-amber-100 text-amber-800'
                      }`}>
                        {sig.severity}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 leading-relaxed">{sig.description}</p>
                    
                    {sig.peer_benchmark_info && (
                      <div className="text-[10px] text-slate-500 font-medium bg-white/70 px-2 py-1 rounded border border-slate-200/60">
                        {sig.peer_benchmark_info}
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-0.5">
                      <span>Category: {sig.signal_category}</span>
                      <span>Confidence: {Math.round((sig.confidence || 0.85) * 100)}%</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-slate-400">
                  <ShieldAlert className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-xs font-semibold">No anomalous risk signals detected.</p>
                </div>
              )}
            </div>

            {/* Case Status Control */}
            <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-bold text-slate-700">Case Workflow Status:</span>
              <select
                value={detail.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="text-xs font-bold bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-slate-800 focus:outline-none focus:border-teal-500"
              >
                <option value="NEW">NEW ALERT</option>
                <option value="UNDER_REVIEW">UNDER REVIEW</option>
                <option value="EVIDENCE_GATHERING">EVIDENCE GATHERING</option>
                <option value="ESCALATED">ESCALATED TO VIGILANCE</option>
                <option value="RESOLVED">RESOLVED / REMEDIATED</option>
                <option value="DISMISSED">DISMISSED</option>
              </select>
            </div>
          </div>

          {/* Right Column (6 cols): Dynamic Project Timeline */}
          <div className="lg:col-span-6 p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-black text-slate-900 tracking-tight">
                Project & Procurement Timeline
              </h3>
              <span className="text-[11px] font-bold text-slate-400">
                {detail.timeline?.length || 0} Events
              </span>
            </div>

            {/* Vertical Dynamic Timeline */}
            <div className="relative pl-6 space-y-5 before:content-[''] before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 py-1 max-h-[300px] overflow-y-auto pr-2">
              {detail.timeline && detail.timeline.length > 0 ? (
                detail.timeline.map((ev, idx) => {
                  const isLateOrFailed = ev.status === 'DELAYED' || ev.status === 'FAILED' || ev.title.toLowerCase().includes('late') || ev.title.toLowerCase().includes('fail');
                  return (
                    <div key={idx} className="relative flex items-start justify-between gap-3 text-xs">
                      <span className={`absolute -left-6 w-3 h-3 rounded-full ring-4 ring-white mt-0.5 ${
                        isLateOrFailed ? 'bg-red-500' : 'bg-teal-500'
                      }`} />
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <p className="font-bold text-slate-900">{ev.title}</p>
                          <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-semibold uppercase">
                            {ev.category}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 leading-snug">{ev.description}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="font-mono text-[10px] text-slate-400 block">{ev.date}</span>
                        {isLateOrFailed && (
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-red-50 text-red-600 border border-red-200 inline-block mt-0.5">
                            {ev.status}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-slate-400 italic">No timeline records logged.</p>
              )}
            </div>

            {/* Investigation Notes Feed */}
            <div className="pt-4 border-t border-slate-100 space-y-3">
              <h4 className="text-xs font-bold text-slate-900">Investigator Triage Notes</h4>
              <div className="space-y-2 max-h-36 overflow-y-auto">
                {detail.notes && detail.notes.length > 0 ? (
                  detail.notes.map((n) => (
                    <div key={n.id} className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                      <p className="text-slate-800 font-medium leading-relaxed">{n.note_text}</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">
                        By {n.author_name} • {new Date(n.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 italic">No notes logged yet.</p>
                )}
              </div>

              {/* Add Note Form */}
              <form onSubmit={handleAddNote} className="flex gap-2 pt-1">
                <input
                  type="text"
                  placeholder="Log investigator note..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="flex-grow px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-teal-500"
                />
                <button
                  type="submit"
                  disabled={submittingNote || !newNote.trim()}
                  className="px-3.5 py-1.5 rounded-xl text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 disabled:opacity-50 transition-colors flex items-center gap-1 shrink-0"
                >
                  <Send className="w-3 h-3" />
                  <span>Log</span>
                </button>
              </form>
            </div>
          </div>

        </div>
      )}

      {/* TAB 2: PROCUREMENT & BIDDING */}
      {activeTab === 'procurement' && (
        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-black text-slate-900">Bidding Distribution & Price Deviation</h3>
              <p className="text-xs text-slate-500">
                Tender Code: {detail.tender_detail?.tender_code || 'T-2023-01'} • Buyer: {detail.tender_detail?.department || 'PWD'}
              </p>
            </div>
            {actualValue > projectValue && projectValue > 0 && (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-50 text-red-600 border border-red-200">
                +{(((actualValue - projectValue) / projectValue) * 100).toFixed(1)}% Deviation vs Estimated
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <p className="text-[11px] text-slate-500 font-medium">Department Estimated Cost</p>
              <p className="text-xl font-bold text-slate-900 mt-1">₹{projectValue.toLocaleString('en-IN')}</p>
              <span className="text-[10px] text-slate-400">Department Schedule of Rates</span>
            </div>
            <div className="p-4 rounded-xl bg-red-50/50 border border-red-200/80">
              <p className="text-[11px] text-red-600 font-medium">Awarded Winning Bid</p>
              <p className="text-xl font-bold text-red-600 mt-1">₹{actualValue.toLocaleString('en-IN')}</p>
              <span className="text-[10px] text-red-600/80">{detail.vendor_name || 'Winning Contractor'}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <p className="text-[11px] text-slate-500 font-medium">Competitive Bidders</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{detail.tender_detail?.bids?.length || 0} Bids</p>
              <span className="text-[10px] text-slate-400">Received prior to deadline</span>
            </div>
          </div>

          {/* Real Bids Table */}
          <div className="border border-slate-200 rounded-xl overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600 min-w-[500px]">
              <thead className="bg-slate-50 text-[11px] font-semibold text-slate-400 uppercase">
                <tr>
                  <th className="py-2.5 px-4">Bidder</th>
                  <th className="py-2.5 px-4 text-right">Bid Amount</th>
                  <th className="py-2.5 px-4 text-center">Tech Score</th>
                  <th className="py-2.5 px-4 text-center">Pricing Deviation</th>
                  <th className="py-2.5 px-4 text-right">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {detail.tender_detail?.bids && detail.tender_detail.bids.length > 0 ? (
                  detail.tender_detail.bids.map((bid, idx) => (
                    <tr key={idx} className={bid.is_winning ? 'bg-red-50/30' : 'hover:bg-slate-50/50'}>
                      <td className="py-2.5 px-4 font-bold text-slate-900">
                        {bid.vendor_name}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono font-bold text-slate-900">
                        ₹{bid.bid_amount.toLocaleString('en-IN')}
                      </td>
                      <td className="py-2.5 px-4 text-center">{bid.technical_score || 85.0}</td>
                      <td className="py-2.5 px-4 text-center font-bold">
                        <span className={bid.pricing_deviation_pct > 0 ? 'text-red-600' : 'text-emerald-600'}>
                          {bid.pricing_deviation_pct > 0 ? '+' : ''}{bid.pricing_deviation_pct}%
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-right">
                        {bid.is_winning ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
                            Winner (L1)
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-400 font-medium">
                            L{idx + 1}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-400 italic">
                      No bids recorded for this procurement tender.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: EXECUTION */}
      {activeTab === 'execution' && (
        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-black text-slate-900">Post-Award Contract Execution</h3>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
              detail.project_detail?.delay_days && detail.project_detail.delay_days > 0
                ? 'bg-red-50 text-red-600 border border-red-200'
                : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
            }`}>
              {detail.project_detail?.execution_status || 'COMPLETED'}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 font-medium">Planned Duration</span>
              <p className="text-lg font-bold text-slate-900 mt-1">
                {detail.project_detail?.planned_duration_days || 180} Days
              </p>
            </div>
            <div className="p-4 rounded-xl bg-red-50 border border-red-200">
              <span className="text-red-600 font-medium">Actual Duration</span>
              <p className="text-lg font-bold text-red-600 mt-1">
                {detail.project_detail?.actual_duration_days || 180} Days
                {detail.project_detail?.delay_days && detail.project_detail.delay_days > 0 ? (
                  <span className="text-xs ml-1">(+{detail.project_detail.delay_days})</span>
                ) : null}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 font-medium">Contract Sum</span>
              <p className="text-lg font-bold text-slate-900 mt-1">
                ₹{(detail.project_detail?.planned_cost || 0).toLocaleString('en-IN')}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-red-50 border border-red-200">
              <span className="text-red-600 font-medium">Actual Outlay</span>
              <p className="text-lg font-bold text-red-600 mt-1">
                ₹{(detail.project_detail?.actual_cost || 0).toLocaleString('en-IN')}
                {detail.project_detail?.cost_overrun_pct && detail.project_detail.cost_overrun_pct > 0 ? (
                  <span className="text-xs ml-1">(+{detail.project_detail.cost_overrun_pct}%)</span>
                ) : null}
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-xs space-y-1">
            <p className="font-bold text-slate-800">Project Description & Scope</p>
            <p className="text-slate-600 leading-relaxed">
              {detail.project_detail?.description || `Infrastructure civil works contract administered under ${detail.project_detail?.department || 'Department'}.`}
            </p>
            <p className="text-[11px] text-slate-400 pt-1">
              Quality Audit Status: <strong className="text-slate-700">{detail.project_detail?.quality_status || 'SATISFACTORY'}</strong>
            </p>
          </div>
        </div>
      )}

      {/* TAB 4: QUALITY & INSPECTIONS */}
      {activeTab === 'quality' && (
        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-black text-slate-900">Quality Inspection Audits</h3>
            <span className="text-xs text-slate-400">
              {detail.inspections?.length || 0} Audits Conducted
            </span>
          </div>

          {/* Inspections */}
          <div className="space-y-3">
            {detail.inspections && detail.inspections.length > 0 ? (
              detail.inspections.map((insp) => (
                <div key={insp.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <p className="font-bold text-slate-900">{insp.inspector_agency || 'State Quality Bureau'}</p>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      insp.result === 'FAILED' ? 'bg-red-50 text-red-600 border border-red-200' :
                      insp.result === 'FLAGGED' ? 'bg-orange-50 text-orange-600 border border-orange-200' :
                      'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    }`}>
                      {insp.result}
                    </span>
                  </div>
                  <p className="text-slate-700 leading-relaxed">
                    {insp.specification_deviations || insp.notes || 'Routine physical inspection completed.'}
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Inspector: {insp.inspector_name} • Date: {insp.inspection_date}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 italic">No official inspection reports logged for this project yet.</p>
            )}
          </div>

          {/* Quality Records */}
          {detail.quality_records && detail.quality_records.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-slate-100">
              <h4 className="text-xs font-bold text-slate-900">Recorded Quality Defects</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {detail.quality_records.map((q) => (
                  <div key={q.id} className="p-3 rounded-xl bg-red-50/40 border border-red-100 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{q.defect_category}</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-100 text-red-700">
                        {q.severity}
                      </span>
                    </div>
                    <p className="text-slate-600 text-[11px]">{q.description}</p>
                    <p className="text-[10px] text-slate-400">Detected: {q.detected_date} • Resolved: {q.resolved ? 'Yes' : 'No'}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: PUBLIC FEEDBACK */}
      {activeTab === 'feedback' && (
        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-black text-slate-900">
              Verified Citizen Defect Reports ({detail.complaints?.length || 0})
            </h3>
            <span className="text-xs text-slate-400">Geo-located Ground Truth</span>
          </div>

          {detail.complaints && detail.complaints.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {detail.complaints.map((c) => (
                <div key={c.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 text-xs space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-bold text-slate-900 leading-snug">{c.title}</p>
                      <span className="inline-block text-[10px] px-2 py-0.5 rounded bg-white text-slate-600 border border-slate-200 mt-1">
                        {c.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-amber-500 shrink-0">
                      <Star className="w-3.5 h-3.5 fill-current" />
                      <span className="font-bold text-slate-800 text-[11px]">{c.rating}/5</span>
                    </div>
                  </div>
                  <p className="text-slate-600 text-[11px] leading-relaxed">{c.description}</p>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-200/50">
                    <span>By {c.citizen_name}</span>
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 font-semibold text-slate-700">
                      {c.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 text-slate-300" />
              <p className="text-xs font-semibold">No citizen feedback submitted for this project yet.</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Citizens can submit on-site defect photos from the Citizen Portal.</p>
            </div>
          )}
        </div>
      )}

      {/* TAB 6: MAINTENANCE & LIFECYCLE */}
      {activeTab === 'maintenance' && (
        <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-black text-slate-900">Post-Award Maintenance & Lifecycle</h3>
            <span className="text-xs text-slate-400">
              {detail.maintenance?.length || 0} Maintenance Outlays
            </span>
          </div>

          {detail.maintenance && detail.maintenance.length > 0 ? (
            <div className="space-y-3">
              {detail.maintenance.map((m) => (
                <div key={m.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 text-xs space-y-2 text-slate-700">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{m.maintenance_type}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      m.benchmark_cost_ratio > 1.5 ? 'bg-red-50 text-red-600 border border-red-200' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {m.benchmark_cost_ratio}× Benchmark Ratio
                    </span>
                  </div>
                  <p className="text-slate-800 font-medium">
                    Outlay: <strong>₹{m.cost.toLocaleString('en-IN')}</strong>
                  </p>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {m.description || 'Post-commissioning remediation and lifecycle maintenance record.'}
                  </p>
                  <p className="text-[10px] text-slate-400">Date: {m.maintenance_date}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
              <p className="text-xs font-semibold">No post-award maintenance claims recorded.</p>
            </div>
          )}
        </div>
      )}

      {/* Export Modal */}
      {exportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="w-full max-w-md bg-white rounded-2xl p-6 shadow-2xl space-y-4 border border-slate-200">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-sm">Export Investigation Dossier</h3>
              <button onClick={() => setExportModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <p className="text-xs text-slate-600 leading-relaxed">
              Export official audit documentation for <strong>{detail.case_code}</strong> ({detail.project_name || 'Project'}).
            </p>

            <div className="space-y-2.5 pt-2">
              <button
                onClick={handleExportJSON}
                className="w-full py-2.5 px-4 rounded-xl font-bold text-xs text-slate-800 bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors flex items-center justify-between"
              >
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-teal-600" />
                  <span>Download Full JSON Dossier</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">.JSON</span>
              </button>

              <button
                onClick={handleExportCSV}
                className="w-full py-2.5 px-4 rounded-xl font-bold text-xs text-slate-800 bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors flex items-center justify-between"
              >
                <div className="flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                  <span>Download CSV Summary Spreadsheet</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">.CSV</span>
              </button>

              <button
                onClick={() => {
                  window.print();
                  setExportModalOpen(false);
                }}
                className="w-full py-2.5 px-4 rounded-xl font-bold text-xs text-white bg-teal-600 hover:bg-teal-500 transition-colors flex items-center justify-center gap-2 shadow-sm"
              >
                <Download className="w-4 h-4" />
                <span>Print / Save PDF Dossier</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
