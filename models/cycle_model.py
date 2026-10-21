from database.db_manager import DatabaseManager

class CycleModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_cycle_with_rollover(self, cycle_data: dict) -> int:
        """
        Creates a new cycle, deactivates the old one, and rolls over active members 
        from the previous cycle (preserving passbooks, names, and next of kin).
        """
        # 1. Get current active cycle before deactivating
        old_active = self.get_active_cycle()
        
        # 2. Deactivate existing active cycles
        self.db.execute_query("UPDATE cycles SET is_active = 0 WHERE is_active = 1")

        # 3. Insert new cycle
        query = """
            INSERT INTO cycles (
                cycle_name, start_date, target_duration_weeks, meeting_frequency,
                share_value, default_shares_per_week, welfare_fixed_amount,
                default_loan_duration_months, default_interest_rate, max_loan_multiplier,
                welfare_loan_interest_rate, welfare_loan_threshold,
                mid_cycle_joiner_rule, exit_rule, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """
        params = (
            cycle_data.get("cycle_name"),
            cycle_data.get("start_date"),
            cycle_data.get("target_duration_weeks", 52),
            cycle_data.get("meeting_frequency", "WEEKLY"),
            cycle_data.get("share_value"),
            cycle_data.get("default_shares_per_week", 5),
            cycle_data.get("welfare_fixed_amount"),
            cycle_data.get("default_loan_duration_months", 3),
            cycle_data.get("default_interest_rate", 0.10),
            cycle_data.get("max_loan_multiplier", 3.0),
            cycle_data.get("welfare_loan_interest_rate", 0.10),
            cycle_data.get("welfare_loan_threshold", 20000.0),
            cycle_data.get("mid_cycle_joiner_rule", "ZERO_HISTORICAL_MODIFIED_PAYOUT"),
            cycle_data.get("exit_rule", "SIT_AND_WAIT_NO_INTEREST")
        )
        new_cycle_id = self.db.execute_query(query, params)

        # 4. Roll over active members from the previous cycle (or all active members if no prior cycle)
        if old_active:
            old_members = self.db.fetch_all(
                "SELECT * FROM members WHERE joined_cycle_id = ? AND status != 'DELETED'", 
                (old_active['cycle_id'],)
            )
        else:
            old_members = self.db.fetch_all("SELECT * FROM members WHERE status != 'DELETED'")

        for m in old_members:
            rollover_query = """
                INSERT INTO members (
                    passbook_number, national_id, full_name, phone_contact,
                    status, joined_cycle_id, next_of_kin_name,
                    next_of_kin_relation, next_of_kin_phone
                ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?)
            """
            self.db.execute_query(rollover_query, (
                m['passbook_number'], m['national_id'], m['full_name'], m['phone_contact'],
                new_cycle_id, m['next_of_kin_name'], m['next_of_kin_relation'], m['next_of_kin_phone']
            ))

        return new_cycle_id

    def get_active_cycle(self) -> dict:
        query = "SELECT * FROM cycles WHERE is_active = 1 LIMIT 1;"
        return self.db.fetch_one(query)

    def list_all_cycles(self) -> list:
        query = "SELECT * FROM cycles ORDER BY start_date DESC;"
        return self.db.fetch_all(query)