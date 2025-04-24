from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from jnius import autoclass
from android.permissions import request_permissions, Permission
import json
import os

# ألوان التطبيق
PRIMARY_COLOR = get_color_from_hex("#6200EE")
SECONDARY_COLOR = get_color_from_hex("#03DAC6")
BACKGROUND_COLOR = get_color_from_hex("#121212")
SURFACE_COLOR = get_color_from_hex("#1E1E1E")
ERROR_COLOR = get_color_from_hex("#CF6679")

# طلبات الأذونات
request_permissions([Permission.PACKAGE_USAGE_STATS, Permission.QUERY_ALL_PACKAGES])

# الوصول إلى مدير التطبيقات في أندرويد
Context = autoclass('android.content.Context')
PackageManager = autoclass('android.content.pm.PackageManager')

class AppIcon(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(50), dp(50))
        self.source = 'assets/default_icon.png'

class RoundedButton(Button):
    radius = NumericProperty(25)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(16)
        self.bold = True
        self.size_hint = (None, None)
        self.height = dp(50)
        self.width = dp(200)
        
        with self.canvas.before:
            Color(*PRIMARY_COLOR)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius, self.radius]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'pin'
        
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_background)
        
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        
        # أيقونة التطبيق الرئيسية
        self.app_icon = Image(
            source='assets/app_icon.png',
            size_hint=(1, 0.4),
            pos_hint={'center_x': 0.5}
        )
        
        # حقل إدخال PIN
        self.pin_input = TextInput(
            hint_text="أدخل رمز PIN المكون من 6 أرقام",
            password=True,
            multiline=False,
            halign='center',
            font_size=dp(24),
            size_hint=(0.8, None),
            height=dp(60),
            pos_hint={'center_x': 0.5}
        )
        
        # زر التأكيد
        self.submit_btn = RoundedButton(
            text="تأكيد",
            pos_hint={'center_x': 0.5}
        )
        self.submit_btn.bind(on_press=self.verify_pin)
        
        # رسالة الخطأ
        self.error_label = Label(
            text="",
            color=ERROR_COLOR,
            size_hint=(1, 0.1)
        )
        
        layout.add_widget(self.app_icon)
        layout.add_widget(self.pin_input)
        layout.add_widget(self.submit_btn)
        layout.add_widget(self.error_label)
        
        self.add_widget(layout)
    
    def update_background(self, instance, value):
        self.background.pos = instance.pos
        self.background.size = instance.size
    
    def verify_pin(self, instance):
        entered_pin = self.pin_input.text
        app = App.get_running_app()
        
        if len(entered_pin) != 6:
            self.error_label.text = "يجب أن يتكون الرمز من 6 أرقام"
            return
        
        if app.verify_pin(entered_pin):
            self.manager.current = 'main'
            self.error_label.text = ""
            self.pin_input.text = ""
        else:
            self.error_label.text = "رمز PIN غير صحيح"
            self.pin_input.text = ""

class AppCard(BoxLayout):
    app_name = StringProperty("")
    package_name = StringProperty("")
    is_locked = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        self.spacing = dp(15)
        self.padding = [dp(15), dp(10)]
        
        with self.canvas.before:
            Color(*SURFACE_COLOR)
            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )
        self.bind(pos=self.update_background, size=self.update_background)
        
        # أيقونة التطبيق
        self.icon = AppIcon()
        
        # معلومات التطبيق
        self.info_layout = BoxLayout(orientation='vertical')
        self.name_label = Label(
            text=self.app_name,
            halign='right',
            size_hint_y=0.7
        )
        self.package_label = Label(
            text=self.package_name,
            halign='right',
            font_size=dp(12),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.3
        )
        self.info_layout.add_widget(self.name_label)
        self.info_layout.add_widget(self.package_label)
        
        # زر القفل/الفتح
        self.lock_btn = Button(
            text="قفل" if not self.is_locked else "فتح",
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            background_normal='',
            background_color=ERROR_COLOR if not self.is_locked else SECONDARY_COLOR
        )
        self.lock_btn.bind(on_press=self.toggle_lock)
        
        self.add_widget(self.icon)
        self.add_widget(self.info_layout)
        self.add_widget(self.lock_btn)
    
    def update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size
    
    def toggle_lock(self, instance):
        self.is_locked = not self.is_locked
        instance.text = "قفل" if not self.is_locked else "فتح"
        instance.background_color = ERROR_COLOR if not self.is_locked else SECONDARY_COLOR
        
        app = App.get_running_app()
        app.toggle_app_lock(self.package_name, self.is_locked)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_background)
        
        layout = BoxLayout(orientation='vertical')
        
        # شريط العنوان
        self.header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            padding=[dp(10), dp(5)]
        )
        
        # أيقونة التطبيق في الشريط
        self.header_icon = Image(
            source='assets/app_icon.png',
            size_hint=(None, 1),
            width=dp(40)
        )
        
        # عنوان الشاشة
        self.title_label = Label(
            text="قفل التطبيقات",
            font_size=dp(24),
            halign='right'
        )
        
        # زر الإعدادات
        self.settings_btn = Button(
            text="الإعدادات",
            size_hint=(None, 1),
            width=dp(100)
        )
        self.settings_btn.bind(on_press=self.open_settings)
        
        self.header.add_widget(self.header_icon)
        self.header.add_widget(self.title_label)
        self.header.add_widget(self.settings_btn)
        
        # شريط البحث
        self.search_input = TextInput(
            hint_text="ابحث عن تطبيق...",
            size_hint=(1, 0.08),
            background_normal='',
            background_color=SURFACE_COLOR,
            foreground_color=(1, 1, 1, 1),
            padding=[dp(15), dp(10), dp(15), dp(10)],
            font_size=dp(18)
        )
        self.search_input.bind(text=self.filter_apps)
        
        # قائمة التطبيقات
        self.scroll_view = ScrollView(size_hint=(1, 0.82))
        self.apps_grid = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(10),
            padding=[dp(10), 0]
        )
        self.apps_grid.bind(minimum_height=self.apps_grid.setter('height'))
        self.scroll_view.add_widget(self.apps_grid)
        
        layout.add_widget(self.header)
        layout.add_widget(self.search_input)
        layout.add_widget(self.scroll_view)
        
        self.add_widget(layout)
    
    def update_background(self, instance, value):
        self.background.pos = instance.pos
        self.background.size = instance.size
    
    def open_settings(self, instance):
        self.manager.current = 'settings'
    
    def filter_apps(self, instance, value):
        app = App.get_running_app()
        filtered = [a for a in app.installed_apps if value.lower() in a[0].lower()]
        self.display_apps(filtered)
    
    def display_apps(self, apps):
        self.apps_grid.clear_widgets()
        for app_name, package_name, is_locked in apps:
            card = AppCard()
            card.app_name = app_name
            card.package_name = package_name
            card.is_locked = is_locked
            self.apps_grid.add_widget(card)

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_background)
        
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        
        # أيقونة الإعدادات
        self.settings_icon = Image(
            source='assets/settings_icon.png',
            size_hint=(1, 0.3),
            pos_hint={'center_x': 0.5}
        )
        
        # خيار تغيير PIN
        self.change_pin_btn = RoundedButton(
            text="تغيير رمز PIN",
            pos_hint={'center_x': 0.5}
        )
        self.change_pin_btn.bind(on_press=self.show_change_pin_popup)
        
        # زر العودة
        self.back_btn = RoundedButton(
            text="العودة",
            pos_hint={'center_x': 0.5}
        )
        self.back_btn.bind(on_press=self.go_back)
        
        layout.add_widget(self.settings_icon)
        layout.add_widget(self.change_pin_btn)
        layout.add_widget(self.back_btn)
        
        self.add_widget(layout)
    
    def update_background(self, instance, value):
        self.background.pos = instance.pos
        self.background.size = instance.size
    
    def show_change_pin_popup(self, instance):
        popup = ChangePinPopup()
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'main'

class ChangePinPopup(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.6)
        self.background_color = (0, 0, 0, 0.7)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        self.title_label = Label(
            text="تغيير رمز PIN",
            font_size=dp(24),
            color=(1, 1, 1, 1)
        )
        
        self.current_pin = TextInput(
            hint_text="الرمز الحالي",
            password=True,
            size_hint=(1, None),
            height=dp(60),
            font_size=dp(24),
            halign='center'
        )
        
        self.new_pin = TextInput(
            hint_text="الرمز الجديد (6 أرقام)",
            password=True,
            size_hint=(1, None),
            height=dp(60),
            font_size=dp(24),
            halign='center'
        )
        
        self.confirm_pin = TextInput(
            hint_text="تأكيد الرمز الجديد",
            password=True,
            size_hint=(1, None),
            height=dp(60),
            font_size=dp(24),
            halign='center'
        )
        
        self.error_label = Label(
            text="",
            color=ERROR_COLOR
        )
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(20))
        self.submit_btn = Button(
            text="حفظ",
            size_hint=(0.5, None),
            height=dp(50),
            background_normal='',
            background_color=PRIMARY_COLOR
        )
        self.submit_btn.bind(on_press=self.change_pin)
        
        self.cancel_btn = Button(
            text="إلغاء",
            size_hint=(0.5, None),
            height=dp(50),
            background_normal='',
            background_color=ERROR_COLOR
        )
        self.cancel_btn.bind(on_press=self.dismiss)
        
        buttons_layout.add_widget(self.submit_btn)
        buttons_layout.add_widget(self.cancel_btn)
        
        layout.add_widget(self.title_label)
        layout.add_widget(self.current_pin)
        layout.add_widget(self.new_pin)
        layout.add_widget(self.confirm_pin)
        layout.add_widget(self.error_label)
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def change_pin(self, instance):
        app = App.get_running_app()
        current = self.current_pin.text
        new = self.new_pin.text
        confirm = self.confirm_pin.text
        
        if not app.verify_pin(current):
            self.error_label.text = "الرمز الحالي غير صحيح"
            return
        
        if len(new) != 6 or not new.isdigit():
            self.error_label.text = "يجب أن يتكون الرمز من 6 أرقام"
            return
        
        if new != confirm:
            self.error_label.text = "الرمز الجديد غير متطابق"
            return
        
        app.change_pin(new)
        self.error_label.text = "تم تغيير الرمز بنجاح"
        Clock.schedule_once(self.dismiss, 1.5)

class AppLocker(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin = "123456"
        self.locked_apps = {}
        self.installed_apps = []
        self.screen_manager = ScreenManager(transition=FadeTransition())
        
        # تحميل البيانات عند البدء
        self.load_data()
    
    def build(self):
        # إعداد واجهة المستخدم
        self.screen_manager.add_widget(PinScreen(name='pin'))
        self.screen_manager.add_widget(MainScreen(name='main'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        
        # الحصول على التطبيقات المثبتة
        self.get_installed_apps()
        
        return self.screen_manager
    
    def load_data(self):
        if os.path.exists("applocker_data.json"):
            try:
                with open("applocker_data.json", "r") as f:
                    data = json.load(f)
                    self.pin = data.get("pin", "123456")
                    self.locked_apps = data.get("locked_apps", {})
            except:
                pass
    
    def save_data(self):
        data = {
            "pin": self.pin,
            "locked_apps": self.locked_apps
        }
        
        with open("applocker_data.json", "w") as f:
            json.dump(data, f)
    
    def get_installed_apps(self):
        context = Context.getApplicationContext()
        package_manager = context.getPackageManager()
        packages = package_manager.getInstalledApplications(PackageManager.GET_META_DATA)
        
        self.installed_apps = []
        for package in packages:
            try:
                app_name = str(package_manager.getApplicationLabel(package))
                package_name = str(package.packageName)
                
                # تخطي تطبيقات النظام
                if not package_name.startswith(('com.android', 'android')):
                    is_locked = self.locked_apps.get(package_name, False)
                    self.installed_apps.append((app_name, package_name, is_locked))
            except:
                continue
    
    def verify_pin(self, pin):
        return pin == self.pin
    
    def change_pin(self, new_pin):
        self.pin = new_pin
        self.save_data()
    
    def toggle_app_lock(self, package_name, lock):
        self.locked_apps[package_name] = lock
        self.save_data()
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        if hasattr(self, 'screen_manager'):
            self.screen_manager.current = 'pin'
        return True

if __name__ == "__main__":
    Window.clearcolor = BACKGROUND_COLOR
    AppLocker().run()
