from database.db_manager import DatabaseManager

class MemberModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_member(self, data: dict) -> int:
        query = """
            INSERT INTO members (
                passbook_number, national_id, full_name, phone_contact,
                status, joined_cycle_id, next_of_kin_name,
                next_of_kin_relation, next_of_kin_phone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get("passbook_number"),
            data.get("national_id"),
            data.get("full_name"),
            data.get("phone_contact"),
            data.get("status", "ACTIVE"),
            data.get("joined_cycle_id"),
            data.get("next_of_kin_name"),
            data.get("next_of_kin_relation"),
            data.get("next_of_kin_phone")
        )
        return self.db.execute_query(query, params)

    def get_member_by_id(self, member_id: int) -> dict:
        query = "SELECT * FROM members WHERE member_id = ?;"
        return self.db.fetch_one(query, (member_id,))

    def get_member_by_passbook(self, passbook_number: str) -> dict:
        query = "SELECT * FROM members WHERE passbook_number = ? AND status != 'DELETED';"
        return self.db.fetch_one(query, (passbook_number,))

    def list_active_members(self, cycle_id: int = None) -> list:
        """Lists active members, excluding soft-deleted ones."""
        query = "SELECT * FROM members WHERE status != 'DELETED'"
        params = []
        if cycle_id:
            query += " AND joined_cycle_id = ?"
            params.append(cycle_id)
        query += " ORDER BY passbook_number ASC;"
        return self.db.fetch_all(query, tuple(params))

    def update_member(self, member_id: int, data: dict) -> int:
        query = """
            UPDATE members SET
                passbook_number = ?, national_id = ?, full_name = ?,
                phone_contact = ?, status = ?, next_of_kin_name = ?,
                next_of_kin_relation = ?, next_of_kin_phone = ?
            WHERE member_id = ?;
        """
        params = (
            data.get("passbook_number"),
            data.get("national_id"),
            data.get("full_name"),
            data.get("phone_contact"),
            data.get("status", "ACTIVE"),
            data.get("next_of_kin_name"),
            data.get("next_of_kin_relation"),
            data.get("next_of_kin_phone"),
            member_id
        )
        return self.db.execute_query(query, params)

    def soft_delete_member(self, member_id: int) -> int:
        """Soft-deletes a member, preserving records for foreign keys but hiding them from active lists."""
        query = "UPDATE members SET status = 'DELETED' WHERE member_id = ?;"
        return self.db.execute_query(query, (member_id,))