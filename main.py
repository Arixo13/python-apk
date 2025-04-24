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
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from jnius import autoclass
from android.permissions import request_permissions, Permission
import json
import os

# ألوان التطبيق
PRIMARY_COLOR = get_color_from_hex("#6200EE")
PRIMARY_LIGHT = get_color_from_hex("#BB86FC")
SECONDARY_COLOR = get_color_from_hex("#03DAC6")
BACKGROUND_COLOR = get_color_from_hex("#121212")
SURFACE_COLOR = get_color_from_hex("#1E1E1E")
ERROR_COLOR = get_color_from_hex("#CF6679")

# طلبات الأذونات
request_permissions([Permission.PACKAGE_USAGE_STATS, Permission.QUERY_ALL_PACKAGES])

# الوصول إلى مدير التطبيقات في أندرويد
Context = autoclass('android.content.Context')
PackageManager = autoclass('android.content.pm.PackageManager')
Intent = autoclass('android.content.Intent')
Settings = autoclass('android.provider.Settings')

class RoundedButton(Button):
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
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(25),])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class PinInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = True
        self.multiline = False
        self.halign = 'center'
        self.font_size = dp(24)
        self.input_filter = 'int'
        self.max_length = 6
        self.background_normal = ''
        self.background_active = ''
        self.background_color = SURFACE_COLOR
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.height = dp(60)
        self.width = dp(300)
        
        with self.canvas.before:
            Color(*SURFACE_COLOR)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10),])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class AppCard(BoxLayout):
    app_name = StringProperty('')
    package_name = StringProperty('')
    is_locked = BooleanProperty(False)
    icon = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        self.spacing = dp(10)
        self.padding = [dp(10), dp(5), dp(10), dp(5)]
        
        with self.canvas.before:
            Color(*SURFACE_COLOR)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15),])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def toggle_lock(self):
        self.is_locked = not self.is_locked
        app = App.get_running_app()
        app.toggle_app_lock(self.package_name, self.is_locked)

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'pin'
        self.pin = ''
        
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        
        # شعار التطبيق
        self.logo = Image(source='logo.png', size_hint=(1, 0.4))
        
        # عنوان الشاشة
        self.title_label = Label(
            text="أدخل رمز PIN المكون من 6 أرقام",
            font_size=dp(24),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1)
        )
        
        # حقل إدخال PIN
        self.pin_input = PinInput()
        
        # رسالة الخطأ
        self.error_label = Label(
            text="",
            font_size=dp(16),
            color=ERROR_COLOR,
            size_hint=(1, 0.1)
        )
        
        # أزرار
        buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=dp(20))
        self.submit_btn = RoundedButton(text="تأكيد")
        self.submit_btn.bind(on_press=self.check_pin)
        
        buttons_layout.add_widget(self.submit_btn)
        
        layout.add_widget(self.logo)
        layout.add_widget(self.title_label)
        layout.add_widget(self.pin_input)
        layout.add_widget(self.error_label)
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def check_pin(self, instance):
        entered_pin = self.pin_input.text
        app = App.get_running_app()
        
        if len(entered_pin) != 6:
            self.error_label.text = "يجب أن يتكون الرمز من 6 أرقام"
            return
        
        if app.check_pin(entered_pin):
            app.root.current = 'main'
            self.error_label.text = ""
            self.pin_input.text = ""
        else:
            self.error_label.text = "رمز PIN غير صحيح"
            self.pin_input.text = ""

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        layout = BoxLayout(orientation='vertical')
        
        # شريط العنوان
        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=dp(10))
        title = Label(text="قفل التطبيقات", font_size=dp(24), color=(1, 1, 1, 1))
        settings_btn = Button(text="الإعدادات", size_hint=(None, 1), width=dp(100))
        settings_btn.bind(on_press=self.open_settings)
        header.add_widget(title)
        header.add_widget(settings_btn)
        
        # شريط البحث
        self.search_input = TextInput(
            hint_text="ابحث عن تطبيق...",
            size_hint=(1, 0.08),
            background_normal='',
            background_color=SURFACE_COLOR,
            foreground_color=(1, 1, 1, 1),
            padding=dp(10),
            font_size=dp(18)
        )
        self.search_input.bind(text=self.update_search_results)
        
        # عرض التطبيقات
        self.scroll_view = ScrollView(size_hint=(1, 0.82))
        self.apps_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10))
        self.apps_grid.bind(minimum_height=self.apps_grid.setter('height'))
        self.scroll_view.add_widget(self.apps_grid)
        
        layout.add_widget(header)
        layout.add_widget(self.search_input)
        layout.add_widget(self.scroll_view)
        
        self.add_widget(layout)
    
    def open_settings(self, instance):
        self.manager.current = 'settings'
    
    def update_search_results(self, instance, value):
        app = App.get_running_app()
        filtered_apps = [pkg for pkg in app.installed_apps if value.lower() in pkg[0].lower()]
        self.display_apps(filtered_apps)
    
    def display_apps(self, apps):
        self.apps_grid.clear_widgets()
        
        for app_name, package_name, icon, is_locked in apps:
            card = AppCard()
            card.app_name = app_name
            card.package_name = package_name
            card.is_locked = is_locked
            card.icon = icon
            
            # هنا يجب تحويل أيقونة التطبيق إلى صورة يمكن عرضها في Kivy
            # هذا الجزء يحتاج إلى تعديل حسب كيفية التعامل مع الأيقونات
            
            self.apps_grid.add_widget(card)

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        
        # عنوان الشاشة
        title = Label(text="الإعدادات", font_size=dp(24), color=(1, 1, 1, 1))
        
        # تغيير PIN
        change_pin_btn = RoundedButton(text="تغيير رمز PIN")
        change_pin_btn.bind(on_press=self.change_pin)
        
        # حماية الإعدادات
        protect_settings = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        protect_label = Label(text="حماية الإعدادات بكلمة المرور", color=(1, 1, 1, 1))
        self.protect_switch = Switch(active=App.get_running_app().settings_protected)
        self.protect_switch.bind(active=self.toggle_settings_protection)
        protect_settings.add_widget(protect_label)
        protect_settings.add_widget(self.protect_switch)
        
        # العودة للشاشة الرئيسية
        back_btn = RoundedButton(text="العودة")
        back_btn.bind(on_press=self.go_back)
        
        layout.add_widget(title)
        layout.add_widget(change_pin_btn)
        layout.add_widget(protect_settings)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def change_pin(self, instance):
        popup = ChangePinPopup()
        popup.open()
    
    def toggle_settings_protection(self, instance, value):
        App.get_running_app().settings_protected = value
    
    def go_back(self, instance):
        self.manager.current = 'main'

class ChangePinPopup(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.6)
        self.background_color = (0, 0, 0, 0.7)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        title = Label(text="تغيير رمز PIN", font_size=dp(24), color=(1, 1, 1, 1))
        
        self.current_pin = PinInput(hint_text="أدخل الرمز الحالي")
        self.new_pin = PinInput(hint_text="أدخل الرمز الجديد")
        self.confirm_pin = PinInput(hint_text="أكد الرمز الجديد")
        
        self.error_label = Label(text="", color=ERROR_COLOR)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(20))
        submit_btn = RoundedButton(text="تأكيد", size_hint=(0.5, None), height=dp(50))
        cancel_btn = RoundedButton(text="إلغاء", size_hint=(0.5, None), height=dp(50))
        
        submit_btn.bind(on_press=self.submit_change)
        cancel_btn.bind(on_press=self.dismiss)
        
        buttons_layout.add_widget(submit_btn)
        buttons_layout.add_widget(cancel_btn)
        
        layout.add_widget(title)
        layout.add_widget(self.current_pin)
        layout.add_widget(self.new_pin)
        layout.add_widget(self.confirm_pin)
        layout.add_widget(self.error_label)
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def submit_change(self, instance):
        app = App.get_running_app()
        current = self.current_pin.text
        new = self.new_pin.text
        confirm = self.confirm_pin.text
        
        if not app.check_pin(current):
            self.error_label.text = "الرمز الحالي غير صحيح"
            return
        
        if len(new) != 6 or not new.isdigit():
            self.error_label.text = "يجب أن يتكون الرمز الجديد من 6 أرقام"
            return
        
        if new != confirm:
            self.error_label.text = "الرمز الجديد غير متطابق"
            return
        
        app.change_pin(new)
        self.error_label.text = "تم تغيير الرمز بنجاح"
        Clock.schedule_once(self.dismiss, 1)

class AppLockerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin = '123456'  # سيتم استبدالها بالقيمة المحفوظة
        self.locked_apps = {}  # {package_name: True/False}
        self.settings_protected = True
        self.installed_apps = []  # (app_name, package_name, icon, is_locked)
        self.sm = ScreenManager(transition=FadeTransition())
    
    def build(self):
        # تحميل البيانات المحفوظة
        self.load_data()
        
        # الحصول على قائمة التطبيقات المثبتة
        self.get_installed_apps()
        
        # إعداد واجهة المستخدم
        self.sm.add_widget(PinScreen())
        self.sm.add_widget(MainScreen())
        self.sm.add_widget(SettingsScreen())
        
        return self.sm
    
    def load_data(self):
        if not os.path.exists('app_locker_data.json'):
            return
        
        try:
            with open('app_locker_data.json', 'r') as f:
                data = json.load(f)
                self.pin = data.get('pin', '123456')
                self.locked_apps = data.get('locked_apps', {})
                self.settings_protected = data.get('settings_protected', True)
        except:
            pass
    
    def save_data(self):
        data = {
            'pin': self.pin,
            'locked_apps': self.locked_apps,
            'settings_protected': self.settings_protected
        }
        
        with open('app_locker_data.json', 'w') as f:
            json.dump(data, f)
    
    def get_installed_apps(self):
        context = Context.getApplicationContext()
        package_manager = context.getPackageManager()
        packages = package_manager.getInstalledApplications(PackageManager.GET_META_DATA)
        
        self.installed_apps = []
        for package in packages:
            app_name = str(package_manager.getApplicationLabel(package))
            package_name = str(package.packageName)
            
            # تخطي تطبيقات النظام إذا لزم الأمر
            if package_name.startswith('com.android'):
                continue
                
            is_locked = self.locked_apps.get(package_name, False)
            
            # الحصول على أيقونة التطبيق (هذا الجزء يحتاج إلى تعديل)
            icon = None
            
            self.installed_apps.append((app_name, package_name, icon, is_locked))
    
    def check_pin(self, entered_pin):
        return entered_pin == self.pin
    
    def change_pin(self, new_pin):
        self.pin = new_pin
        self.save_data()
    
    def toggle_app_lock(self, package_name, is_locked):
        self.locked_apps[package_name] = is_locked
        self.save_data()
        
        if is_locked:
            # هنا يجب إضافة كود لمراقبة التطبيق المقفل
            pass
    
    def on_pause(self):
        # عند مغادرة التطبيق، تأكد من أنه محمي
        return True
    
    def on_resume(self):
        # عند العودة للتطبيق، اطلب رمز PIN إذا كانت الحماية مفعلة
        if self.settings_protected:
            self.sm.current = 'pin'
        return True

if __name__ == "__main__":
    Window.clearcolor = BACKGROUND_COLOR
    AppLockerApp().run()
