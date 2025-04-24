from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import json
import os

# ألوان التطبيق
PRIMARY_COLOR = get_color_from_hex("#6200EE")
BACKGROUND_COLOR = get_color_from_hex("#121212")
ERROR_COLOR = get_color_from_hex("#CF6679")

class PinInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = True
        self.multiline = False
        self.halign = 'center'
        self.font_size = dp(24)
        self.size_hint = (0.8, None)
        self.height = dp(60)
        self.background_normal = ''
        self.background_color = (1, 1, 1, 0.1)

class AppLockerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin = "123456"  # كود افتراضي
        self.locked_apps = {}  # {'app_package': True/False}
        self.load_data()

    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(PinScreen(name='pin'))
        self.sm.add_widget(MainScreen(name='main'))
        return self.sm

    def load_data(self):
        if os.path.exists('locker_data.json'):
            try:
                with open('locker_data.json', 'r') as f:
                    data = json.load(f)
                    self.pin = data.get('pin', "123456")
                    self.locked_apps = data.get('locked_apps', {})
            except:
                pass

    def save_data(self):
        data = {
            'pin': self.pin,
            'locked_apps': self.locked_apps
        }
        with open('locker_data.json', 'w') as f:
            json.dump(data, f)

    def verify_pin(self, pin):
        return pin == self.pin

    def change_pin(self, new_pin):
        self.pin = new_pin
        self.save_data()

    def toggle_app_lock(self, package_name, lock):
        self.locked_apps[package_name] = lock
        self.save_data()

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        
        self.pin_input = PinInput(hint_text="أدخل رمز PIN المكون من 6 أرقام")
        
        self.submit_btn = Button(
            text="تأكيد",
            size_hint=(0.6, None),
            height=dp(50),
            background_normal='',
            background_color=PRIMARY_COLOR
        )
        self.submit_btn.bind(on_press=self.check_pin)
        
        self.error_label = Label(
            text="",
            color=ERROR_COLOR,
            size_hint=(1, 0.1)
        )
        
        layout.add_widget(self.pin_input)
        layout.add_widget(self.submit_btn)
        layout.add_widget(self.error_label)
        self.add_widget(layout)

    def check_pin(self, instance):
        app = App.get_running_app()
        if app.verify_pin(self.pin_input.text):
            self.manager.current = 'main'
            self.error_label.text = ""
        else:
            self.error_label.text = "رمز PIN غير صحيح"
            self.pin_input.text = ""

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # شريط العنوان
        header = BoxLayout(size_hint=(1, 0.1))
        title = Label(text="قفل التطبيقات", font_size=dp(24))
        header.add_widget(title)
        
        # محاكاة قائمة التطبيقات (بدون jnius)
        self.apps_list = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # تطبيقات افتراضية (يمكن استبدالها بقائمة حقيقية)
        default_apps = [
            {"name": "الواتساب", "package": "com.whatsapp"},
            {"name": "فيسبوك", "package": "com.facebook.katana"},
            {"name": "إنستغرام", "package": "com.instagram.android"}
        ]
        
        for app in default_apps:
            btn = Button(
                text=f"{app['name']} - {'مقفل' if app['package'] in App.get_running_app().locked_apps else 'مفتوح'}",
                size_hint_y=None,
                height=dp(60)
            )
            btn.bind(on_press=lambda x, p=app['package']: self.toggle_app(p))
            self.apps_list.add_widget(btn)
        
        layout.add_widget(header)
        layout.add_widget(self.apps_list)
        self.add_widget(layout)

    def toggle_app(self, package_name):
        app = App.get_running_app()
        current_state = app.locked_apps.get(package_name, False)
        app.toggle_app_lock(package_name, not current_state)
        self.manager.current = 'main'  # إعادة تحميل الشاشة

if __name__ == "__main__":
    Window.clearcolor = BACKGROUND_COLOR
    AppLockerApp().run()
