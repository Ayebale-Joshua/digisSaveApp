from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from models.transaction_model import TransactionModel
from models.member_model import MemberModel
from models.cycle_model import CycleModel
from models.loan_model import LoanModel
import os

kv_path = os.path.join(os.path.dirname(__file__), "../kv/meeting.kv")
if os.path.exists(kv_path):
    Builder.load_file(kv_path)

class MeetingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_step = 1
        self.meeting_id = None
        self.active_cycle = None

    def on_enter(self):
        app = self.manager.app if hasattr(self.manager, 'app') else None
        if app:
            self.db = app.db
            self.tx_model = TransactionModel(self.db)
            self.member_model = MemberModel(self.db)
            self.cycle_model = CycleModel(self.db)
            self.loan_model = LoanModel(self.db)
            
            self.active_cycle = self.cycle_model.get_active_cycle()
            if self.active_cycle:
                meetings = self.db.fetch_all(
                    "SELECT * FROM meetings WHERE cycle_id = ? AND status = 'IN_PROGRESS'", 
                    (self.active_cycle['cycle_id'],)
                )
                if meetings:
                    self.meeting_id = meetings[0]['meeting_id']
                else:
                    self.meeting_id = self.tx_model.create_meeting(
                        self.active_cycle['cycle_id'], 1, datetime.now().strftime("%Y-%m-%d")
                    )
            self.switch_step(1)

    def switch_step(self, step_num):
        self.current_step = step_num
        
        # Highlight active tab
        for i in range(1, 8):
            btn = self.ids.get(f"step{i}_btn")
            if btn:
                if i == step_num:
                    btn.background_color = (0.17, 0.42, 0.69, 1)
                else:
                    btn.background_color = (0.3, 0.35, 0.4, 1)

        container = self.ids.step_content_container
        container.clear_widgets()

        if step_num == 1:
            self.build_attendance_step(container)
        elif step_num == 2:
            self.build_fines_step(container)
        elif step_num == 3:
            self.build_savings_step(container)
        elif step_num == 4:
            self.build_welfare_step(container)
        elif step_num == 5:
            self.build_loans_out_step(container)
        elif step_num == 6:
            self.build_repayments_step(container)
        elif step_num == 7:
            self.build_summary_step(container)

    def build_attendance_step(self, container):
        container.add_widget(Label(text="Step 1: Meeting Attendance & Start Time", font_size='16sp', bold=True, size_hint_y=None, height='35dp', color=(0.1, 0.2, 0.3, 1)))
        
        meeting = self.db.fetch_one("SELECT * FROM meetings WHERE meeting_id = ?", (self.meeting_id,))
        start_time = meeting['start_time'] if meeting else 'Unknown'
        container.add_widget(Label(text=f"Meeting Started At: {start_time} | Status: IN_PROGRESS", font_size='14sp', size_hint_y=None, height='30dp', color=(0.2, 0.5, 0.2, 1)))

        scroll = ScrollView()
        list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_box.bind(minimum_height=list_box.setter('height'))
        
        members = self.member_model.list_active_members(self.active_cycle['cycle_id'] if self.active_cycle else None)
        for m in members:
            row = BoxLayout(size_hint_y=None, height='35dp', spacing=10)
            row.add_widget(Label(text=f"PB: {m['passbook_number']} - {m['full_name']}", color=(0.2, 0.2, 0.2, 1)))
            
            chk_btn = Button(text="Mark Present", size_hint_x=None, width='120dp', background_color=(0.25, 0.35, 0.45, 1), background_normal='')
            def mark_att(instance, mid=m['member_id']):
                self.tx_model.add_transaction({
                    "meeting_id": self.meeting_id,
                    "member_id": mid,
                    "transaction_type": "ATTENDANCE",
                    "fund_source": "FINES",
                    "amount": 0.0,
                    "shares_count": 0
                })
                instance.text = "Present ✓"
                instance.disabled = True
            chk_btn.bind(on_release=mark_att)
            row.add_widget(chk_btn)
            list_box.add_widget(row)
            
        scroll.add_widget(list_box)
        container.add_widget(scroll)

    def build_fines_step(self, container):
        container.add_widget(Label(text="Step 2: Attendance Fines & Penalties", font_size='16sp', bold=True, size_hint_y=None, height='35dp', color=(0.1, 0.2, 0.3, 1)))
        self._build_member_input_list(container, "ATTENDANCE_FINE", "FINES")

    def build_savings_step(self, container):
        share_val = self.active_cycle['share_value'] if self.active_cycle else 2000
        container.add_widget(Label(
            text=f"Step 3: Savings / Share Purchases (1 Share = UGX {share_val:,.0f})", 
            font_size='16sp', bold=True, size_hint_y=None, height='35dp', color=(0.1, 0.2, 0.3, 1)
        ))

        # Structured Table Header
        header = BoxLayout(size_hint_y=None, height='30dp', spacing=5, padding=[5, 0])
        header.add_widget(Label(text="Member Passbook & Name", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.35, halign='left'))
        header.add_widget(Label(text="Select Shares (1 - 5)", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.45, halign='center'))
        header.add_widget(Label(text="Action", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.20, halign='center'))
        container.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=[5, 5])
        list_box.bind(minimum_height=list_box.setter('height'))

        members = self.member_model.list_active_members(self.active_cycle['cycle_id'] if self.active_cycle else None)

        for m in members:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp', spacing=5)
            
            row.add_widget(Label(
                text=f"PB: {m['passbook_number']} - {m['full_name']}", 
                size_hint_x=0.35, color=(0.2, 0.2, 0.2, 1), halign='left', valign='middle'
            ))

            # 5-Share Button Group Container
            share_btn_box = BoxLayout(orientation='horizontal', spacing=4, size_hint_x=0.45)
            selected_shares = {'count': 0}
            btns = []

            def make_select_handler(count, current_btns, state_dict):
                def select_share(instance):
                    state_dict['count'] = count
                    for idx, b in enumerate(current_btns):
                        if idx < count:
                            b.background_color = (0.25, 0.35, 0.45, 1) # Highlight active green
                        else:
                            b.background_color = (0.7, 0.7, 0.7, 1)    # Default inactive gray
                return select_share

            for i in range(1, 6):
                btn_amt = i * share_val
                b = Button(
                    text=f"{i}x\n({int(btn_amt/1000)}k)", 
                    font_size='10sp', 
                    background_color=(0.7, 0.7, 0.7, 1), 
                    background_normal=''
                )
                btns.append(b)
                share_btn_box.add_widget(b)

            for i, b in enumerate(btns):
                b.bind(on_release=make_select_handler(i + 1, btns, selected_shares))

            row.add_widget(share_btn_box)

            # Confirm Purchase Button
            confirm_btn = Button(
                text="Confirm", 
                size_hint_x=0.20, 
                background_color=(0.25, 0.35, 0.45, 1), 
                background_normal=''
            )
            def save_shares(instance, mid=m['member_id'], state_dict=selected_shares, current_row_btns=btns):
                cnt = state_dict['count']
                if cnt > 0:
                    amt = cnt * share_val
                    self.tx_model.add_transaction({
                        "meeting_id": self.meeting_id,
                        "member_id": mid,
                        "transaction_type": "SAVINGS_SHARE",
                        "fund_source": "SAVINGS",
                        "amount": amt,
                        "shares_count": cnt
                    })
                    instance.text = f"Saved ({cnt}x) ✓"
                    instance.disabled = True
                    for b in current_row_btns:
                        b.disabled = True

            confirm_btn.bind(on_release=save_shares)
            row.add_widget(confirm_btn)
            list_box.add_widget(row)

        scroll.add_widget(list_box)
        container.add_widget(scroll)

    def build_welfare_step(self, container):
        welfare_val = self.active_cycle['welfare_fixed_amount'] if self.active_cycle else 5000
        container.add_widget(Label(text=f"Step 4: Welfare / Social Fund (Fixed: UGX {welfare_val:,.0f})", font_size='16sp', bold=True, size_hint_y=None, height='35dp', color=(0.1, 0.2, 0.3, 1)))
        
        scroll = ScrollView()
        list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_box.bind(minimum_height=list_box.setter('height'))
        
        members = self.member_model.list_active_members(self.active_cycle['cycle_id'] if self.active_cycle else None)
        
        for m in members:
            row = BoxLayout(size_hint_y=None, height='35dp', spacing=10)
            row.add_widget(Label(text=f"PB: {m['passbook_number']} - {m['full_name']}", color=(0.2, 0.2, 0.2, 1)))
            
            btn = Button(text=f"Pay UGX {welfare_val:,.0f}", size_hint_x=None, width='150dp', background_color=(0.25, 0.35, 0.45, 1), background_normal='')
            def pay_welfare(instance, mid=m['member_id']):
                self.tx_model.add_transaction({
                    "meeting_id": self.meeting_id,
                    "member_id": mid,
                    "transaction_type": "WELFARE",
                    "fund_source": "WELFARE",
                    "amount": welfare_val,
                    "shares_count": 0
                })
                instance.text = "Paid ✓"
                instance.disabled = True
            btn.bind(on_release=pay_welfare)
            row.add_widget(btn)
            list_box.add_widget(row)
            
        scroll.add_widget(list_box)
        container.add_widget(scroll)

    def build_loans_out_step(self, container):
        container.add_widget(Label(text="Step 5: Loan Disbursements & Eligibility Check", font_size='16sp', bold=True, size_hint_y=None, height='35dp', color=(0.1, 0.2, 0.3, 1)))
        
        form = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height='180dp')
        passbook_input = TextInput(hint_text="Member Passbook Number", multiline=False, size_hint_y=None, height='40dp')
        amount_input = TextInput(hint_text="Requested Loan Amount (UGX)", multiline=False, size_hint_y=None, height='40dp')
        
        status_lbl = Label(text="", font_size='14sp', color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height='30dp')
        
        btn = Button(text="Check Eligibility & Disburse Loan", size_hint_y=None, height='45dp', background_color=(0.17, 0.42, 0.69, 1), background_normal='')
        
        def process_loan(instance):
            pb = passbook_input.text.strip()
            try:
                amt = float(amount_input.text.strip())
            except ValueError:
                status_lbl.text = "Invalid loan amount."
                return
            
            member = self.member_model.get_member_by_passbook(pb)
            if not member:
                status_lbl.text = "Member not found."
                return
            
            savings_res = self.db.fetch_one("""
                SELECT SUM(amount) as total FROM transactions 
                WHERE member_id = ? AND transaction_type = 'SAVINGS_SHARE'
            """, (member['member_id'],))
            total_savings = savings_res['total'] if savings_res and savings_res['total'] else 0.0
            max_allowed = total_savings * (self.active_cycle['max_loan_multiplier'] if self.active_cycle else 3.0)
            
            if amt > max_allowed and max_allowed > 0:
                status_lbl.text = f"ELIGIBILITY FAILED: Max loan allowed is UGX {max_allowed:,.2f} (3x savings)."
                return
            
            self.loan_model.disburse_loan({
                "member_id": member['member_id'],
                "cycle_id": self.active_cycle['cycle_id'],
                "loan_source": "SAVINGS",
                "principal_amount": amt,
                "interest_rate": self.active_cycle.get('default_interest_rate', 0.10),
                "duration_months": self.active_cycle.get('default_loan_duration_months', 3)
            })
            status_lbl.color = (0.2, 0.6, 0.2, 1)
            status_lbl.text = "SUCCESS: Loan eligibility verified and disbursed!"
            passbook_input.text = ""
            amount_input.text = ""
            
        btn.bind(on_release=process_loan)
        form.add_widget(passbook_input)
        form.add_widget(amount_input)
        form.add_widget(btn)
        form.add_widget(status_lbl)
        container.add_widget(form)

    def build_repayments_step(self, container):
        container.add_widget(Label(text="Step 6: Loan Repayments", font_size='16sp', bold=True, size_hint_y=None, height='35dp', color=(0.1, 0.2, 0.3, 1)))
        
        # Table Header
        header = BoxLayout(size_hint_y=None, height='30dp', spacing=5, padding=[5, 0])
        header.add_widget(Label(text="Member Passbook & Name", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.45, halign='left'))
        header.add_widget(Label(text="Remaining Due", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.25, halign='right'))
        header.add_widget(Label(text="Payment Amount & Action", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.30, halign='center'))
        container.add_widget(header)

        scroll = ScrollView()
        list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_box.bind(minimum_height=list_box.setter('height'))
        
        loans = self.loan_model.list_loans(cycle_id=self.active_cycle['cycle_id'] if self.active_cycle else None, status='ACTIVE')
        for l in loans:
            row = BoxLayout(size_hint_y=None, height='45dp', spacing=5, padding=[5, 0])
            row.add_widget(Label(text=f"PB: {l['passbook_number']} - {l['full_name']}", size_hint_x=0.45, color=(0.2, 0.2, 0.2, 1), halign='left'))
            row.add_widget(Label(text=f"UGX {l['remaining_balance']:,.2f}", size_hint_x=0.25, color=(0.85, 0.30, 0.20, 1), halign='right', bold=True))
            
            action_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_x=0.30)
            pay_input = TextInput(hint_text="Amount", multiline=False)
            pay_btn = Button(text="Pay", background_color=(0.17, 0.56, 0.3, 1), background_normal='')
            
            def make_repayment(instance, lid=l['loan_id'], mid=l['member_id'], p_input=pay_input):
                try:
                    p_amt = float(p_input.text.strip())
                    self.loan_model.update_loan_balance_after_payment(lid, p_amt)
                    self.tx_model.add_transaction({
                        "meeting_id": self.meeting_id,
                        "member_id": mid,
                        "transaction_type": "LOAN_REPAYMENT",
                        "fund_source": "SAVINGS",
                        "amount": p_amt,
                        "reference_id": lid
                    })
                    p_input.text = "Paid ✓"
                    p_input.disabled = True
                except ValueError:
                    pass
            pay_btn.bind(on_release=make_repayment)
            
            action_box.add_widget(pay_input)
            action_box.add_widget(pay_btn)
            row.add_widget(action_box)
            list_box.add_widget(row)
            
        scroll.add_widget(list_box)
        container.add_widget(scroll)

    def build_summary_step(self, container):
        container.add_widget(Label(text="Step 7: Pre-Commit Cash Box Reconciliation & Ledger", font_size='16sp', bold=True, size_hint_y=None, height='35dp', color=(0.1, 0.2, 0.3, 1)))
        
        summary = self.tx_model.get_meeting_cash_summary(self.meeting_id)
        summary_text = (
            f"Total Cash-In: UGX {summary['total_cash_in']:,.2f} | "
            f"Total Cash-Out: UGX {summary['total_cash_out']:,.2f} | "
            f"Net Cash Box: UGX {summary['net_cash']:,.2f}"
        )
        container.add_widget(Label(text=summary_text, font_size='14sp', bold=True, size_hint_y=None, height='30dp', color=(0.1, 0.2, 0.3, 1)))

        # Table Header
        header = BoxLayout(size_hint_y=None, height='30dp', spacing=5, padding=[5, 0])
        header.add_widget(Label(text="Passbook & Name", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.40, halign='left'))
        header.add_widget(Label(text="Transaction Type", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.35, halign='left'))
        header.add_widget(Label(text="Amount", bold=True, color=(0.1, 0.2, 0.35, 1), size_hint_x=0.25, halign='right'))
        container.add_widget(header)

        scroll = ScrollView()
        list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_box.bind(minimum_height=list_box.setter('height'))
        
        txs = self.tx_model.get_meeting_transactions(self.meeting_id)
        for t in txs:
            row = BoxLayout(size_hint_y=None, height='35dp', spacing=5, padding=[5, 0])
            row.add_widget(Label(text=f"PB: {t['passbook_number']} - {t['full_name']}", size_hint_x=0.40, color=(0.3, 0.3, 0.3, 1), halign='left'))
            row.add_widget(Label(text=t['transaction_type'], size_hint_x=0.35, color=(0.3, 0.3, 0.3, 1), halign='left'))
            row.add_widget(Label(text=f"UGX {t['amount']:,.2f}", size_hint_x=0.25, color=(0.10, 0.21, 0.36, 1), halign='right', bold=True))
            list_box.add_widget(row)
            
        scroll.add_widget(list_box)
        container.add_widget(scroll)

        commit_btn = Button(text="CONFIRM & COMMIT MEETING BATCH", size_hint_y=None, height='50dp', background_color=(0.17, 0.56, 0.3, 1), background_normal='')
        def commit_meeting(instance):
            self.tx_model.commit_meeting(self.meeting_id)
            self.manager.current = 'dashboard'
        commit_btn.bind(on_release=commit_meeting)
        container.add_widget(commit_btn)

    def _build_member_input_list(self, container, tx_type, fund_source):
        scroll = ScrollView()
        list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_box.bind(minimum_height=list_box.setter('height'))
        
        members = self.member_model.list_active_members(self.active_cycle['cycle_id'] if self.active_cycle else None)
        for m in members:
            row = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
            row.add_widget(Label(text=f"PB: {m['passbook_number']} - {m['full_name']}", size_hint_x=0.4, color=(0.2, 0.2, 0.2, 1)))
            
            amt_input = TextInput(hint_text="Amount (UGX)", size_hint_x=0.3, multiline=False)
            row.add_widget(amt_input)
            
            btn = Button(text="Save", size_hint_x=0.3, background_color=(0.17, 0.42, 0.69, 1), background_normal='')
            def save_entry(instance, mid=m['member_id'], input_field=amt_input):
                try:
                    val = float(input_field.text.strip())
                    self.tx_model.add_transaction({
                        "meeting_id": self.meeting_id,
                        "member_id": mid,
                        "transaction_type": tx_type,
                        "fund_source": fund_source,
                        "amount": val,
                        "shares_count": 0
                    })
                    input_field.text = "Saved ✓"
                except ValueError:
                    pass
            btn.bind(on_release=save_entry)
            row.add_widget(btn)
            list_box.add_widget(row)
            
        scroll.add_widget(list_box)
        container.add_widget(scroll)