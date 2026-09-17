import React from 'react';
import { Shield, CheckCircle2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="backdrop-blur-xl bg-slate-950/90 border-t border-white/10 text-slate-400 text-xs py-10 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-cyan-400" />
              <span className="text-white font-bold text-base">ProcureShield AI</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              Explainable public procurement intelligence and investigation prioritization platform. Connecting the dots from tender publication to delivered citizen impact.
            </p>
            <div className="text-[11px] text-cyan-400 font-medium">
              Version 1.0 • Enterprise GovTech Suite
            </div>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Platform Modules</h4>
            <ul className="space-y-2 text-xs">
              <li><span className="text-slate-300 hover:text-cyan-400 cursor-pointer">Investigation Queue</span></li>
              <li><span className="text-slate-300 hover:text-cyan-400 cursor-pointer">360° Case Dossier View</span></li>
              <li><span className="text-slate-300 hover:text-cyan-400 cursor-pointer">Vendor Relationship Graph</span></li>
              <li><span className="text-slate-300 hover:text-cyan-400 cursor-pointer">Price Benchmarking Engine</span></li>
              <li><span className="text-slate-300 hover:text-cyan-400 cursor-pointer">Citizen Feedback & Reviewer Ranking</span></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Responsible AI</h4>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-white/10 space-y-2">
              <div className="flex items-start gap-2 text-cyan-300 text-xs font-medium">
                <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <span>Detection, Not Accusation</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                All risk scores and pattern signals are prioritized intelligence for human auditors. AI does not render legal verdicts or blacklist entities.
              </p>
            </div>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Governance & Audit</h4>
            <ul className="space-y-2 text-xs">
              <li><span className="text-slate-400">WCAG 2.1 AA Compliant</span></li>
              <li><span className="text-slate-400">Tamper-Evident Action Audit Logs</span></li>
              <li><span className="text-slate-400">Contextual Peer Median Clustering</span></li>
              <li><span className="text-slate-400">Citizen Evidence Integrity Verification</span></li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 text-[11px]">
          <p>© 2024 ProcureShield AI. All rights reserved. Built for public procurement transparency.</p>
          <div className="flex items-center gap-1">
            <span>Tagline:</span>
            <span className="text-cyan-400 font-medium">From Tender to Public Impact</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
