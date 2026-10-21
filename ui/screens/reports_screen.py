from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from utils.pdf_generator import PDFGenerator
from utils.excel_generator import ExcelGenerator
from models.transaction_model import TransactionModel
import os

kv_path = os.path.join(os.path.dirname(__file__), "../kv/reports.kv")
if os.path.exists(kv_path):
    Builder.load_file(kv_path)

class ReportsScreen(Screen):
    def on_enter(self):
        app = self.manager.app if hasattr(self.manager, 'app') else None
        if app:
            self.tx_model = TransactionModel(app.db)

    def export_pdf(self):
        # Fetch mock meeting #1 details & transactions
        transactions = self.tx_model.get_meeting_transactions(1)
        cash_summary = self.tx_model.get_meeting_cash_summary(1)
        meeting_data = {
            "meeting_number": 1,
            "meeting_date": "2026-10-18",
            "total_cash_in": cash_summary["total_cash_in"],
            "total_cash_out": cash_summary["total_cash_out"]
        }

        output_path = os.path.abspath("Meeting_Summary_Report.pdf")
        PDFGenerator.generate_meeting_summary_pdf(meeting_data, transactions, output_path)
        self.ids.status_label.text = f"PDF Generated successfully: {output_path}"

    def export_excel(self):
        transactions = self.tx_model.get_meeting_transactions(1)
        meeting_data = {"meeting_number": 1, "meeting_date": "2026-10-18"}

        output_path = os.path.abspath("Meeting_Summary_Report.xlsx")
        ExcelGenerator.export_meeting_ledger_to_excel(meeting_data, transactions, output_path)
        self.ids.status_label.text = f"Excel Generated successfully: {output_path}"