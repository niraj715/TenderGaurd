import React, { useState, useEffect } from 'react';
import { Building2, Search, GitBranch, ShieldAlert, ArrowUpRight, CheckCircle2, ChevronRight, X } from 'lucide-react';
import { Vendor, VendorNetwork } from '../types';
import { api } from '../services/api';
import { NetworkGraph } from '../components/NetworkGraph';

export const VendorsDirectory: React.FC = () => {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedVendorForNetwork, setSelectedVendorForNetwork] = useState<Vendor | null>(null);
  const [networkData, setNetworkData] = useState<VendorNetwork | null>(null);
  const [viewMode, setViewMode] = useState<'directory' | 'graph'>('graph'); // Default to Graph mode matching mockup!

  useEffect(() => {
    const fetchVendors = async () => {
      setLoading(true);
      try {
        const data = await api.getVendors();
        setVendors(data);
        if (data.length > 0) {
          // Preload network for flagship vendor BuildRight
          const flagship = data.find(v => v.name.includes('BuildRight')) || data[0];
          setSelectedVendorForNetwork(flagship);
          api.getVendorNetwork(flagship.id).then(setNetworkData).catch(console.error);
        }
      } catch (err) {
        console.error('Failed to load vendors', err);
      } finally {
        setLoading(false);
      }
    };
    fetchVendors();
  }, []);

  const handleOpenNetwork = async (v: Vendor) => {
    setSelectedVendorForNetwork(v);
    try {
      const net = await api.getVendorNetwork(v.id);
      setNetworkData(net);
    } catch (err) {
      console.error('Failed to load network', err);
    }
  };

  const filtered = vendors.filter(v => 
    v.name.toLowerCase().includes(search.toLowerCase()) ||
    v.category.toLowerCase().includes(search.toLowerCase()) ||
    v.registration_number.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 animate-fade-in">
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center border border-teal-200/60">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
                Vendor Relationship Network & Directory
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Investigating shared directorships, registered premises, and repeat collusive bidding patterns
              </p>
            </div>
          </div>
        </div>

        {/* Mode Switcher */}
        <div className="flex items-center gap-2">
          <div className="flex items-center p-1 bg-slate-100 rounded-xl border border-slate-200/60 text-xs">
            <button
              onClick={() => setViewMode('graph')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                viewMode === 'graph' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Interactive Graph
            </button>
            <button
              onClick={() => setViewMode('directory')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                viewMode === 'directory' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Vendor Registry ({vendors.length})
            </button>
          </div>
        </div>
      </div>

      {/* Main View Area */}
      {viewMode === 'graph' ? (
        <div className="space-y-6">
          {/* Active Graph Container matching reference mockup */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-base font-bold text-slate-900">Vendor Relationship Network</h2>
                <p className="text-xs text-slate-500">
                  Target Entity: <span className="font-semibold text-teal-700">{selectedVendorForNetwork?.name || 'BuildRight Infra Pvt Ltd'}</span>
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
                  Nexus Severity: High (8 Collusions)
                </span>
              </div>
            </div>

            <NetworkGraph 
              network={networkData} 
            />
          </div>

          {/* Quick Select Vendor Pill Row */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-sm flex items-center gap-3 overflow-x-auto">
            <span className="text-xs font-bold text-slate-500 whitespace-nowrap">Switch Target Entity:</span>
            {vendors.slice(0, 5).map((v) => (
              <button
                key={v.id}
                onClick={() => handleOpenNetwork(v)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
                  selectedVendorForNetwork?.id === v.id
                    ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {v.name}
              </button>
            ))}
          </div>
        </div>
      ) : (
        /* Table View */
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between gap-4">
            <div className="relative w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search vendor by name or GST..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500"
              />
            </div>
            <span className="text-xs text-slate-400 font-medium">Showing {filtered.length} registered contractors</span>
          </div>

          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200/80">
              <tr>
                <th className="py-3 px-4 font-bold">Vendor Name</th>
                <th className="py-3 px-4 font-bold">Category</th>
                <th className="py-3 px-4 font-bold text-center">Win Rate</th>
                <th className="py-3 px-4 font-bold text-right">Total Volume</th>
                <th className="py-3 px-4 font-bold text-center">Avg Delay</th>
                <th className="py-3 px-4 font-bold text-center">Risk Rating</th>
                <th className="py-3 px-4 font-bold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={7} className="py-10 text-center text-slate-400">Loading vendors...</td></tr>
              ) : filtered.map((v) => (
                <tr key={v.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-bold text-slate-900 text-sm">{v.name}</div>
                    <div className="text-[10px] font-mono text-slate-400">{v.registration_number}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-600">{v.category}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`font-bold ${v.win_rate >= 0.7 ? 'text-rose-600' : 'text-slate-800'}`}>
                      {Math.round(v.win_rate * 100)}% ({v.total_contracts} awards)
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-semibold text-teal-700">
                    ₹{v.total_contract_value.toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`font-semibold ${v.avg_delay_days > 40 ? 'text-rose-600' : 'text-slate-600'}`}>
                      +{Math.round(v.avg_delay_days)} Days
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      v.risk_level === 'CRITICAL' ? 'badge-critical' : v.risk_level === 'HIGH' ? 'badge-high' : 'badge-low'
                    }`}>
                      {v.risk_level}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => {
                        handleOpenNetwork(v);
                        setViewMode('graph');
                      }}
                      className="px-2.5 py-1 rounded-lg bg-teal-50 text-teal-700 hover:bg-teal-100 border border-teal-200/80 text-xs font-semibold inline-flex items-center gap-1"
                    >
                      <GitBranch className="w-3.5 h-3.5" />
                      <span>Explore Nexus</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

