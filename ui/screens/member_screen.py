from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from models.member_model import MemberModel
from models.cycle_model import CycleModel
import os

kv_path = os.path.join(os.path.dirname(__file__), "../kv/members.kv")
if os.path.exists(kv_path):
    Builder.load_file(kv_path)

class MembersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.editing_member_id = None

    def on_enter(self):
        app = self.manager.app if hasattr(self.manager, 'app') else None
        if app:
            self.member_model = MemberModel(app.db)
            self.cycle_model = CycleModel(app.db)
            self.load_members()

    def register_or_update_member(self):
        passbook = self.ids.txt_passbook.text.strip()
        fullname = self.ids.txt_fullname.text.strip()
        phone = self.ids.txt_phone.text.strip()
        nok_name = self.ids.txt_nok_name.text.strip()
        nok_relation = self.ids.txt_nok_relation.text.strip()
        nok_phone = self.ids.txt_nok_phone.text.strip()

        if not passbook or not fullname:
            return  # Basic validation check

        active_cycle = self.cycle_model.get_active_cycle()
        cycle_id = active_cycle['cycle_id'] if active_cycle else None

        data = {
            "passbook_number": passbook,
            "full_name": fullname,
            "phone_contact": phone,
            "joined_cycle_id": cycle_id,
            "next_of_kin_name": nok_name or "N/A",
            "next_of_kin_relation": nok_relation or "N/A",
            "next_of_kin_phone": nok_phone or "N/A",
            "status": "ACTIVE"
        }

        if self.editing_member_id:
            # Update existing member
            self.member_model.update_member(self.editing_member_id, data)
            self.editing_member_id = None
        else:
            # Create new member
            self.member_model.create_member(data)

        self.clear_form()
        self.load_members()

    def load_members(self):
        container = self.ids.members_list_container
        container.clear_widgets()

        # Fixed method call: list_active_members()
        members = self.member_model.list_active_members()
        for m in members:
            row = BoxLayout(size_hint_y=None, height='40dp', spacing=8)
            row.add_widget(Label(text=f"PB: {m['passbook_number']}", size_hint_x=0.15, color=(0.2, 0.2, 0.2, 1), bold=True))
            row.add_widget(Label(text=m['full_name'], size_hint_x=0.25, color=(0.2, 0.2, 0.2, 1)))
            row.add_widget(Label(text=f"Phone: {m['phone_contact'] or 'N/A'}", size_hint_x=0.2, color=(0.4, 0.4, 0.4, 1)))
            
            # Edit Button
            edit_btn = Button(text="Edit", size_hint_x=0.2, background_color=(0.25, 0.35, 0.45, 1), background_normal='')
            def prep_edit(instance, member_data=m):
                self.editing_member_id = member_data['member_id']
                self.ids.txt_passbook.text = str(member_data['passbook_number'])
                self.ids.txt_fullname.text = member_data['full_name']
                self.ids.txt_phone.text = member_data['phone_contact'] or ""
                self.ids.txt_nok_name.text = member_data['next_of_kin_name'] or ""
                self.ids.txt_nok_relation.text = member_data['next_of_kin_relation'] or ""
                self.ids.txt_nok_phone.text = member_data['next_of_kin_phone'] or ""
            edit_btn.bind(on_release=prep_edit)
            row.add_widget(edit_btn)

            # Soft Delete Button
            del_btn = Button(text="Delete", size_hint_x=0.2, background_color=(0.85, 0.3, 0.2, 1), background_normal='')
            def soft_del(instance, mid=m['member_id']):
                self.member_model.soft_delete_member(mid)
                self.load_members()
            del_btn.bind(on_release=soft_del)
            row.add_widget(del_btn)

            container.add_widget(row)

    def clear_form(self):
        self.editing_member_id = None
        self.ids.txt_passbook.text = ""
        self.ids.txt_fullname.text = ""
        self.ids.txt_phone.text = ""
        self.ids.txt_nok_name.text = ""
        self.ids.txt_nok_relation.text = ""
        self.ids.txt_nok_phone.text = ""