import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { TopHeader } from './components/TopHeader';
import { Sidebar } from './components/Sidebar';
import { Footer } from './components/Footer';
import { AuthModal } from './components/AuthModal';
import { LandingPage } from './pages/LandingPage';
import { InvestigatorDashboard } from './pages/InvestigatorDashboard';
import { CaseDetail360 } from './pages/CaseDetail360';
import { CitizenDashboard } from './pages/CitizenDashboard';
import { ReviewerLeaderboard } from './pages/ReviewerLeaderboard';
import { VendorsDirectory } from './pages/VendorsDirectory';
import { TendersDirectory } from './pages/TendersDirectory';
import { User, Role, KPIs } from './types';
import { api } from './services/api';
import { FileCheck, ExternalLink, Printer, ShieldAlert } from 'lucide-react';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<string>('landing');
  const [selectedAlertId, setSelectedAlertId] = useState<number>(1);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  // Sync state from URL query parameters on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab');
    const idParam = params.get('id');

    if (idParam && !isNaN(parseInt(idParam))) {
      setSelectedAlertId(parseInt(idParam));
    }

    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, []);

  // Sync URL query parameters when activeTab or selectedAlertId changes
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (activeTab === 'landing') {
      url.searchParams.delete('tab');
      url.searchParams.delete('id');
    } else {
      url.searchParams.set('tab', activeTab);
      if (activeTab === 'case-detail') {
        url.searchParams.set('id', selectedAlertId.toString());
      } else {
        url.searchParams.delete('id');
      }
    }
    window.history.replaceState({}, '', url.toString());
  }, [activeTab, selectedAlertId]);

  // Load user from localStorage or auto-demo login as Lead Investigator
  useEffect(() => {
    const storedUser = localStorage.getItem('ps_user');
    if (storedUser) {
      try {
        const u = JSON.parse(storedUser);
        setCurrentUser(u);
      } catch (e) {
        console.error(e);
      }
    } else {
      api.demoLogin('INVESTIGATOR').then(res => {
        setCurrentUser(res.user);
      }).catch(err => {
        console.error('Auto demo login', err);
      });
    }

    // Fetch dynamic platform KPIs
    api.getKPIs().then(setKpis).catch(console.error);
  }, []);

  // Strict RBAC Redirection Guard
  useEffect(() => {
    if (!currentUser) return;

    if (currentUser.role === 'CITIZEN') {
      const allowedCitizenTabs = ['landing', 'citizen', 'tenders', 'leaderboard'];
      if (!allowedCitizenTabs.includes(activeTab)) {
        setActiveTab('citizen');
      }
    }
  }, [currentUser, activeTab]);

  const handleRoleSwitch = async (role: Role) => {
    try {
      const res = await api.demoLogin(role);
      setCurrentUser(res.user);
      if (role === 'CITIZEN') {
        setActiveTab('citizen');
      } else {
        setActiveTab('dashboard');
      }
    } catch (err) {
      console.error('Failed to switch role', err);
    }
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    setActiveTab('landing');
  };

  const handleSelectCase = (alertId: number) => {
    if (currentUser?.role === 'CITIZEN') {
      // For citizens, clicking a case or tender opens the citizen review flow
      setActiveTab('citizen');
    } else {
      setSelectedAlertId(alertId);
      setActiveTab('case-detail');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const isAppMode = activeTab !== 'landing';

  return (
    <div className="min-h-screen bg-[#F0F4F8] text-slate-900 font-sans selection:bg-teal-500/20 selection:text-teal-900">
      {/* Public Landing View */}
      {!isAppMode ? (
        <div className="flex flex-col min-h-screen">
          <Navbar
            currentUser={currentUser}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            onOpenAuth={(mode) => {
              setAuthMode(mode || 'login');
              setIsAuthOpen(true);
            }}
            onLogout={handleLogout}
          />

          <main className="flex-grow">
            <LandingPage
              kpis={kpis}
              onExploreDashboard={() => {
                if (currentUser?.role === 'CITIZEN') {
                  setActiveTab('citizen');
                } else {
                  setActiveTab('dashboard');
                }
              }}
              onOpenAuth={(mode) => {
                setAuthMode(mode || 'login');
                setIsAuthOpen(true);
              }}
              onSelectRole={handleRoleSwitch}
            />
          </main>

          <Footer />
        </div>
      ) : (
        /* Authenticated Enterprise App Layout */
        <div className="flex h-screen overflow-hidden">
          {/* Responsive Navigation Sidebar */}
          <Sidebar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            currentUser={currentUser}
            onRoleSwitch={handleRoleSwitch}
            onLogout={handleLogout}
            alertsCount={kpis?.active_alerts ?? 0}
            isOpen={isMobileNavOpen}
            onClose={() => setIsMobileNavOpen(false)}
          />

          {/* Main Content Column */}
          <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
            {/* Top Header App Bar with Responsive Hamburger */}
            <TopHeader
              currentUser={currentUser}
              onRoleSwitch={handleRoleSwitch}
              onOpenAuth={() => {
                setAuthMode('login');
                setIsAuthOpen(true);
              }}
              onToggleMobileMenu={() => setIsMobileNavOpen(prev => !prev)}
              onSearch={(query) => {
                if (currentUser?.role === 'CITIZEN') {
                  setActiveTab('citizen');
                } else {
                  setActiveTab('tenders');
                }
              }}
            />

            {/* Active View Content Area */}
            <main className="flex-grow p-3 sm:p-5 lg:p-7">
              {/* INVESTIGATOR ONLY: Dashboard & Queue */}
              {(activeTab === 'dashboard' || activeTab === 'alerts') && (
                currentUser?.role === 'INVESTIGATOR' ? (
                  <InvestigatorDashboard
                    kpis={kpis}
                    onSelectCase={handleSelectCase}
                    onViewAllAlerts={() => setActiveTab('alerts')}
                  />
                ) : (
                  <UnauthorizedBanner onGoBack={() => setActiveTab('citizen')} />
                )
              )}

              {/* INVESTIGATOR ONLY: 360 Case Detail */}
              {activeTab === 'case-detail' && (
                currentUser?.role === 'INVESTIGATOR' ? (
                  <CaseDetail360
                    alertId={selectedAlertId}
                    onBack={() => setActiveTab('alerts')}
                  />
                ) : (
                  <UnauthorizedBanner onGoBack={() => setActiveTab('citizen')} />
                )
              )}

              {/* CITIZEN ONLY: Citizen Dashboard */}
              {activeTab === 'citizen' && (
                <CitizenDashboard
                  currentUser={currentUser}
                  onOpenAuth={() => {
                    setAuthMode('login');
                    setIsAuthOpen(true);
                  }}
                  onNavigateToLeaderboard={() => setActiveTab('leaderboard')}
                />
              )}

              {/* PUBLIC / BOTH: Reviewer Leaderboard */}
              {activeTab === 'leaderboard' && (
                <ReviewerLeaderboard 
                  onNavigateToFeedback={() => setActiveTab('citizen')}
                />
              )}

              {/* INVESTIGATOR ONLY: Vendor Intelligence */}
              {activeTab === 'vendors' && (
                currentUser?.role === 'INVESTIGATOR' ? (
                  <VendorsDirectory />
                ) : (
                  <UnauthorizedBanner onGoBack={() => setActiveTab('citizen')} />
                )
              )}

              {/* BOTH: Public Tenders Directory */}
              {activeTab === 'tenders' && (
                <TendersDirectory 
                  onSelectTender={handleSelectCase}
                  onReviewTender={(tenderCode) => {
                    setActiveTab('citizen');
                    const url = new URL(window.location.href);
                    url.searchParams.set('tab', 'citizen');
                    url.searchParams.set('tender', tenderCode);
                    window.history.pushState({}, '', url.toString());
                  }}
                  currentUser={currentUser}
                />
              )}

              {/* INVESTIGATOR ONLY: Forensic Reports */}
              {activeTab === 'reports' && (
                currentUser?.role === 'INVESTIGATOR' ? (
                  <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
                    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2.5">
                          <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center border border-teal-200/60">
                            <FileCheck className="w-5 h-5" />
                          </div>
                          <div>
                            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                              Forensic Audit Reports & Evidentiary Briefs
                            </h1>
                            <p className="text-xs text-slate-500 mt-0.5">
                              Cryptographically anchored dossiers compiled under Section 11 forensic vigilance standards
                            </p>
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={() => window.print()}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-sm shadow-teal-600/20 transition-all"
                      >
                        <Printer className="w-3.5 h-3.5" />
                        <span>Print Dossier</span>
                      </button>
                    </div>

                    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-5">
                      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                        <div>
                          <span className="text-xs font-bold text-teal-700 uppercase tracking-wider">Investigative Dossier</span>
                          <h2 className="text-lg font-bold text-slate-900 mt-0.5">Active Case Forensic Queue Summary</h2>
                        </div>
                        <span className="px-3 py-1 rounded-full text-xs font-bold bg-teal-50 text-teal-700 border border-teal-200">
                          Total Active Cases: {kpis?.active_alerts ?? 0}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
                          <span className="text-slate-400 font-semibold block mb-1">Tenders Analyzed</span>
                          <span className="font-bold text-slate-900 text-sm">{kpis?.tenders_analyzed ?? 500} Total Tenders</span>
                          <span className="block text-[11px] text-slate-500 mt-0.5">Automated 20-Indicator (C1–C20) Verification</span>
                        </div>
                        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
                          <span className="text-slate-400 font-semibold block mb-1">High-Risk Alerts</span>
                          <span className="font-bold text-red-600 text-sm">{kpis?.critical_cases ?? 0} Critical Priority Cases</span>
                          <span className="block text-[11px] text-slate-500 mt-0.5">Human forensic review recommended</span>
                        </div>
                        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
                          <span className="text-slate-400 font-semibold block mb-1">Citizen Feedback</span>
                          <span className="font-bold text-emerald-600 text-sm">{kpis?.citizen_reviews ?? 0} Verified Community Audits</span>
                          <span className="block text-[11px] text-slate-500 mt-0.5">Ground-level field validation active</span>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                        <span className="text-[11px] text-slate-400">Section 11 Automated Audit Pipeline</span>
                        <button
                          onClick={() => handleSelectCase(1)}
                          className="text-xs font-bold text-teal-600 hover:text-teal-700 inline-flex items-center gap-1"
                        >
                          <span>Open Detailed Case Dossier #1</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <UnauthorizedBanner onGoBack={() => setActiveTab('citizen')} />
                )
              )}
            </main>
          </div>
        </div>
      )}

      {/* Global Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        initialMode={authMode}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(user) => {
          setCurrentUser(user);
          if (user.role === 'CITIZEN') setActiveTab('citizen');
          else setActiveTab('dashboard');
        }}
      />
    </div>
  );
};

const UnauthorizedBanner: React.FC<{ onGoBack: () => void }> = ({ onGoBack }) => (
  <div className="max-w-2xl mx-auto my-12 bg-white rounded-2xl border border-amber-200 p-8 shadow-sm text-center space-y-4">
    <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200">
      <ShieldAlert className="w-6 h-6" />
    </div>
    <div>
      <h3 className="text-lg font-bold text-slate-900">Investigator Access Required</h3>
      <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
        This forensic module is restricted to authorized investigators. As a Citizen Reviewer, you have access to Public Tenders, Review Submission, and Community Rankings.
      </p>
    </div>
    <button
      onClick={onGoBack}
      className="px-5 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition-colors shadow-sm shadow-teal-600/20"
    >
      Return to Citizen Hub
    </button>
  </div>
);

export default App;

