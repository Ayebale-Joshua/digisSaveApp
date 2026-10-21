from database.db_manager import DatabaseManager

class TransactionModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_meeting(self, cycle_id: int, meeting_number: int, meeting_date: str) -> int:
        """Initializes a new meeting session."""
        query = """
            INSERT INTO meetings (cycle_id, meeting_number, meeting_date, status)
            VALUES (?, ?, ?, 'IN_PROGRESS');
        """
        return self.db.execute_query(query, (cycle_id, meeting_number, meeting_date))

    def add_transaction(self, data: dict) -> int:
        """
        Records a financial transaction during a meeting workflow step 
        (Attendance Fine, Share Purchase, Welfare, Loan Repayment, etc.).
        """
        query = """
            INSERT INTO transactions (
                meeting_id, member_id, transaction_type, fund_source,
                amount, shares_count, reference_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            data.get("meeting_id"),
            data.get("member_id"),
            data.get("transaction_type"),    # e.g., 'ATTENDANCE_FINE', 'SAVINGS_SHARE', 'WELFARE', 'LOAN_REPAYMENT'
            data.get("fund_source", "SAVINGS"), # 'SAVINGS', 'WELFARE', 'FINES'
            data.get("amount"),
            data.get("shares_count", 0),
            data.get("reference_id")         # Links to loan_id if applicable
        )
        return self.db.execute_query(query, params)

    def get_meeting_transactions(self, meeting_id: int) -> list:
        """Retrieves all transactions recorded during a specific meeting."""
        query = """
            SELECT t.*, m.full_name, m.passbook_number
            FROM transactions t
            JOIN members m ON t.member_id = m.member_id
            WHERE t.meeting_id = ?
            ORDER BY t.transaction_id ASC;
        """
        return self.db.fetch_all(query, (meeting_id,))

    def get_meeting_cash_summary(self, meeting_id: int) -> dict:
        """
        Calculates total cash-in vs cash-out for the pre-commit cash box reconciliation screen.
        """
        query = """
            SELECT 
                SUM(CASE WHEN transaction_type IN ('SAVINGS_SHARE', 'WELFARE', 'ATTENDANCE_FINE', 'LOAN_REPAYMENT') THEN amount ELSE 0 END) as total_cash_in,
                SUM(CASE WHEN transaction_type = 'LOAN_DISBURSEMENT' THEN amount ELSE 0 END) as total_cash_out
            FROM transactions
            WHERE meeting_id = ?;
        """
        result = self.db.fetch_one(query, (meeting_id,))
        if not result or result["total_cash_in"] is None:
            return {"total_cash_in": 0.0, "total_cash_out": 0.0, "net_cash": 0.0}
        
        cash_in = result["total_cash_in"] or 0.0
        cash_out = result["total_cash_out"] or 0.0
        
        return {
            "total_cash_in": cash_in,
            "total_cash_out": cash_out,
            "net_cash": cash_in - cash_out
        }

    def commit_meeting(self, meeting_id: int) -> int:
        """Locks the meeting session as COMPLETED."""
        summary = self.get_meeting_cash_summary(meeting_id)
        query = """
            UPDATE meetings 
            SET status = 'COMPLETED', total_cash_in = ?, total_cash_out = ?
            WHERE meeting_id = ?;
        """
        return self.db.execute_query(query, (summary["total_cash_in"], summary["total_cash_out"], meeting_id))

    def create_audit_log(self, data: dict) -> int:
        """
        Records an ACID-compliant adjustment or reversal entry for post-commit corrections,
        preserving original transaction history without destructive deletes/updates.
        """
        query = """
            INSERT INTO audit_logs (
                original_transaction_id, meeting_id, admin_user,
                action_type, adjustment_amount, reason
            ) VALUES (?, ?, ?, ?, ?, ?);
        """
        params = (
            data.get("original_transaction_id"),
            data.get("meeting_id"),
            data.get("admin_user", "SYSTEM_ADMIN"),
            data.get("action_type", "REVERSAL_ENTRY"),
            data.get("adjustment_amount"),
            data.get("reason") # Mandatory explanation
        )
        return self.db.execute_query(query, (data.get("original_transaction_id"), data.get("meeting_id"), data.get("admin_user", "SYSTEM_ADMIN"), data.get("action_type", "REVERSAL_ENTRY"), data.get("adjustment_amount"), data.get("reason")))




    def get_cycle_financial_totals(self, cycle_id: int) -> dict:
        """Calculates total savings pool and welfare pool for an active cycle."""
        query = """
            SELECT 
                SUM(CASE WHEN transaction_type = 'SAVINGS_SHARE' THEN amount ELSE 0 END) as savings_pool,
                SUM(CASE WHEN transaction_type = 'WELFARE' THEN amount ELSE 0 END) as welfare_pool
            FROM transactions t
            JOIN meetings m ON t.meeting_id = m.meeting_id
            WHERE m.cycle_id = ?;
        """
        res = self.db.fetch_one(query, (cycle_id,))
        return {
            "savings_pool": res["savings_pool"] or 0.0 if res else 0.0,
            "welfare_pool": res["welfare_pool"] or 0.0 if res else 0.0
        }