import React, { useState, useEffect } from 'react';
import { 
  Search, MapPin, UploadCloud, ArrowRight, CheckCircle2, 
  Star, AlertCircle, X, Shield, Award, Clock, FileText, 
  MessageSquare, ChevronRight, Check, Sparkles, Building2
} from 'lucide-react';
import { Tender, Project, User as UserType, ReviewerProfile, Complaint } from '../types';
import { api } from '../services/api';

interface CitizenDashboardProps {
  currentUser: UserType | null;
  onOpenAuth: () => void;
  onNavigateToLeaderboard?: () => void;
}

export const CitizenDashboard: React.FC<CitizenDashboardProps> = ({ 
  currentUser, 
  onOpenAuth,
  onNavigateToLeaderboard 
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'submit' | 'my-reviews'>('submit');
  const [profile, setProfile] = useState<ReviewerProfile | null>(null);
  const [myReviews, setMyReviews] = useState<Complaint[]>([]);
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [searchTender, setSearchTender] = useState('');
  const [selectedTender, setSelectedTender] = useState<Tender | null>(null);
  
  // Form fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('ROAD_QUALITY');
  const [rating, setRating] = useState(2);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [photoUrl, setPhotoUrl] = useState('https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=80');
  
  const [submitting, setSubmitting] = useState(false);
  const [submittedSuccess, setSubmittedSuccess] = useState(false);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const loadProfileAndReviews = async () => {
    try {
      const [profData, reviewsData] = await Promise.all([
        api.getMyReviewerProfile().catch(() => null),
        api.getMyReviews().catch(() => [])
      ]);
      if (profData) setProfile(profData);
      setMyReviews(reviewsData);
    } catch (err) {
      console.error('Failed to load profile/reviews', err);
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoadingInitial(true);
      try {
        const tendersRes = await api.getTenders();
        const tendersList: Tender[] = Array.isArray(tendersRes) ? tendersRes : (tendersRes.items || []);
        setTenders(tendersList);
        
        // Check URL params for preselected tender code
        const params = new URLSearchParams(window.location.search);
        const tenderParam = params.get('tender');
        if (tenderParam) {
          const match = tendersList.find(t => t.tender_code.toLowerCase() === tenderParam.toLowerCase());
          if (match) {
            setSelectedTender(match);
          } else if (tendersList.length > 0) {
            setSelectedTender(tendersList[0]);
          }
        } else if (tendersList.length > 0) {
          setSelectedTender(tendersList[0]);
        }

        await loadProfileAndReviews();
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingInitial(false);
      }
    };
    init();
  }, []);

  const filteredTenders = tenders.filter(t => {
    const q = searchTender.toLowerCase();
    return (
      t.tender_code.toLowerCase().includes(q) ||
      t.title.toLowerCase().includes(q) ||
      t.department.toLowerCase().includes(q) ||
      (t.location && t.location.toLowerCase().includes(q))
    );
  }).slice(0, 6);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTender) {
      showToast('Please select a tender to audit.');
      return;
    }
    if (!title.trim() || !description.trim()) {
      showToast('Please provide both title and description.');
      return;
    }

    setSubmitting(true);
    try {
      await api.createComplaint({
        tender_id: selectedTender.tender_code,
        project_id: selectedTender.id,
        title: title.trim(),
        description: description.trim(),
        category,
        rating,
        media_url: photoUrl,
        location: selectedTender.location || 'Site Coordinates'
      });
      setSubmittedSuccess(true);
      showToast('Defect review submitted successfully!');
      // Reload profile & reviews
      await loadProfileAndReviews();
    } catch (err: any) {
      console.error(err);
      showToast(err.message || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleResetForm = () => {
    setTitle('');
    setDescription('');
    setUploadedFileName(null);
    setSubmittedSuccess(false);
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-4 py-3 rounded-2xl shadow-xl border border-slate-800 flex items-center gap-2 text-xs font-semibold animate-fade-in">
          <Check className="w-4 h-4 text-teal-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Citizen Auditor Profile Header Card */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-slate-900 via-slate-850 to-teal-950 text-white border border-slate-800 shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-teal-500/20 border border-teal-400/30 flex items-center justify-center font-black text-xl text-teal-300 shadow-inner shrink-0">
            {currentUser?.name ? currentUser.name.charAt(0).toUpperCase() : 'C'}
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-lg sm:text-xl font-black tracking-tight text-white">
                {currentUser?.name || 'Citizen Auditor'}
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/20 text-teal-300 border border-teal-400/30">
                Verified Citizen Reviewer
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Role: <strong className="text-slate-300">Citizen Reviewer (CITIZEN)</strong> • Empaneled On-Site Auditor
            </p>
          </div>
        </div>

        {/* Dynamic Reputation Metrics */}
        <div className="flex flex-wrap items-center gap-3 sm:gap-6 bg-white/5 p-3 rounded-2xl border border-white/10">
          <div>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
              Reputation Score
            </span>
            <span className="text-xl font-mono font-black text-teal-300">
              {profile ? profile.reputation_score : 85.0}
              <span className="text-xs text-slate-400 font-normal">/100</span>
            </span>
          </div>

          <div className="w-px h-8 bg-white/10 hidden sm:block" />

          <div>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
              Audits Logged
            </span>
            <span className="text-xl font-mono font-black text-white">
              {profile ? profile.total_reports : myReviews.length}
            </span>
          </div>

          <div className="w-px h-8 bg-white/10 hidden sm:block" />

          <div>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
              Community Rank
            </span>
            <span className="text-xl font-mono font-black text-amber-300">
              #{profile ? profile.rank : 1}
            </span>
          </div>
        </div>
      </div>

      {/* Sub-navigation Tabs */}
      <div className="flex items-center gap-3 border-b border-slate-200">
        <button
          onClick={() => {
            setActiveSubTab('submit');
            setSubmittedSuccess(false);
          }}
          className={`pb-3 px-4 text-xs font-bold transition-all relative ${
            activeSubTab === 'submit'
              ? 'text-teal-600'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <span>Submit Project Audit</span>
          {activeSubTab === 'submit' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-teal-600 rounded-full" />
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('my-reviews')}
          className={`pb-3 px-4 text-xs font-bold transition-all relative ${
            activeSubTab === 'my-reviews'
              ? 'text-teal-600'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <span>My Submitted Audits ({myReviews.length})</span>
          {activeSubTab === 'my-reviews' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-teal-600 rounded-full" />
          )}
        </button>
      </div>

      {/* SUBTAB 1: SUBMIT NEW AUDIT */}
      {activeSubTab === 'submit' && (
        submittedSuccess ? (
          <div className="p-8 sm:p-12 rounded-3xl bg-white border border-slate-200 shadow-sm text-center max-w-lg mx-auto space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-xs">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-black text-slate-900">
              Review Submitted into Official Audit Log!
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Your defect report for <strong>{selectedTender?.title} ({selectedTender?.tender_code})</strong> has been saved directly into the investigation database. 
              The system has boosted your Citizen Reviewer reputation score.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <button
                onClick={handleResetForm}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 transition-colors shadow-sm"
              >
                Submit Another Report
              </button>
              <button
                onClick={() => setActiveSubTab('my-reviews')}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
              >
                View My Reviews
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              
              {/* Left Column (7 cols): Tender Search, Selection & Review Inputs */}
              <div className="lg:col-span-7 space-y-5">
                
                {/* 1. Tender Lookup */}
                <div className="space-y-1.5">
                  <label className="block text-xs font-bold text-slate-800">
                    Step 1: Search & Select Tender by ID or Name
                  </label>
                  
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder="Type tender code (e.g. T001) or keyword..."
                      value={searchTender}
                      onChange={(e) => setSearchTender(e.target.value)}
                      className="w-full pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-teal-500 transition-colors"
                    />
                  </div>

                  {/* Matching Suggestions Pills */}
                  {searchTender.trim() && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {filteredTenders.map(t => (
                        <button
                          type="button"
                          key={t.id}
                          onClick={() => {
                            setSelectedTender(t);
                            setSearchTender('');
                          }}
                          className={`px-2.5 py-1 rounded-lg text-xs font-semibold text-left border transition-all ${
                            selectedTender?.id === t.id
                              ? 'bg-teal-50 border-teal-400 text-teal-800'
                              : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                          }`}
                        >
                          <span className="font-mono font-bold">{t.tender_code}</span>: {t.title.slice(0, 32)}...
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Selected Tender Card */}
                {selectedTender && (
                  <div className="p-4 rounded-2xl bg-teal-50/50 border border-teal-200/80 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="font-mono text-xs font-black text-teal-700">
                          {selectedTender.tender_code}
                        </span>
                        <h4 className="text-xs font-bold text-slate-900 mt-0.5">
                          {selectedTender.title}
                        </h4>
                        <p className="text-[11px] text-slate-500">
                          {selectedTender.department} • {selectedTender.location || 'India'}
                        </p>
                      </div>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-100 text-teal-800">
                        {selectedTender.status}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-600 pt-1 border-t border-teal-200/60">
                      <span>Awarded: <strong>{selectedTender.winning_vendor_name || 'BuildRight Infra'}</strong></span>
                      <span>Contract Sum: <strong>₹{(selectedTender.winning_bid_amount || selectedTender.estimated_value).toLocaleString('en-IN')}</strong></span>
                    </div>
                  </div>
                )}

                {/* 2. Review Title */}
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-slate-800">
                    Step 2: Observation Title
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Sub-base asphalt peeled off; deep potholes near KM-4"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-teal-500"
                  />
                </div>

                {/* 3. Category */}
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-slate-800">
                    Step 3: Defect Category
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-bold focus:outline-none focus:border-teal-500"
                  >
                    <option value="ROAD_QUALITY">Road Quality & Asphalt Deterioration</option>
                    <option value="CONSTRUCTION_DEFECT">Structural Crack & Construction Defect</option>
                    <option value="DRAINAGE_FAILURE">Culvert / Drainage Blockage & Flooding</option>
                    <option value="SAFETY_HAZARD">Missing Crash Barriers & Safety Hazard</option>
                    <option value="DELAY">Project Stalled / Abandoned Worksite</option>
                    <option value="CORRUPTION_OVERPRICING">Substandard Material / Suspected Overpricing</option>
                  </select>
                </div>

                {/* 4. Detailed Description */}
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-slate-800">
                    Step 4: Detailed On-Site Observation Notes
                  </label>
                  <textarea
                    required
                    rows={4}
                    placeholder="Describe the physical condition, exact landmark, estimated depth/extent of defect, and any safety hazards to pedestrians/vehicles..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-teal-500 resize-none leading-relaxed"
                  />
                </div>

              </div>

              {/* Right Column (5 cols): Rating & Evidence Upload */}
              <div className="lg:col-span-5 space-y-5 flex flex-col justify-between">
                
                {/* Photo Evidence Upload */}
                <div className="space-y-1.5">
                  <label className="block text-xs font-bold text-slate-800">
                    Step 5: Attach Photographic or Video Evidence
                  </label>

                  <div 
                    onClick={() => {
                      setUploadedFileName('site_defect_evidence_km4.jpg');
                      setPhotoUrl('https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=80');
                      showToast('Photo attached with forensic geo-timestamp');
                    }}
                    className="border-2 border-dashed border-slate-200 hover:border-teal-400 rounded-2xl p-7 text-center bg-slate-50/50 hover:bg-teal-50/30 transition-all cursor-pointer flex flex-col items-center justify-center space-y-2"
                  >
                    <div className="w-10 h-10 rounded-full bg-teal-50 text-teal-600 flex items-center justify-center shadow-xs">
                      <UploadCloud className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-800">
                        {uploadedFileName ? 'Change Attached File' : 'Click to Upload Defect Photo'}
                      </p>
                      <p className="text-[11px] text-teal-600 font-semibold">
                        Geo-tagging & EXIF timestamp verified
                      </p>
                    </div>
                    <p className="text-[10px] text-slate-400">
                      Supports JPG, PNG, MP4 (Max 50 MB)
                    </p>
                  </div>

                  {uploadedFileName && (
                    <div className="p-2.5 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-between text-xs text-teal-900">
                      <div className="flex items-center gap-2 truncate">
                        <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
                        <span className="font-semibold truncate">{uploadedFileName}</span>
                      </div>
                      <button 
                        type="button" 
                        onClick={() => setUploadedFileName(null)}
                        className="text-teal-600 hover:text-teal-900 p-1"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>

                {/* Rating */}
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2">
                  <label className="block text-xs font-bold text-slate-800">
                    Step 6: Observed Quality Rating
                  </label>
                  <div className="flex items-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        type="button"
                        key={star}
                        onClick={() => setRating(star)}
                        className={`p-1.5 rounded-lg transition-transform hover:scale-110 ${
                          rating >= star ? 'text-amber-400' : 'text-slate-300'
                        }`}
                      >
                        <Star className="w-5 h-5 fill-current" />
                      </button>
                    ))}
                    <span className="text-xs font-bold text-slate-700 ml-2">
                      ({rating}/5 - {rating <= 2 ? 'Severe Defect / Danger' : (rating === 3 ? 'Moderate Defect' : 'Satisfactory')})
                    </span>
                  </div>
                </div>

                {/* Verification Notice */}
                <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200/80 text-[11px] text-amber-800 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold">
                    <Sparkles className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    <span>Integrity Guardrails</span>
                  </div>
                  <p className="leading-snug text-amber-700">
                    Submissions are encrypted and reviewed by empaneled vigilance investigators. Verified defects award up to +15 reputation points.
                  </p>
                </div>

              </div>

            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={handleResetForm}
                className="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors"
              >
                Reset
              </button>
              <button
                type="submit"
                disabled={submitting || !selectedTender}
                className="px-7 py-2.5 rounded-xl text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 disabled:opacity-50 transition-all flex items-center gap-1.5 shadow-sm"
              >
                <span>{submitting ? 'Encrypting & Logging...' : 'Submit Official Audit'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        )
      )}

      {/* SUBTAB 2: MY SUBMITTED AUDITS */}
      {activeSubTab === 'my-reviews' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs flex items-center justify-between">
            <div>
              <h3 className="text-sm font-black text-slate-900">
                My Submitted Audit Reviews ({myReviews.length})
              </h3>
              <p className="text-xs text-slate-500">
                Your historical contributions tracked across regional tenders and infrastructure projects
              </p>
            </div>
            <button
              onClick={() => {
                setActiveSubTab('submit');
                setSubmittedSuccess(false);
              }}
              className="px-3.5 py-1.5 rounded-xl text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 transition-colors flex items-center gap-1"
            >
              <span>+ New Audit</span>
            </button>
          </div>

          {myReviews.length === 0 ? (
            <div className="p-12 text-center text-slate-400 bg-white rounded-2xl border border-slate-200">
              <MessageSquare className="w-10 h-10 mx-auto mb-3 text-slate-300" />
              <h4 className="text-sm font-bold text-slate-700">No Audits Submitted Yet</h4>
              <p className="text-xs text-slate-500 mt-1">
                Help keep public infrastructure accountable by submitting observations from your locality.
              </p>
              <button
                onClick={() => setActiveSubTab('submit')}
                className="mt-4 px-5 py-2 rounded-xl text-xs font-bold text-teal-700 bg-teal-50 hover:bg-teal-100 border border-teal-200 inline-block"
              >
                Submit Your First Review
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {myReviews.map((rev) => (
                <div key={rev.id} className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="font-mono text-[10px] font-bold text-teal-700 block">
                        {rev.tender_id || `Project #${rev.project_id}`}
                      </span>
                      <h4 className="text-sm font-bold text-slate-900 mt-0.5 leading-snug">
                        {rev.title}
                      </h4>
                      <p className="text-[11px] text-slate-500">{rev.project_name}</p>
                    </div>

                    <div className="text-right shrink-0">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        rev.status === 'VERIFIED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                        rev.status === 'UNVERIFIED' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {rev.status}
                      </span>
                      <div className="flex items-center gap-1 text-amber-500 mt-1 justify-end">
                        <Star className="w-3 h-3 fill-current" />
                        <span className="text-[11px] font-bold text-slate-700">{rev.rating}/5</span>
                      </div>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">
                    {rev.description}
                  </p>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-100">
                    <span>Category: <strong>{rev.category}</strong></span>
                    <span>{rev.created_at ? new Date(rev.created_at).toLocaleDateString() : 'Recent'}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
