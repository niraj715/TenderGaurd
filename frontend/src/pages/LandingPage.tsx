import React, { useState } from 'react';
import { 
  Shield, ArrowRight, Play, CheckCircle2, TrendingUp, Users, 
  AlertTriangle, Layers, FileCheck, Scale, Eye, X 
} from 'lucide-react';
import { KPIs, Role } from '../types';

interface LandingPageProps {
  kpis: KPIs | null;
  onExploreDashboard: () => void;
  onOpenAuth: (mode?: 'login' | 'register') => void;
  onSelectRole: (role: Role) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  kpis,
  onExploreDashboard,
  onOpenAuth,
  onSelectRole,
}) => {
  const [demoModalOpen, setDemoModalOpen] = useState(false);

  const lifecycleSteps = [
    { title: 'Tender', desc: 'Specifications & estimated value', icon: FileCheck },
    { title: 'Bidding', desc: 'Price spread & co-bidding patterns', icon: Scale },
    { title: 'Vendor', desc: 'Win-rate & corporate linkages', icon: Users },
    { title: 'Award', desc: 'Contract finalization & timeline', icon: CheckCircle2 },
    { title: 'Execution', desc: 'Milestones & delay tracking', icon: Layers },
    { title: 'Quality', desc: 'Laboratory tests & inspections', icon: AlertTriangle },
    { title: 'Citizen Feedback', desc: 'Geo-tagged verified photos', icon: Users },
    { title: 'Maintenance', desc: 'Lifecycle cost ratios vs peers', icon: TrendingUp },
    { title: 'Investigation', desc: 'Prioritized 360° case dossier', icon: Eye },
  ];

  return (
    <div className="space-y-16 pb-20 animate-fade-in">
      {/* Hero Section matching Top-Left in Mockup */}
      <section className="max-w-7xl mx-auto px-6 sm:px-12 pt-8 sm:pt-14">
        {/* Subtle Top-Right Subtitle */}
        <div className="flex justify-end mb-4">
          <span className="text-xs font-bold text-slate-400 tracking-wide uppercase">
            Transparent Systems, Stronger Tomorrows
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Left Column: Headline & Action Buttons */}
          <div className="lg:col-span-6 space-y-6">
            <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight leading-[1.08]">
              From Tender <br />
              <span className="text-teal-600">to Public Impact</span>
            </h1>

            <h2 className="text-base sm:text-lg font-bold text-slate-800 leading-snug">
              Transparent Procurement. Stronger Infrastructure. Better Communities.
            </h2>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-xl">
              ProcureShield uses AI to analyze government procurement from bidding to real-world outcomes — helping investigators detect risks and citizens voice their experience.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={onExploreDashboard}
                className="px-6 py-3 rounded-full text-xs font-bold text-white bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 shadow-md shadow-teal-600/25 transition-all flex items-center gap-2 group"
              >
                <span>Explore Dashboard</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => setDemoModalOpen(true)}
                className="px-6 py-3 rounded-full text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 shadow-xs transition-all flex items-center gap-2"
              >
                <div className="w-5 h-5 rounded-full bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Play className="w-2.5 h-2.5 fill-current ml-0.5" />
                </div>
                <span>Watch Demo</span>
              </button>
            </div>

            {/* Quick Persona Access for Testing */}
            <div className="pt-2 flex items-center gap-2 text-xs text-slate-500">
              <span className="text-[11px] font-semibold text-slate-400">Jump in as:</span>
              <button 
                onClick={() => onSelectRole('INVESTIGATOR')}
                className="px-2.5 py-1 rounded-lg bg-teal-50 text-teal-700 font-semibold text-[11px] hover:bg-teal-100 transition-colors"
              >
                Investigator
              </button>
              <button 
                onClick={() => onSelectRole('CITIZEN')}
                className="px-2.5 py-1 rounded-lg bg-sky-50 text-sky-700 font-semibold text-[11px] hover:bg-sky-100 transition-colors"
              >
                Citizen
              </button>
            </div>
          </div>

          {/* Right Column: Hero Visual with curved road & floating badge */}
          <div className="lg:col-span-6 relative">
            <div className="relative rounded-3xl overflow-hidden border border-slate-200 shadow-xl group">
              <img
                src="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=1000&auto=format&fit=crop&q=80"
                alt="Highway Infrastructure along lush mountains"
                className="w-full h-80 sm:h-96 object-cover transform group-hover:scale-105 transition-transform duration-700"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-transparent to-slate-900/10" />

              {/* Floating Badge as shown in Mockup */}
              <div className="absolute bottom-6 right-6 text-right">
                <p className="text-xl sm:text-2xl font-black text-white leading-tight drop-shadow-md">
                  Better Projects
                </p>
                <p className="text-lg sm:text-xl font-bold text-teal-300 leading-tight drop-shadow-md">
                  Stronger Communities
                </p>
              </div>

              {/* Verified Shield Badge on Top-Left */}
              <div className="absolute top-4 left-4 px-3 py-1.5 rounded-full bg-white/90 backdrop-blur-md border border-white/50 text-[11px] font-bold text-slate-800 flex items-center gap-1.5 shadow-sm">
                <Shield className="w-3.5 h-3.5 text-teal-600" />
                <span>360° Verified Auditing</span>
              </div>
            </div>
          </div>
        </div>

        {/* 4 Stat Strip at bottom of Hero */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12">
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs text-left">
            <p className="text-2xl sm:text-3xl font-black text-slate-900">
              {(kpis?.tenders_analyzed ?? 12482).toLocaleString()}
            </p>
            <p className="text-xs font-semibold text-slate-500 mt-0.5">Tenders Analysed</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs text-left">
            <p className="text-2xl sm:text-3xl font-black text-slate-900">
              {(kpis?.vendors_monitored ?? 8421).toLocaleString()}
            </p>
            <p className="text-xs font-semibold text-slate-500 mt-0.5">Vendors</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs text-left">
            <p className="text-2xl sm:text-3xl font-black text-red-600">
              {(kpis?.active_alerts ?? 347).toLocaleString()}
            </p>
            <p className="text-xs font-semibold text-slate-500 mt-0.5">Alerts</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs text-left">
            <p className="text-2xl sm:text-3xl font-black text-teal-600">
              2.3K
            </p>
            <p className="text-xs font-semibold text-slate-500 mt-0.5">Citizen Reviews</p>
          </div>
        </div>
      </section>

      {/* How It Works Section (PRD Section 8.3) */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-6 sm:px-12 pt-8">
        <div className="text-center mb-10">
          <span className="text-xs font-bold text-teal-600 uppercase tracking-widest">Complete Lifecycle Intelligence</span>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 mt-1">How ProcureShield Works</h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-xl mx-auto mt-2">
            Every public project is analyzed across 9 stages of procurement, ensuring that anomalies in bidding match verified facts in physical execution.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {lifecycleSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div key={idx} className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs hover:border-teal-300 transition-all">
                <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center mb-3">
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-teal-600">0{idx + 1}</span>
                  <h3 className="text-sm font-bold text-slate-900">{step.title}</h3>
                </div>
                <p className="text-xs text-slate-500 mt-1">{step.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* About & Responsible AI Statement (PRD Section 8.2 & 41) */}
      <section id="about" className="max-w-7xl mx-auto px-6 sm:px-12 pt-8">
        <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-md">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div className="space-y-4">
              <span className="text-xs font-bold text-teal-600 uppercase tracking-wider">Responsible AI Commitment</span>
              <h2 className="text-2xl font-black text-slate-900">
                AI does not accuse. AI connects evidence and prioritizes investigation.
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                ProcureShield was created to empower government auditors, researchers, and citizens with transparent intelligence. Unusually high pricing or delayed schedules alone do not imply corruption — which is why every signal provides peer benchmarks, historical comparisons, and links directly to ground inspection records.
              </p>
              <div className="flex items-center gap-4 pt-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                  <CheckCircle2 className="w-4 h-4 text-teal-600" />
                  <span>100% Explainable Signals</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                  <CheckCircle2 className="w-4 h-4 text-teal-600" />
                  <span>Human-in-the-Loop</span>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-3 text-xs text-slate-600">
              <h4 className="font-bold text-slate-900 text-sm">Flagship Investigation Case #1042</h4>
              <p>
                <strong>NH-21 Rural Road (12 km)</strong> received an Investigation Priority of <strong>91/100</strong> due to converging signals:
              </p>
              <ul className="space-y-1.5 list-disc list-inside text-slate-700">
                <li>Winning bid was 16% above comparable regional median</li>
                <li>Vendor won 9 of 10 similar tenders (award concentration)</li>
                <li>Corporate directorship overlap with co-bidders</li>
                <li>Project completed 105 days late with 37 verified citizen complaints</li>
                <li>Maintenance spending was 2.4× higher than peer benchmark</li>
              </ul>
              <button
                onClick={onExploreDashboard}
                className="mt-3 w-full py-2 rounded-xl text-xs font-bold text-teal-700 bg-teal-50 border border-teal-200 hover:bg-teal-100 transition-colors"
              >
                Inspect Case #1042 in 360° View →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Real-World Impact Section (matching Navbar anchor #impact) */}
      <section id="impact" className="max-w-7xl mx-auto px-6 sm:px-12 pt-8">
        <div className="text-center mb-10">
          <span className="text-xs font-bold text-teal-600 uppercase tracking-widest">Measurable Civic Impact</span>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 mt-1">Transforming Public Spending Accountability</h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-xl mx-auto mt-2">
            By connecting procurement data to verified on-site reality, ProcureShield bridges the gap between digital tender records and physical infrastructure quality.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center font-black text-sm">
              ₹
            </div>
            <h3 className="text-base font-bold text-slate-900">Fiscal Safeguards</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Detecting collusive bidding rings, single-bidder non-competitive anomalies, and 40%+ pricing escalations before public funds are disbursed.
            </p>
            <span className="inline-block text-[11px] font-bold text-teal-700 bg-teal-50 px-2.5 py-0.5 rounded-full">
              ₹1,280 Cr Under Review
            </span>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center font-black text-sm">
              ⏱
            </div>
            <h3 className="text-base font-bold text-slate-900">Execution Timeliness</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Monitoring critical milestones to flag chronic 100+ day delays, phantom work, and substandard asphalt density before projects deteriorate.
            </p>
            <span className="inline-block text-[11px] font-bold text-sky-700 bg-sky-50 px-2.5 py-0.5 rounded-full">
              89 Corrective Actions
            </span>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-black text-sm">
              🤝
            </div>
            <h3 className="text-base font-bold text-slate-900">Citizen Verification</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Equipping community members with verified geo-tagged photo audits, giving voice to local citizens and elevating their trust in governance.
            </p>
            <span className="inline-block text-[11px] font-bold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-full">
              2,300+ Verified Audits
            </span>
          </div>
        </div>
      </section>

      {/* Demo Modal */}
      {demoModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-fade-in">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                <Play className="w-4 h-4 text-teal-600" />
                <span>ProcureShield AI Platform Walkthrough</span>
              </h3>
              <button onClick={() => setDemoModalOpen(false)} className="p-1 text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="rounded-xl bg-slate-950 p-6 text-white text-xs space-y-3">
              <p className="text-teal-400 font-semibold">Interactive Platform Tour Ready:</p>
              <p>1. Open the <strong>Investigation Queue</strong> to review critical cases sorted by multi-signal risk.</p>
              <p>2. Drill down into <strong>Case #1042</strong> to inspect the Vendor Relationship Graph and Timeline.</p>
              <p>3. Switch to <strong>Citizen Mode</strong> to test the 4-step report submission and Reviewer Leaderboard.</p>
            </div>
            <button
              onClick={() => {
                setDemoModalOpen(false);
                onExploreDashboard();
              }}
              className="w-full py-2.5 rounded-xl font-bold text-xs text-white bg-teal-600 hover:bg-teal-500 transition-colors"
            >
              Launch Live Dashboard Now
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
