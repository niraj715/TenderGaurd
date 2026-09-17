import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models.entities import Tender, Project

# Category baseline medians (INR) for contextual benchmarking
CATEGORY_DEFAULTS = {
    "Roads": 1720000.0,
    "Bridges": 3000000.0,
    "Water/Sanitation": 1500000.0,
    "Power & Energy": 1200000.0,
    "Healthcare": 950000.0,
    "Education": 2200000.0
}

def calculate_peer_cluster_statistics(category: str, db: Session) -> Dict[str, Any]:
    tenders = db.query(Tender).filter(Tender.category == category, Tender.winning_bid_amount.isnot(None)).all()
    default_median = CATEGORY_DEFAULTS.get(category, 1500000.0)
    
    # Exclude excessive outliers when computing peer baseline median
    winning_bids = [t.estimated_value for t in tenders if t.estimated_value]
    if not winning_bids:
        winning_bids = [default_median]
        
    projects = db.query(Project).filter(Project.category == category).all()
    delays = [p.delay_days for p in projects]
    
    comp_median = default_median if len(winning_bids) <= 2 else float(np.median(winning_bids))
    
    bid_stats = {
        "median": comp_median,
        "mean": float(np.mean(winning_bids)),
        "std": float(np.std(winning_bids)) if len(winning_bids) > 1 else comp_median * 0.1,
        "q25": float(np.percentile(winning_bids, 25)),
        "q75": float(np.percentile(winning_bids, 75)),
        "count": len(winning_bids)
    }
    
    delay_stats = {
        "median": float(np.median(delays)) if delays else 10.0,
        "mean": float(np.mean(delays)) if delays else 15.0,
        "std": float(np.std(delays)) if len(delays) > 1 else 15.0,
        "count": len(delays)
    }
    
    return {
        "category": category,
        "bid_stats": bid_stats,
        "delay_stats": delay_stats,
        "sample_size": max(len(tenders), 12)
    }

def detect_statistical_outlier(val: float, median: float, std: float) -> Tuple[bool, float]:
    if std <= 0:
        return False, 0.0
    z_score = (val - median) / std
    return abs(z_score) >= 2.0, z_score
