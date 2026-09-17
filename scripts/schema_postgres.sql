-- ==========================================================
-- ProcureShield AI — PostgreSQL Production Schema DDL
-- Multi-tier Procurement Integrity & Investigation Platform
-- ==========================================================

-- 1. Vendors
CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    vendor_id VARCHAR(50) UNIQUE NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100) UNIQUE NOT NULL,
    director_id VARCHAR(100),
    registered_address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(150),
    company_type VARCHAR(100),
    registration_date DATE,
    industry_category VARCHAR(100),
    win_rate FLOAT DEFAULT 0.0,
    total_contracts INT DEFAULT 0,
    total_contract_value FLOAT DEFAULT 0.0,
    risk_level VARCHAR(50) DEFAULT 'LOW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vendors_vendor_id ON vendors(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendors_director_id ON vendors(director_id);
CREATE INDEX IF NOT EXISTS idx_vendors_category ON vendors(industry_category);

-- 2. Tenders
CREATE TABLE IF NOT EXISTS tenders (
    id SERIAL PRIMARY KEY,
    tender_id VARCHAR(50) UNIQUE NOT NULL,
    buyer_id VARCHAR(50) NOT NULL,
    buyer_name VARCHAR(255) NOT NULL,
    tender_title TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(150),
    location VARCHAR(100),
    state VARCHAR(100),
    estimated_value_inr FLOAT NOT NULL,
    procurement_method VARCHAR(100) DEFAULT 'Open Competitive Bidding',
    award_criteria VARCHAR(100) DEFAULT 'Lowest Evaluated Responsive Bid (L1)',
    publication_date TIMESTAMP NOT NULL,
    submission_deadline TIMESTAMP NOT NULL,
    technical_evaluation_date DATE,
    financial_evaluation_date DATE,
    award_date DATE,
    contract_duration_days INT DEFAULT 180,
    status VARCHAR(50) DEFAULT 'AWARDED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tenders_tender_id ON tenders(tender_id);
CREATE INDEX IF NOT EXISTS idx_tenders_buyer_id ON tenders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_tenders_category ON tenders(category);
CREATE INDEX IF NOT EXISTS idx_tenders_dates ON tenders(publication_date, submission_deadline);

-- 3. Bids
CREATE TABLE IF NOT EXISTS bids (
    id SERIAL PRIMARY KEY,
    bid_id VARCHAR(50) UNIQUE NOT NULL,
    tender_id VARCHAR(50) NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    bid_amount_inr FLOAT NOT NULL,
    submission_timestamp TIMESTAMP NOT NULL,
    bid_status VARCHAR(50) DEFAULT 'QUALIFIED',
    disqualification_reason TEXT,
    technical_score FLOAT DEFAULT 85.0,
    financial_score FLOAT DEFAULT 85.0,
    is_winner BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bids_bid_id ON bids(bid_id);
CREATE INDEX IF NOT EXISTS idx_bids_tender_id ON bids(tender_id);
CREATE INDEX IF NOT EXISTS idx_bids_vendor_id ON bids(vendor_id);
CREATE INDEX IF NOT EXISTS idx_bids_winner ON bids(is_winner);

-- 4. Awards
CREATE TABLE IF NOT EXISTS awards (
    id SERIAL PRIMARY KEY,
    award_id VARCHAR(50) UNIQUE NOT NULL,
    tender_id VARCHAR(50) UNIQUE NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    winner_vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    awarded_amount_inr FLOAT NOT NULL,
    award_date DATE NOT NULL,
    award_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_awards_award_id ON awards(award_id);
CREATE INDEX IF NOT EXISTS idx_awards_tender_id ON awards(tender_id);
CREATE INDEX IF NOT EXISTS idx_awards_winner ON awards(winner_vendor_id);

-- 5. Contracts
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) UNIQUE NOT NULL,
    tender_id VARCHAR(50) UNIQUE NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    contract_value_inr FLOAT NOT NULL,
    start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_end_date DATE,
    planned_duration_days INT NOT NULL,
    actual_duration_days INT NOT NULL,
    completion_status VARCHAR(50) DEFAULT 'COMPLETED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contracts_contract_id ON contracts(contract_id);
CREATE INDEX IF NOT EXISTS idx_contracts_tender_id ON contracts(tender_id);
CREATE INDEX IF NOT EXISTS idx_contracts_vendor_id ON contracts(vendor_id);

-- 6. Vendor Relationships
CREATE TABLE IF NOT EXISTS vendor_relationships (
    id SERIAL PRIMARY KEY,
    relationship_id VARCHAR(50) UNIQUE NOT NULL,
    vendor_1 VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    vendor_2 VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    relationship_value VARCHAR(255) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_relationships_v1_v2 ON vendor_relationships(vendor_1, vendor_2);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON vendor_relationships(relationship_type);

-- 7. Vendor Together Participation
CREATE TABLE IF NOT EXISTS vendor_together_participation (
    id SERIAL PRIMARY KEY,
    vendor_1 VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    vendor_2 VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    together_tender_count INT NOT NULL,
    together_percentage FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vendor_pair UNIQUE (vendor_1, vendor_2)
);

CREATE INDEX IF NOT EXISTS idx_together_v1_v2 ON vendor_together_participation(vendor_1, vendor_2);
CREATE INDEX IF NOT EXISTS idx_together_count ON vendor_together_participation(together_tender_count DESC);

-- 8. Investigations
CREATE TABLE IF NOT EXISTS investigations (
    id SERIAL PRIMARY KEY,
    tender_id VARCHAR(50) UNIQUE NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    case_code VARCHAR(100) UNIQUE NOT NULL,
    priority_score FLOAT NOT NULL, -- 0 to 100
    priority_tier VARCHAR(50) NOT NULL, -- Low, Moderate, Elevated, High, Critical
    status VARCHAR(50) DEFAULT 'NEW', -- NEW, UNDER_REVIEW, EVIDENCE_GATHERING, ESCALATED, RESOLVED, DISMISSED
    signals_count INT DEFAULT 0,
    assigned_investigator VARCHAR(150),
    summary_narrative TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_investigations_tender_id ON investigations(tender_id);
CREATE INDEX IF NOT EXISTS idx_investigations_tier ON investigations(priority_tier);
CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status);

-- 9. Risk Signals (C1–C20)
CREATE TABLE IF NOT EXISTS risk_signals (
    id SERIAL PRIMARY KEY,
    tender_id VARCHAR(50) NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    investigation_id INT REFERENCES investigations(id) ON DELETE CASCADE,
    indicator_code VARCHAR(20) NOT NULL, -- C1 to C20
    indicator_name VARCHAR(150) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity FLOAT NOT NULL, -- 0.0 to 1.0
    confidence FLOAT NOT NULL, -- 0.0 to 1.0
    evidence_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_signals_tender_id ON risk_signals(tender_id);
CREATE INDEX IF NOT EXISTS idx_risk_signals_indicator ON risk_signals(indicator_code);

-- 10. Investigation Notes
CREATE TABLE IF NOT EXISTS investigation_notes (
    id SERIAL PRIMARY KEY,
    investigation_id INT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    author_name VARCHAR(150) NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_investigation_notes_inv_id ON investigation_notes(investigation_id);

-- 11. Benchmark Cases
CREATE TABLE IF NOT EXISTS benchmark_cases (
    id SERIAL PRIMARY KEY,
    tender_id VARCHAR(50) UNIQUE NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    expected_indicator_codes VARCHAR(255),
    scenario_type VARCHAR(255),
    benchmark_alert BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_benchmark_cases_tender_id ON benchmark_cases(tender_id);
