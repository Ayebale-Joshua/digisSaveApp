from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from models.cycle_model import CycleModel
import os

kv_path = os.path.join(os.path.dirname(__file__), "../kv/new_cycle.kv")
if os.path.exists(kv_path):
    Builder.load_file(kv_path)

class NewCycleScreen(Screen):
    def create_cycle(self):
        app = self.manager.app if hasattr(self.manager, 'app') else None
        if not app:
            return

        try:
            share_val = float(self.ids.txt_share_value.text.strip())
            welfare_val = float(self.ids.txt_welfare_amount.text.strip())
        except ValueError:
            return

        cycle_data = {
            "cycle_name": self.ids.txt_cycle_name.text.strip(),
            "start_date": self.ids.txt_start_date.text.strip(),
            "share_value": share_val,
            "welfare_fixed_amount": welfare_val,
            "is_active": 1
        }

        cycle_model = CycleModel(app.db)
        cycle_model.create_cycle_with_rollover(cycle_data)
        
        # Return to dashboard
        self.manager.current = 'dashboard'