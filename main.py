from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from database.db_manager import DatabaseManager
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.meeting_screen import MeetingScreen
from ui.screens.member_screen import MembersScreen
from ui.screens.reports_screen import ReportsScreen
from ui.screens.new_cycle_screen import NewCycleScreen
from ui.screens.archive_screen import ArchiveScreen

Window.size = (1200, 600)

class DigiSaveApp(App):
    def build(self):
        self.title = "DigiSave - VSLA Automation System"
        self.db = DatabaseManager()
        
        sm = ScreenManager()
        sm.app = self
        
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(MeetingScreen(name='meeting'))
        sm.add_widget(MembersScreen(name='members'))
        sm.add_widget(ReportsScreen(name='reports'))
        sm.add_widget(NewCycleScreen(name='new_cycle'))
        sm.add_widget(ArchiveScreen(name='archive'))
        
        return sm

if __name__ == '__main__':
    DigiSaveApp().run()