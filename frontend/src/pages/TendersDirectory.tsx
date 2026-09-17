import React, { useState, useEffect } from 'react';
import { FileText, Search, ExternalLink, Filter, Building2, MapPin, Tag, ArrowRight, MessageSquare, ShieldAlert } from 'lucide-react';
import { Tender, User } from '../types';
import { api } from '../services/api';

interface TendersDirectoryProps {
  onSelectTender?: (alertId: number) => void;
  onReviewTender?: (tenderCode: string) => void;
  currentUser?: User | null;
}

export const TendersDirectory: React.FC<TendersDirectoryProps> = ({ 
  onSelectTender, 
  onReviewTender,
  currentUser 
}) => {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [tendersRes, catsData] = await Promise.all([
          api.getTenders(),
          api.getCategories().catch(() => [])
        ]);
        const tendersList: Tender[] = Array.isArray(tendersRes) ? tendersRes : (tendersRes.items || []);
        setTenders(tendersList);
        if (catsData && catsData.length > 0) {
          setCategories(catsData);
        } else {
          // Extract unique categories from tenders if categories endpoint was empty
          const uniqueCats: string[] = Array.from(new Set(tendersList.map(t => t.category).filter(Boolean)));
          setCategories(uniqueCats);
        }
      } catch (err) {
        console.error('Failed to load tenders data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filtered = tenders.filter(t => {
    const query = search.toLowerCase();
    const matchesSearch =
      (t.title && t.title.toLowerCase().includes(query)) ||
      (t.tender_code && t.tender_code.toLowerCase().includes(query)) ||
      (t.department && t.department.toLowerCase().includes(query)) ||
      (t.location && t.location.toLowerCase().includes(query));
    const matchesCategory = categoryFilter === 'ALL' || t.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const isCitizen = currentUser?.role === 'CITIZEN';

  const handleRowAction = (t: Tender) => {
    if (isCitizen && onReviewTender) {
      onReviewTender(t.tender_code);
    } else if (onSelectTender) {
      onSelectTender(t.id);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 animate-fade-in">
      {/* Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center border border-teal-200/60 shrink-0">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                Public Tenders Registry
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Audited procurement records, cost variances, and contractor bid histories ({tenders.length} tenders)
              </p>
            </div>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by code, title, department..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500 transition-colors"
            />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-bold focus:outline-none focus:border-teal-500 transition-colors"
          >
            <option value="ALL">All Categories ({categories.length})</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Mobile Card View (visible on mobile < 640px) */}
      <div className="sm:hidden space-y-3">
        {loading ? (
          <div className="p-8 text-center text-slate-400 bg-white rounded-2xl border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-teal-500 border-t-transparent mb-2"></div>
            <p className="text-xs">Loading public tenders...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-slate-400 bg-white rounded-2xl border border-slate-200">
            <p className="text-xs">No tenders match your search.</p>
          </div>
        ) : (
          filtered.map((t) => (
            <div
              key={t.id}
              onClick={() => handleRowAction(t)}
              className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-3 active:scale-[0.99] transition-transform cursor-pointer"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="font-mono text-xs font-black text-teal-700">{t.tender_code}</span>
                  <h3 className="text-sm font-bold text-slate-900 mt-0.5 leading-snug">{t.title}</h3>
                  <p className="text-[11px] text-slate-500">{t.department}</p>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200 shrink-0">
                  {t.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-100">
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium">Estimated Value</span>
                  <span className="font-mono font-bold text-slate-800">₹{t.estimated_value.toLocaleString('en-IN')}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium">Awarded Bid</span>
                  <span className="font-mono font-bold text-slate-800">
                    {t.winning_bid_amount ? `₹${t.winning_bid_amount.toLocaleString('en-IN')}` : 'In Bidding'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                <span>Vendor: <strong className="text-slate-800">{t.winning_vendor_name || 'Evaluation Pending'}</strong></span>
                <span className="text-teal-600 font-bold flex items-center gap-0.5">
                  {isCitizen ? 'Submit Review' : 'View Dossier'} <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Desktop & Tablet Table View (hidden on small mobile) */}
      <div className="hidden sm:block bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700 min-w-[750px]">
            <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200/80">
              <tr>
                <th className="py-3.5 px-4 font-bold">Tender Code</th>
                <th className="py-3.5 px-4 font-bold">Title & Department</th>
                <th className="py-3.5 px-4 font-bold">Category</th>
                <th className="py-3.5 px-4 font-bold text-right">Estimated Cost</th>
                <th className="py-3.5 px-4 font-bold text-right">Awarded Bid</th>
                <th className="py-3.5 px-4 font-bold">Winning Vendor</th>
                <th className="py-3.5 px-4 font-bold text-center">Status</th>
                <th className="py-3.5 px-4 font-bold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-teal-500 border-t-transparent mb-2"></div>
                    <p className="text-xs">Loading audited tenders from database...</p>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No procurement tenders found matching "{search}".
                  </td>
                </tr>
              ) : (
                filtered.map((t) => (
                  <tr 
                    key={t.id} 
                    onClick={() => handleRowAction(t)}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-teal-700 whitespace-nowrap">
                      {t.tender_code}
                    </td>
                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="font-bold text-slate-900 text-xs truncate group-hover:text-teal-600 transition-colors">
                        {t.title}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate">{t.department} • {t.location || 'India'}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 whitespace-nowrap font-medium">
                      {t.category}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-600 whitespace-nowrap">
                      ₹{t.estimated_value.toLocaleString('en-IN')}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold whitespace-nowrap">
                      {t.winning_bid_amount ? (
                        <div>
                          <span className={t.winning_bid_amount > t.estimated_value ? 'text-rose-600' : 'text-emerald-600'}>
                            ₹{t.winning_bid_amount.toLocaleString('en-IN')}
                          </span>
                          <span className={`block text-[10px] ${t.winning_bid_amount > t.estimated_value ? 'text-rose-600/80' : 'text-emerald-600/80'}`}>
                            {t.winning_bid_amount > t.estimated_value ? '+' : ''}
                            {(((t.winning_bid_amount - t.estimated_value) / t.estimated_value) * 100).toFixed(1)}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-slate-400 font-normal">In Bidding</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-800 max-w-[160px] truncate">
                      {t.winning_vendor_name || 'Evaluation Pending'}
                    </td>
                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
                        {t.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      {isCitizen ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onReviewTender) onReviewTender(t.tender_code);
                          }}
                          className="px-2.5 py-1 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-700 border border-teal-200/80 text-xs font-bold inline-flex items-center gap-1"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span>Review</span>
                        </button>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onSelectTender) onSelectTender(t.id);
                          }}
                          className="px-2.5 py-1 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-bold inline-flex items-center gap-1"
                        >
                          <span>Dossier</span>
                          <ArrowRight className="w-3 h-3 text-slate-400" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
