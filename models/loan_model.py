from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

class LoanModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def disburse_loan(self, data: dict) -> int:
        """
        Disburses a new loan from either 'SAVINGS' or 'WELFARE' pool.
        Calculates total due based on principal and interest rate.
        """
        principal = data.get("principal_amount")
        interest_rate = data.get("interest_rate")
        duration_months = data.get("duration_months", 3)
        
        # Calculate total due (Principal + Simple Interest for the term)
        total_interest = principal * interest_rate
        total_due = principal + total_interest
        
        # Calculate due date based on months (approx 30 days per month)
        disbursement_date = data.get("disbursement_date", datetime.now().strftime("%Y-%m-%d"))
        due_date_obj = datetime.strptime(disbursement_date, "%Y-%m-%d") + timedelta(days=int(duration_months * 30))
        due_date = due_date_obj.strftime("%Y-%m-%d")

        query = """
            INSERT INTO loans (
                member_id, cycle_id, loan_source, principal_amount,
                interest_rate, total_due, remaining_balance,
                duration_months, disbursement_date, due_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        """
        params = (
            data.get("member_id"),
            data.get("cycle_id"),
            data.get("loan_source", "SAVINGS"),  # 'SAVINGS' or 'WELFARE'
            principal,
            interest_rate,
            total_due,
            total_due,  # Initial remaining balance equals total due
            duration_months,
            disbursement_date,
            due_date
        )
        return self.db.execute_query(query, params)

    def get_loan_by_id(self, loan_id: int) -> dict:
        """Retrieves a loan record by its ID."""
        query = "SELECT * FROM loans WHERE loan_id = ?;"
        return self.db.fetch_one(query, (loan_id,))

    def list_loans(self, cycle_id: int = None, status: str = None) -> list:
        """Lists loans with optional filters for cycle and status."""
        query = """
            SELECT l.*, m.full_name, m.passbook_number 
            FROM loans l
            JOIN members m ON l.member_id = m.member_id
            WHERE 1=1
        """
        params = []
        if cycle_id:
            query += " AND l.cycle_id = ?"
            params.append(cycle_id)
        if status:
            query += " AND l.status = ?"
            params.append(status)
            
        query += " ORDER BY l.disbursement_date DESC;"
        return self.db.fetch_all(query, tuple(params))

    def update_loan_balance_after_payment(self, loan_id: int, payment_amount: float) -> dict:
        """
        Updates a loan's remaining balance after a partial or full payment.
        If remaining balance reaches <= 0, marks the loan as 'REPAID'.
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("Loan not found.")

        new_balance = max(0.0, loan["remaining_balance"] - payment_amount)
        new_status = "REPAID" if new_balance == 0 else loan["status"]

        query = """
            UPDATE loans 
            SET remaining_balance = ?, status = ?
            WHERE loan_id = ?;
        """
        self.db.execute_query(query, (new_balance, new_status, loan_id))
        return {"remaining_balance": new_balance, "status": new_status}

    def process_interest_only_renewal(self, loan_id: int, extension_months: int = 3) -> int:
        """
        Allows a member to pay interest only to avoid principal rollover penalties,
        extending the due date for another term.
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("Loan not found.")

        current_due_date = datetime.strptime(loan["due_date"], "%Y-%m-%d")
        new_due_date_obj = current_due_date + timedelta(days=int(extension_months * 30))
        new_due_date = new_due_date_obj.strftime("%Y-%m-%d")

        query = """
            UPDATE loans 
            SET due_date = ?, status = 'INTEREST_RENEWED'
            WHERE loan_id = ?;
        """
        return self.db.execute_query(query, (new_due_date, loan_id))


    def get_active_loans_total(self, cycle_id: int) -> float:
        """Calculates the total remaining loan balance across all active loans in a cycle."""
        query = "SELECT SUM(remaining_balance) as total_outstanding FROM loans WHERE cycle_id = ? AND status = 'ACTIVE';"
        res = self.db.fetch_one(query, (cycle_id,))
        return res["total_outstanding"] or 0.0 if res else 0.0