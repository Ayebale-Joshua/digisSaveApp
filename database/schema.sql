PRAGMA foreign_keys = ON;

-- 1. CYCLES TABLE: Stores baseline configuration rules for each operational period
CREATE TABLE IF NOT EXISTS cycles (
    cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    target_duration_weeks INTEGER DEFAULT 52,
    meeting_frequency TEXT DEFAULT 'WEEKLY',
    share_value REAL NOT NULL,
    default_shares_per_week INTEGER DEFAULT 5,
    welfare_fixed_amount REAL NOT NULL,
    default_loan_duration_months INTEGER DEFAULT 3,
    default_interest_rate REAL DEFAULT 0.10,
    max_loan_multiplier REAL DEFAULT 3.0,
    welfare_loan_interest_rate REAL DEFAULT 0.10,
    welfare_loan_threshold REAL DEFAULT 20000.0,
    mid_cycle_joiner_rule TEXT DEFAULT 'ZERO_HISTORICAL_MODIFIED_PAYOUT',
    exit_rule TEXT DEFAULT 'SIT_AND_WAIT_NO_INTEREST',
    is_active INTEGER DEFAULT 1
);

-- 2. MEMBERS TABLE: Profiles, passbooks, and next-of-kin details (Supports soft-delete via STATUS = 'DELETED')
CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    passbook_number TEXT NOT NULL,
    national_id TEXT,
    full_name TEXT NOT NULL,
    phone_contact TEXT,
    status TEXT DEFAULT 'ACTIVE',                 -- 'ACTIVE', 'INACTIVE_SUSPENDED', 'EXITED', 'DELETED'
    joined_cycle_id INTEGER,
    next_of_kin_name TEXT NOT NULL,
    next_of_kin_relation TEXT NOT NULL,
    next_of_kin_phone TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (joined_cycle_id) REFERENCES cycles(cycle_id)
);

-- 3. MEETINGS TABLE: Represents each scheduled gathering with exact start timestamp tracking
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id INTEGER NOT NULL,
    meeting_number INTEGER NOT NULL,
    meeting_date TEXT NOT NULL,
    start_time TEXT DEFAULT CURRENT_TIMESTAMP,    -- Exact timestamp when meeting is started
    status TEXT DEFAULT 'IN_PROGRESS',            -- 'IN_PROGRESS', 'COMPLETED'
    total_cash_in REAL DEFAULT 0.0,
    total_cash_out REAL DEFAULT 0.0,
    FOREIGN KEY (cycle_id) REFERENCES cycles(cycle_id)
);

-- 4. LOANS TABLE: Manages loan disbursements, balances, and sources
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    cycle_id INTEGER NOT NULL,
    loan_source TEXT DEFAULT 'SAVINGS',           -- 'SAVINGS' or 'WELFARE'
    principal_amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    total_due REAL NOT NULL,
    remaining_balance REAL NOT NULL,
    duration_months INTEGER NOT NULL,
    disbursement_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE',                 -- 'ACTIVE', 'REPAID', 'INTEREST_RENEWED', 'DEFAULTED'
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (cycle_id) REFERENCES cycles(cycle_id)
);

-- 5. TRANSACTIONS TABLE: Core financial ledger for the 7-step meeting workflow
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,               -- 'ATTENDANCE', 'ATTENDANCE_FINE', 'SAVINGS_SHARE', 'WELFARE', 'LOAN_DISBURSEMENT', 'LOAN_REPAYMENT'
    fund_source TEXT DEFAULT 'SAVINGS',           -- 'SAVINGS', 'WELFARE', 'FINES'
    amount REAL NOT NULL,
    shares_count INTEGER DEFAULT 0,
    reference_id INTEGER,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- 6. AUDIT_LOGS TABLE: ACID compliance and post-commit error corrections/reversals
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_transaction_id INTEGER NOT NULL,
    meeting_id INTEGER NOT NULL,
    admin_user TEXT DEFAULT 'SYSTEM_ADMIN',
    action_type TEXT NOT NULL,
    adjustment_amount REAL NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
);