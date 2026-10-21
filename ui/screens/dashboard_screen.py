from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from models.cycle_model import CycleModel
from models.transaction_model import TransactionModel
from models.loan_model import LoanModel
import os

kv_path = os.path.join(os.path.dirname(__file__), "../kv/dashboard.kv")
if os.path.exists(kv_path):
    Builder.load_file(kv_path)

class DashboardScreen(Screen):
    def on_enter(self):
        app = self.manager.app if hasattr(self.manager, 'app') else None
        if app:
            cycle_model = CycleModel(app.db)
            tx_model = TransactionModel(app.db)
            loan_model = LoanModel(app.db)

            active_cycle = cycle_model.get_active_cycle()
            if active_cycle:
                cid = active_cycle['cycle_id']
                self.ids.cycle_label.text = f"Active Cycle: {active_cycle['cycle_name']}"

                # Real-time metrics lookup
                totals = tx_model.get_cycle_financial_totals(cid)
                loans_total = loan_model.get_active_loans_total(cid)

                self.ids.savings_pool_label.text = f"UGX {totals['savings_pool']:,.2f}"
                self.ids.welfare_pool_label.text = f"UGX {totals['welfare_pool']:,.2f}"
                self.ids.active_loans_label.text = f"UGX {loans_total:,.2f}"
            else:
                self.ids.cycle_label.text = "No Active Cycle Found"
                self.ids.savings_pool_label.text = "UGX 0.00"
                self.ids.welfare_pool_label.text = "UGX 0.00"
                self.ids.active_loans_label.text = "UGX 0.00"