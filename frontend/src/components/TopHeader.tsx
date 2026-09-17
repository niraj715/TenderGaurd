import React, { useState } from 'react';
import { Search, Bell, ChevronDown, Menu, Check } from 'lucide-react';
import { User, Role } from '../types';

interface TopHeaderProps {
  currentUser: User | null;
  onRoleSwitch: (role: Role) => void;
  onOpenAuth: () => void;
  onSearch?: (query: string) => void;
  onToggleMobileMenu?: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  currentUser,
  onRoleSwitch,
  onOpenAuth,
  onSearch,
  onToggleMobileMenu,
}) => {
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [searchVal, setSearchVal] = useState('');

  const roles: { role: Role; label: string; name: string; dept: string }[] = [
    { role: 'INVESTIGATOR', label: 'Forensic Investigator', name: 'Sarah Chen', dept: 'Forensic Audit & Vigilance Cell' },
    { role: 'CITIZEN', label: 'Citizen Reviewer', name: 'Rohan Verma', dept: 'Public Infrastructure Watch' },
  ];

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSearch) {
      onSearch(searchVal);
    }
  };

  return (
    <header className="h-16 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20 shadow-sm">
      {/* Left: Mobile Menu Toggle & Title */}
      <div className="flex items-center gap-3">
        {onToggleMobileMenu && (
          <button
            onClick={onToggleMobileMenu}
            className="md:hidden p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div>
          <h2 className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider hidden sm:block">
            ProcureShield AI
          </h2>
          <p className="text-sm font-bold text-slate-900 leading-tight truncate">
            {currentUser?.role === 'CITIZEN' ? 'Citizen Oversight & Public Review' : 'Procurement Intelligence System'}
          </p>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2 sm:gap-4">
        {/* Search Bar */}
        <div className="relative w-44 sm:w-64 md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder={currentUser?.role === 'CITIZEN' ? "Search tenders to review..." : "Search tenders, cases..."}
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 hover:bg-slate-100/80 focus:bg-white border border-slate-200 rounded-xl text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/10 transition-all"
          />
        </div>

        {/* User Profile / Persona Selector */}
        <div className="relative">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center gap-2 p-1.5 pr-2.5 rounded-full hover:bg-slate-50 border border-slate-200/80 transition-all"
            aria-label="Switch Persona"
          >
            <img
              src={currentUser?.avatar_url || `https://api.dicebear.com/7.x/bottts/svg?seed=${currentUser?.name || 'User'}`}
              alt={currentUser?.name || 'User'}
              className="w-7 h-7 rounded-full object-cover border border-slate-200"
            />
            <div className="text-left hidden md:block">
              <p className="text-xs font-bold text-slate-800 leading-none">
                {currentUser?.name || 'Sarah Chen'}
              </p>
              <p className="text-[10px] text-slate-400 font-medium capitalize mt-0.5">
                {currentUser?.role === 'CITIZEN' ? 'Citizen Reviewer' : 'Investigator'}
              </p>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {/* Dropdown for instant role switching (ONLY 2 PERSONAS) */}
          {roleDropdownOpen && (
            <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-slate-200/80 py-2 z-50 animate-fade-in">
              <div className="px-3.5 py-2 border-b border-slate-100">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Switch Persona</p>
                <p className="text-xs text-slate-500 mt-0.5">Select role to verify RBAC access</p>
              </div>
              <div className="p-1 space-y-1">
                {roles.map((r) => {
                  const isCurrent = currentUser?.role === r.role;
                  return (
                    <button
                      key={r.role}
                      onClick={() => {
                        onRoleSwitch(r.role);
                        setRoleDropdownOpen(false);
                      }}
                      className={`w-full text-left p-2.5 rounded-xl transition-all flex items-start justify-between ${
                        isCurrent 
                          ? 'bg-teal-50 text-teal-900 border border-teal-200/60' 
                          : 'hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      <div>
                        <div className="flex items-center gap-1.5">
                          <p className="text-xs font-bold leading-tight">{r.name}</p>
                          <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                            r.role === 'CITIZEN' ? 'bg-blue-100 text-blue-700' : 'bg-teal-100 text-teal-700'
                          }`}>
                            {r.role}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400 mt-0.5">{r.dept}</p>
                      </div>
                      {isCurrent && <Check className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />}
                    </button>
                  );
                })}
              </div>
              <div className="pt-1 border-t border-slate-100 px-2">
                <button
                  onClick={() => {
                    onOpenAuth();
                    setRoleDropdownOpen(false);
                  }}
                  className="w-full text-center py-1.5 rounded-lg text-xs font-semibold text-teal-600 hover:bg-teal-50 transition-colors"
                >
                  Manage Account / Log In
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
