import React from 'react';
import { 
  Shield, LayoutDashboard, FileText, Building2, 
  AlertTriangle, MessageSquare, FileBarChart, 
  Award, LogOut, X 
} from 'lucide-react';
import { Role, User } from '../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentUser?: User | null;
  onRoleSwitch: (role: Role) => void;
  onLogout: () => void;
  alertsCount?: number;
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  onLogout,
  alertsCount = 0,
  isOpen = false,
  onClose,
}) => {
  const isCitizen = currentUser?.role === 'CITIZEN';

  const citizenNavItems = [
    { id: 'citizen', label: 'Citizen Hub', icon: MessageSquare, description: 'Submit & Track Reviews' },
    { id: 'tenders', label: 'Public Tenders', icon: FileText, description: 'Search & Review Tenders' },
    { id: 'leaderboard', label: 'Reviewer Ranking', icon: Award, description: 'Reputation Leaderboard' },
  ];

  const investigatorNavItems = [
    { id: 'dashboard', label: 'Investigator Command', icon: LayoutDashboard },
    { id: 'alerts', label: 'Investigation Queue', icon: AlertTriangle, badge: alertsCount },
    { id: 'tenders', label: 'Procurement Registry', icon: FileText },
    { id: 'vendors', label: 'Vendor Intelligence', icon: Building2 },
    { id: 'reports', label: 'Forensic Reports', icon: FileBarChart },
    { id: 'leaderboard', label: 'Citizen Audits', icon: Award },
  ];

  const navItems = isCitizen ? citizenNavItems : investigatorNavItems;

  const handleNavClick = (tabId: string) => {
    setActiveTab(tabId);
    if (onClose) onClose();
  };

  return (
    <>
      {/* Mobile Drawer Overlay Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-40 md:hidden transition-opacity duration-300"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between h-screen shadow-lg md:shadow-sm transition-transform duration-300 ease-in-out
        md:translate-x-0 md:static md:z-30 md:shrink-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div>
          {/* Logo Bar */}
          <div className="h-16 flex items-center justify-between px-6 border-b border-slate-100">
            <div 
              className="flex items-center gap-2.5 cursor-pointer select-none"
              onClick={() => handleNavClick('landing')}
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center shadow-md shadow-teal-500/20">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-1">
                  <span className="font-extrabold text-slate-900 text-lg tracking-tight">Procure<span className="text-teal-600">Shield</span></span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-teal-200/60">AI</span>
                </div>
                <p className="text-[10px] text-slate-400 font-medium tracking-wide uppercase">
                  {isCitizen ? 'Citizen Vigilance' : 'Forensic Audit'}
                </p>
              </div>
            </div>

            {/* Mobile Close Button */}
            <button
              onClick={onClose}
              className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Persona Badge */}
          <div className="px-4 pt-3 pb-1">
            <div className={`px-3 py-1.5 rounded-xl border text-[11px] font-bold flex items-center justify-between ${
              isCitizen 
                ? 'bg-blue-50/70 text-blue-800 border-blue-200/80' 
                : 'bg-teal-50/70 text-teal-800 border-teal-200/80'
            }`}>
              <span>{isCitizen ? 'Citizen Reviewer' : 'Forensic Investigator'}</span>
              <span className="w-2 h-2 rounded-full animate-pulse bg-emerald-500" />
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3.5 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id || 
                (item.id === 'alerts' && activeTab === 'case-detail') ||
                (item.id === 'citizen' && activeTab === 'citizen');

              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-teal-600 text-white shadow-md shadow-teal-600/20'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {'badge' in item && typeof item.badge === 'number' && item.badge > 0 && (
                    <span className={`px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                      isActive ? 'bg-white/20 text-white' : 'bg-red-50 text-red-600 border border-red-200'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Actions */}
        <div className="p-3.5 border-t border-slate-100 space-y-1">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut className="w-4 h-4 text-red-500" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
};
