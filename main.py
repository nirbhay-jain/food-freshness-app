from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform
import numpy as np
import cv2
import os

# Safe loading for TFLite
try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    try:
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter
    except:
        Interpreter = None

class FreshnessApp(App):
    def build(self):
        # 1. Android Permissions
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA])

        # 2. Setup AI Brain
        self.interpreter = None
        self.labels = ['Fresh', 'Rotten']
        
        try:
            if Interpreter:
                if not os.path.exists("food_model.tflite"):
                    print("Error: food_model.tflite not found")
                
                self.interpreter = Interpreter(model_path="food_model.tflite")
                
                # --- FIX FOR (1,1,1,3) ERROR ---
                # We force the model to accept (1, 224, 224, 3) 
                # This fixes models that converted with 'dynamic' shapes.
                input_index = self.interpreter.get_input_details()[0]['index']
                self.interpreter.resize_tensor_input(input_index, [1, 224, 224, 3])
                
                # Re-allocate after resizing
                self.interpreter.allocate_tensors()
                
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                
                self.expected_shape = list(self.input_details[0]['shape'])
                self.expected_dtype = self.input_details[0]['dtype']
                
                print(f"DEBUG: Successfully forced shape to: {self.expected_shape}")
        except Exception as e:
            print(f"Model Load Error: {e}")

        # 3. UI Layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.camera = Camera(play=False, resolution=(640, 480), index=0)
        self.layout.add_widget(self.camera)

        self.result_label = Label(text="Tap 'Open' to start", size_hint_y=0.15)
        self.layout.add_widget(self.result_label)

        self.btn_box = BoxLayout(size_hint_y=0.2, spacing=10)
        
        self.open_btn = Button(text="Open Camera", background_color=(0.2, 0.6, 1, 1))
        self.open_btn.bind(on_press=self.toggle_camera)
        
        self.check_btn = Button(text="Check", background_color=(0.2, 0.8, 0.2, 1), disabled=True)
        self.check_btn.bind(on_press=self.analyze_frame)

        self.btn_box.add_widget(self.open_btn)
        self.btn_box.add_widget(self.check_btn)
        self.layout.add_widget(self.btn_box)

        return self.layout

    def toggle_camera(self, instance):
        if not self.camera.play:
            self.camera.play = True
            self.open_btn.text = "Stop"
            self.check_btn.disabled = False
        else:
            self.camera.play = False
            self.open_btn.text = "Open"
            self.check_btn.disabled = True

    def analyze_frame(self, instance):
        if not self.interpreter:
            self.result_label.text = "AI Brain not loaded!"
            return

        try:
            self.camera.export_to_png("scan.png")
            frame = cv2.imread("scan.png")
            if frame is None:
                self.result_label.text = "Capture Failed"
                return

            # Process image specifically for 224x224 RGB
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (224, 224))

            if self.expected_dtype == np.float32:
                img = img.astype(np.float32) / 255.0
            else:
                img = img.astype(self.expected_dtype)

            # Final check on dimensions
            img_final = np.expand_dims(img, axis=0).copy()

            # Run prediction
            self.interpreter.set_tensor(self.input_details[0]['index'], img_final)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            idx = np.argmax(output[0])
            score = output[0][idx] * 100
            self.result_label.text = f"{self.labels[idx]} ({score:.1f}%)"
            
        except Exception as e:
            self.result_label.text = "Prediction Error"
            print(f"CRITICAL ERROR: {e}")

if __name__ == '__main__':
    FreshnessApp().run()