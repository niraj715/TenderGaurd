import React, { useState, useEffect } from 'react';
import { Award, CheckCircle2, Heart, MessageSquare, ArrowRight, ShieldCheck, Sparkles, Trophy, User } from 'lucide-react';
import { ReviewerProfile } from '../types';
import { api } from '../services/api';

interface ReviewerLeaderboardProps {
  onNavigateToFeedback?: () => void;
}

export const ReviewerLeaderboard: React.FC<ReviewerLeaderboardProps> = ({ onNavigateToFeedback }) => {
  const [leaderboard, setLeaderboard] = useState<ReviewerProfile[]>([]);
  const [myProfile, setMyProfile] = useState<ReviewerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<'this_month' | 'all_time' | 'my_rank'>('all_time');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [lbData, myData] = await Promise.all([
          api.getLeaderboard().catch(() => []),
          api.getMyReviewerProfile().catch(() => null)
        ]);
        setLeaderboard(lbData || []);
        if (myData) setMyProfile(myData);
      } catch (err) {
        console.error('Failed to load leaderboard', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeFilter]);

  // Avatar photos pool for aesthetic citizen rendering
  const avatarPool = [
    'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80'
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6 animate-fade-in">
      {/* Container Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 sm:p-7">
        {/* Header with Title and Filter Pills */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-200/60">
                <Trophy className="w-4 h-4" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                Top Citizen Reviewers Leaderboard
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Community members contributing certified ground truth and geo-tagged defect reports
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200/60 text-xs">
            <button
              onClick={() => setActiveFilter('all_time')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeFilter === 'all_time'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All Time
            </button>
            <button
              onClick={() => setActiveFilter('this_month')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeFilter === 'this_month'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              This Month
            </button>
            <button
              onClick={() => setActiveFilter('my_rank')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeFilter === 'my_rank'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              My Rank
            </button>
          </div>
        </div>

        {/* Dynamic Reviewer List from Database */}
        <div className="divide-y divide-slate-100 mt-2">
          {loading ? (
            <div className="py-12 text-center text-slate-400">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-teal-500 border-t-transparent mb-2"></div>
              <p className="text-xs">Loading reviewer rankings...</p>
            </div>
          ) : leaderboard.length === 0 ? (
            <div className="py-12 text-center text-slate-400">
              <p className="text-xs">No reviewer profiles recorded yet.</p>
            </div>
          ) : (
            leaderboard.map((rev, idx) => {
              const rank = rev.rank || idx + 1;
              const avatar = avatarPool[idx % avatarPool.length];
              const badgeText = rev.badges && rev.badges.length > 0 ? rev.badges[0] : 'Community Watcher';

              return (
                <div
                  key={rev.id}
                  className="py-3.5 px-2 sm:px-3 flex items-center justify-between hover:bg-slate-50/80 rounded-xl transition-colors group"
                >
                  <div className="flex items-center gap-3.5">
                    {/* Rank indicator */}
                    <div className="w-7 text-center font-bold text-sm shrink-0">
                      {rank === 1 ? (
                        <span className="w-7 h-7 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center font-extrabold text-xs shadow-xs">
                          1
                        </span>
                      ) : rank === 2 ? (
                        <span className="w-7 h-7 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center font-extrabold text-xs">
                          2
                        </span>
                      ) : rank === 3 ? (
                        <span className="w-7 h-7 rounded-full bg-amber-50 text-amber-900 flex items-center justify-center font-extrabold text-xs border border-amber-200">
                          3
                        </span>
                      ) : (
                        <span className="text-slate-400 font-semibold">{rank}</span>
                      )}
                    </div>

                    {/* Avatar */}
                    <img
                      src={avatar}
                      alt={rev.user_name}
                      className="w-10 h-10 rounded-full object-cover border border-slate-200 shadow-xs shrink-0"
                    />

                    {/* Name & Stats */}
                    <div>
                      <div className="flex items-center gap-1.5">
                        <h3 className="font-bold text-slate-900 text-sm">{rev.user_name}</h3>
                        <CheckCircle2 className="w-3.5 h-3.5 text-teal-600" />
                      </div>
                      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 mt-0.5">
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3 text-slate-400" />
                          {rev.total_reports} audits
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1 text-teal-700 font-semibold">
                          <ShieldCheck className="w-3 h-3" />
                          {rev.verified_reports} verified
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Badge & Score */}
                  <div className="flex items-center gap-3">
                    <span className="hidden sm:inline-flex px-2.5 py-1 rounded-full text-xs font-semibold border bg-teal-50 text-teal-700 border-teal-200">
                      {badgeText}
                    </span>

                    <div className="text-right shrink-0">
                      <div className="text-xs font-extrabold text-slate-900 font-mono">
                        {rev.reputation_score}
                        <span className="text-[10px] text-slate-400 font-normal">/100</span>
                      </div>
                      <div className="text-[10px] text-teal-600 font-medium flex items-center gap-0.5 justify-end">
                        <ShieldCheck className="w-3 h-3" />
                        Reputation
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Your Rank Pinned Card */}
        <div className="mt-6 p-4 rounded-xl bg-slate-900 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md shadow-slate-900/10">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-full bg-teal-500/20 border border-teal-400/30 flex items-center justify-center font-bold text-teal-300 shrink-0">
              #{myProfile ? myProfile.rank : 1}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-white">
                  Your Rank #{myProfile ? myProfile.rank : 1}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-teal-500/20 text-teal-300 border border-teal-400/20">
                  {myProfile?.badges?.[0] || 'Active Citizen'}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {myProfile ? myProfile.total_reports : 0} reviews • {myProfile ? myProfile.verified_reports : 0} verified • {myProfile ? myProfile.reputation_score : 85}/100 Trust Score
              </p>
            </div>
          </div>

          <button
            onClick={onNavigateToFeedback}
            className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs transition-all shadow-sm group whitespace-nowrap"
          >
            <span>Submit Project Audit</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>

      {/* PRD Methodology Note */}
      <div className="p-4 rounded-xl bg-white border border-slate-200/80 text-xs text-slate-600 flex items-start gap-3">
        <div className="p-2 rounded-lg bg-teal-50 text-teal-600 border border-teal-100 shrink-0">
          <Sparkles className="w-4 h-4" />
        </div>
        <div className="space-y-1">
          <h4 className="font-bold text-slate-900">Algorithmic Reputation Guardrails (PRD Section 12)</h4>
          <p className="text-slate-500 text-[11px] leading-relaxed">
            Reputation scores reflect verified objective audit metrics: GPS accuracy, photo forensic integrity, and confirmation by site inspectors. Popularity metrics cannot override verified photographic defect audits.
          </p>
        </div>
      </div>
    </div>
  );
};
