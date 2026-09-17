import React from 'react';
import { Shield, ArrowRight } from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  currentUser: User | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenAuth: (mode?: 'login' | 'register') => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentUser,
  activeTab,
  setActiveTab,
  onOpenAuth,
  onLogout,
}) => {
  return (
    <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200/70 sticky top-0 z-40 px-6 sm:px-12 flex items-center justify-between">
      {/* Brand Logo */}
      <div 
        className="flex items-center gap-2.5 cursor-pointer select-none"
        onClick={() => setActiveTab('landing')}
      >
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-cyan-500 flex items-center justify-center shadow-md shadow-teal-600/20">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <span className="font-extrabold text-slate-900 text-xl tracking-tight">
          Procure<span className="text-teal-600">Shield</span>
        </span>
      </div>

      {/* Nav Links as shown in Top-Left of Mockup */}
      <nav className="hidden md:flex items-center gap-8">
        <button
          onClick={() => {
            setActiveTab('landing');
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          className={`text-xs font-bold transition-colors ${
            activeTab === 'landing' ? 'text-teal-600' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Home
        </button>

        <a
          href="#about"
          className="text-xs font-bold text-slate-600 hover:text-slate-900 transition-colors"
        >
          About
        </a>

        <a
          href="#how-it-works"
          className="text-xs font-bold text-slate-600 hover:text-slate-900 transition-colors"
        >
          How It Works
        </a>

        <a
          href="#impact"
          className="text-xs font-bold text-slate-600 hover:text-slate-900 transition-colors"
        >
          Impact
        </a>
      </nav>

      {/* Right Buttons: Log In & Get Started */}
      <div className="flex items-center gap-3">
        {currentUser ? (
          <div className="flex items-center gap-3">
            <button
              onClick={() => setActiveTab('dashboard')}
              className="px-5 py-2 rounded-full text-xs font-bold text-white bg-gradient-to-r from-teal-600 to-cyan-600 hover:opacity-95 shadow-md shadow-teal-600/20 transition-all flex items-center gap-1.5"
            >
              <span>Go to App</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onLogout}
              className="text-xs font-semibold text-slate-500 hover:text-red-600 px-2"
            >
              Logout
            </button>
          </div>
        ) : (
          <>
            <button
              onClick={() => onOpenAuth('login')}
              className="px-5 py-2 rounded-full text-xs font-bold text-teal-800 bg-sky-50 hover:bg-sky-100/80 border border-sky-200/80 transition-all"
            >
              Log In
            </button>

            <button
              onClick={() => onOpenAuth('register')}
              className="px-5 py-2 rounded-full text-xs font-bold text-white bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 shadow-md shadow-teal-600/20 transition-all"
            >
              Get Started
            </button>
          </>
        )}
      </div>
    </header>
  );
};
