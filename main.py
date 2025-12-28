from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

class SimpleFreshnessApp(App):
    def build(self):
        # 1. Request camera permission on Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])

        # 2. Create simple UI
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = Label(
            text='Food Freshness Checker\n(Build Test Version)',
            font_size='24sp',
            size_hint_y=0.3
        )
        layout.add_widget(title)
        
        # Status label
        self.status_label = Label(
            text='App is working!\nTap button below to test.',
            font_size='18sp',
            size_hint_y=0.4
        )
        layout.add_widget(self.status_label)
        
        # Test button
        test_button = Button(
            text='Test Button',
            size_hint_y=0.3,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        test_button.bind(on_press=self.on_button_press)
        layout.add_widget(test_button)
        
        return layout
    
    def on_button_press(self, instance):
        self.status_label.text = 'Button works! ✓\n\nBuild successful!\nNext: Add AI features'

if __name__ == '__main__':
    SimpleFreshnessApp().run()