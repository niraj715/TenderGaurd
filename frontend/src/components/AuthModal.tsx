import React, { useState } from 'react';
import { 
  X, Shield, Eye, EyeOff, User, Search, Landmark, 
  BarChart3, ArrowRight, Check, CheckCircle2 
} from 'lucide-react';
import { api } from '../services/api';
import { User as UserType, Role } from '../types';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: UserType) => void;
  initialMode?: 'login' | 'register' | 'role';
}

export const AuthModal: React.FC<AuthModalProps> = ({ 
  isOpen, 
  onClose, 
  onSuccess,
  initialMode = 'login' 
}) => {
  const [mode, setMode] = useState<'login' | 'register' | 'role'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [selectedRole, setSelectedRole] = useState<Role>('INVESTIGATOR');
  const [rememberMe, setRememberMe] = useState(true);
  const [agreedTerms, setAgreedTerms] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleDemo = async (roleType: Role) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.demoLogin(roleType);
      onSuccess(res.user);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.login(email, password);
      onSuccess(res.user);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Incorrect email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (!agreedTerms) {
      setError('Please agree to the Terms of Service and Privacy Policy');
      return;
    }
    setMode('role'); // Advance to Choose Your Role step as shown in mockup
  };

  const handleCompleteRoleSelection = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.register(name || 'New Member', email, password, selectedRole);
      onSuccess(res.user);
      onClose();
    } catch (err: any) {
      // If user already exists, try logging in with selected role
      try {
        const demoRes = await api.demoLogin(selectedRole);
        onSuccess(demoRes.user);
        onClose();
      } catch {
        setError(err.message || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-md rounded-2xl bg-white/95 backdrop-blur-xl border border-slate-200/90 shadow-2xl overflow-hidden">
        
        {/* macOS Style Window Dots Header */}
        <div className="px-5 pt-4 pb-2 flex items-center justify-between border-b border-slate-100">
          <div className="window-dots">
            <span className="window-dot-red" />
            <span className="window-dot-yellow" />
            <span className="window-dot-green" />
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6 pt-5">
          {/* Logo Header */}
          <div className="text-center mb-5">
            <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl bg-teal-50 text-teal-600 border border-teal-200/70 mb-2.5 shadow-sm">
              <Shield className="w-6 h-6 text-teal-600" />
            </div>
            
            {mode === 'login' && (
              <>
                <h3 className="text-xl font-black text-slate-900 tracking-tight">Welcome Back</h3>
                <p className="text-xs text-slate-500 mt-1">Login to continue to a more transparent tomorrow.</p>
              </>
            )}

            {mode === 'register' && (
              <>
                <h3 className="text-xl font-black text-slate-900 tracking-tight">Create Your Account</h3>
                <p className="text-xs text-slate-500 mt-1">Join us in building transparent public infrastructure.</p>
              </>
            )}

            {mode === 'role' && (
              <>
                <h3 className="text-xl font-black text-slate-900 tracking-tight">Choose Your Role</h3>
                <p className="text-xs text-slate-500 mt-1">Tell us how you'll be using ProcureShield.</p>
              </>
            )}
          </div>

          {error && (
            <div className="p-3 mb-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-xs font-medium">
              {error}
            </div>
          )}

          {/* MODE 1: LOGIN (Welcome Back) */}
          {mode === 'login' && (
            <div className="space-y-4">
              {/* Instant 1-Click Demo Personas */}
              <div className="p-3 rounded-xl bg-teal-50/50 border border-teal-200/60">
                <p className="text-[10px] font-bold text-teal-800 uppercase tracking-wider mb-2 flex items-center gap-1">
                  <span>⚡</span> Instant Demo Personas (1-Click)
                </p>
                <div className="grid grid-cols-2 gap-1.5">
                  <button
                    onClick={() => handleDemo('INVESTIGATOR')}
                    disabled={loading}
                    className="p-2 rounded-lg bg-white border border-teal-100 hover:border-teal-400 text-left transition-all shadow-xs"
                  >
                    <p className="text-xs font-bold text-slate-800 leading-tight">Sarah Chen</p>
                    <p className="text-[10px] text-teal-600 font-medium">Lead Investigator</p>
                  </button>
                  <button
                    onClick={() => handleDemo('CITIZEN')}
                    disabled={loading}
                    className="p-2 rounded-lg bg-white border border-teal-100 hover:border-teal-400 text-left transition-all shadow-xs"
                  >
                    <p className="text-xs font-bold text-slate-800 leading-tight">Rohan Verma</p>
                    <p className="text-[10px] text-teal-600 font-medium">#1 Citizen Reviewer</p>
                  </button>
                </div>
              </div>

              <div className="relative flex py-1 items-center">
                <div className="flex-grow border-t border-slate-200"></div>
                <span className="flex-shrink mx-3 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">or continue with</span>
                <div className="flex-grow border-t border-slate-200"></div>
              </div>

              <form onSubmit={handleLoginSubmit} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Email or Username</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:bg-white focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/15 transition-all"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-semibold text-slate-700">Password</label>
                    <a href="#forgot" className="text-[11px] font-medium text-teal-600 hover:underline">Forgot password?</a>
                  </div>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full px-3.5 py-2 pr-9 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:bg-white focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/15 transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    >
                      {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-0.5">
                  <input
                    type="checkbox"
                    id="remember"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-3.5 h-3.5 rounded text-teal-600 focus:ring-teal-500"
                  />
                  <label htmlFor="remember" className="text-xs text-slate-600">Remember me</label>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 shadow-md shadow-teal-600/20 transition-all disabled:opacity-50"
                >
                  {loading ? 'Signing in...' : 'Login'}
                </button>
              </form>

              {/* SSO / Demo Persona Buttons */}
              <div className="space-y-2 pt-1">
                <button 
                  type="button"
                  onClick={() => handleDemo('INVESTIGATOR')}
                  className="w-full py-2.5 px-3 rounded-xl border border-teal-200 bg-teal-50/50 hover:bg-teal-50 text-xs font-bold text-teal-800 flex items-center justify-center gap-2 transition-all shadow-sm"
                >
                  <Search className="w-4 h-4 text-teal-600" />
                  <span>Demo Login as Lead Investigator (Sarah Chen)</span>
                </button>

                <button 
                  type="button"
                  onClick={() => handleDemo('CITIZEN')}
                  className="w-full py-2.5 px-3 rounded-xl border border-slate-200 hover:bg-slate-50 text-xs font-bold text-slate-700 flex items-center justify-center gap-2 transition-colors"
                >
                  <User className="w-4 h-4 text-slate-600" />
                  <span>Demo Login as Citizen Auditor (Rohan Verma)</span>
                </button>
              </div>

              <div className="text-center pt-2">
                <p className="text-xs text-slate-500">
                  Don't have an account?{' '}
                  <button
                    onClick={() => setMode('register')}
                    className="font-bold text-teal-600 hover:underline"
                  >
                    Sign up
                  </button>
                </p>
              </div>
            </div>
          )}

          {/* MODE 2: REGISTER (Create Your Account) */}
          {mode === 'register' && (
            <form onSubmit={handleRegisterSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your full name"
                  className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:bg-white focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/15 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:bg-white focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/15 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a strong password"
                  className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:bg-white focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/15 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Confirm Password</label>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:bg-white focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/15 transition-all"
                />
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="agreeTerms"
                  checked={agreedTerms}
                  onChange={(e) => setAgreedTerms(e.target.checked)}
                  className="w-3.5 h-3.5 rounded text-teal-600 focus:ring-teal-500"
                />
                <label htmlFor="agreeTerms" className="text-[11px] text-slate-600">
                  I agree to the <span className="text-teal-600 underline cursor-pointer">Terms of Service</span> and <span className="text-teal-600 underline cursor-pointer">Privacy Policy</span>
                </label>
              </div>

              <button
                type="submit"
                className="w-full mt-2 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 shadow-md shadow-teal-600/20 transition-all"
              >
                Create Account
              </button>

              <div className="text-center pt-2">
                <p className="text-xs text-slate-500">
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={() => setMode('login')}
                    className="font-bold text-teal-600 hover:underline"
                  >
                    Login
                  </button>
                </p>
              </div>
            </form>
          )}

          {/* MODE 3: CHOOSE YOUR ROLE (Top Right in Mockup) */}
          {mode === 'role' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Citizen */}
                <button
                  type="button"
                  onClick={() => setSelectedRole('CITIZEN')}
                  className={`p-4 rounded-xl text-left transition-all border ${
                    selectedRole === 'CITIZEN'
                      ? 'border-teal-600 bg-teal-50/60 ring-2 ring-teal-500/20'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="w-8 h-8 rounded-lg bg-teal-100/70 text-teal-700 flex items-center justify-center mb-2">
                    <User className="w-4 h-4" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900">Citizen Reviewer</h4>
                  <p className="text-[10px] text-slate-500 mt-1 leading-tight">
                    Submit verified field reviews, upload geo-tagged photos, and build civic reputation.
                  </p>
                </button>

                {/* Investigator */}
                <button
                  type="button"
                  onClick={() => setSelectedRole('INVESTIGATOR')}
                  className={`p-4 rounded-xl text-left transition-all border ${
                    selectedRole === 'INVESTIGATOR'
                      ? 'border-teal-600 bg-teal-50/60 ring-2 ring-teal-500/20'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="w-8 h-8 rounded-lg bg-teal-100/70 text-teal-700 flex items-center justify-center mb-2">
                    <Search className="w-4 h-4" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900">Investigator</h4>
                  <p className="text-[10px] text-slate-500 mt-1 leading-tight">
                    Analyze C1–C20 forensic signals, investigate high-risk alerts, and manage dossiers.
                  </p>
                </button>
              </div>

              <div className="flex items-center justify-between pt-3">
                <button
                  type="button"
                  onClick={() => setMode('register')}
                  className="text-xs font-medium text-slate-400 hover:text-slate-600"
                >
                  Back
                </button>

                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={handleCompleteRoleSelection}
                    className="text-xs font-medium text-slate-500 hover:text-slate-700"
                  >
                    Skip for now
                  </button>
                  <button
                    type="button"
                    onClick={handleCompleteRoleSelection}
                    disabled={loading}
                    className="w-9 h-9 rounded-full bg-teal-600 hover:bg-teal-500 text-white flex items-center justify-center shadow-md shadow-teal-600/25 transition-all"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
