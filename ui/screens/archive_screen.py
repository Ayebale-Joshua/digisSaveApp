from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from models.cycle_model import CycleModel
import os

kv_path = os.path.join(os.path.dirname(__file__), "../kv/archive.kv")
if os.path.exists(kv_path):
    Builder.load_file(kv_path)

class ArchiveScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_cycle_id = None

    def on_enter(self):
        app = self.manager.app if hasattr(self.manager, 'app') else None
        if app:
            self.db = app.db
            self.cycle_model = CycleModel(self.db)
            self.load_cycles_list()

    def load_cycles_list(self):
        container = self.ids.cycles_list_container
        container.clear_widgets()

        cycles = self.cycle_model.list_all_cycles()
        for c in cycles:
            btn = Button(
                text=f"{c['cycle_name']} ({c['start_date']})",
                size_hint_y=None,
                height='45dp',
                background_color=(0.17, 0.42, 0.69, 1),
                background_normal=''
            )
            btn.bind(on_release=lambda instance, cid=c['cycle_id'], cname=c['cycle_name']: self.select_cycle(cid, cname))
            container.add_widget(btn)

    def select_cycle(self, cycle_id, cycle_name):
        self.selected_cycle_id = cycle_id
        self.ids.drilldown_title_label.text = f"Cycle: {cycle_name} - Records"
        self.show_drilldown('members')

    def show_drilldown(self, category):
        if not self.selected_cycle_id:
            return

        container = self.ids.drilldown_content_container
        container.clear_widgets()

        # Structured Table Header
        header = BoxLayout(size_hint_y=None, height='30dp', spacing=5, padding=[5, 0])
        if category == 'members':
            header.add_widget(Label(text="Passbook", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.25, halign='left'))
            header.add_widget(Label(text="Full Name", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.50, halign='left'))
            header.add_widget(Label(text="Phone", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.25, halign='left'))
        elif category == 'savings':
            header.add_widget(Label(text="Passbook", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.25, halign='left'))
            header.add_widget(Label(text="Full Name", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.45, halign='left'))
            header.add_widget(Label(text="Total Saved", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.30, halign='right'))
        elif category == 'loans':
            header.add_widget(Label(text="Passbook", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.20, halign='left'))
            header.add_widget(Label(text="Full Name", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.40, halign='left'))
            header.add_widget(Label(text="Due Amount", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.25, halign='right'))
            header.add_widget(Label(text="Status", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.15, halign='center'))
        container.add_widget(header)

        # Data Rows
        if category == 'members':
            records = self.db.fetch_all("SELECT passbook_number, full_name, phone_contact FROM members WHERE joined_cycle_id = ? AND status != 'DELETED'", (self.selected_cycle_id,))
            for r in records:
                row = BoxLayout(size_hint_y=None, height='35dp', spacing=5, padding=[5, 0])
                row.add_widget(Label(text=str(r['passbook_number']), size_hint_x=0.25, color=(0.2, 0.2, 0.2, 1), halign='left', bold=True))
                row.add_widget(Label(text=r['full_name'], size_hint_x=0.50, color=(0.2, 0.2, 0.2, 1), halign='left'))
                row.add_widget(Label(text=r['phone_contact'] or 'N/A', size_hint_x=0.25, color=(0.4, 0.4, 0.4, 1), halign='left'))
                container.add_widget(row)
        elif category == 'savings':
            records = self.db.fetch_all("""
                SELECT m.passbook_number, m.full_name, SUM(t.amount) as total_saved 
                FROM transactions t
                JOIN members m ON t.member_id = m.member_id
                JOIN meetings mt ON t.meeting_id = mt.meeting_id
                WHERE mt.cycle_id = ? AND t.transaction_type = 'SAVINGS_SHARE'
                GROUP BY m.member_id
            """, (self.selected_cycle_id,))
            for r in records:
                row = BoxLayout(size_hint_y=None, height='35dp', spacing=5, padding=[5, 0])
                row.add_widget(Label(text=str(r['passbook_number']), size_hint_x=0.25, color=(0.2, 0.2, 0.2, 1), halign='left', bold=True))
                row.add_widget(Label(text=r['full_name'], size_hint_x=0.45, color=(0.2, 0.2, 0.2, 1), halign='left'))
                row.add_widget(Label(text=f"UGX {r['total_saved']:,.2f}", size_hint_x=0.30, color=(0.17, 0.56, 0.30, 1), halign='right', bold=True))
                container.add_widget(row)
        elif category == 'loans':
            records = self.db.fetch_all("""
                SELECT m.passbook_number, m.full_name, l.remaining_balance, l.status 
                FROM loans l
                JOIN members m ON l.member_id = m.member_id
                WHERE l.cycle_id = ?
            """, (self.selected_cycle_id,))
            for r in records:
                row = BoxLayout(size_hint_y=None, height='35dp', spacing=5, padding=[5, 0])
                row.add_widget(Label(text=str(r['passbook_number']), size_hint_x=0.20, color=(0.2, 0.2, 0.2, 1), halign='left', bold=True))
                row.add_widget(Label(text=r['full_name'], size_hint_x=0.40, color=(0.2, 0.2, 0.2, 1), halign='left'))
                row.add_widget(Label(text=f"UGX {r['remaining_balance']:,.2f}", size_hint_x=0.25, color=(0.85, 0.30, 0.20, 1), halign='right', bold=True))
                row.add_widget(Label(text=r['status'], size_hint_x=0.15, color=(0.4, 0.4, 0.4, 1), halign='center'))
                container.add_widget(row)