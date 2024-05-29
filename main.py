import subprocess
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock

class StartScreen(Screen):
    def sync_device(self):
        ip = self.ids.device_ip.text
        self.manager.transition.direction = "left"
        self.manager.get_screen('success_loading_screen').ids.loading_device_ip.text = ip
        self.manager.current = "success_loading_screen"
        App.get_running_app().sync_device(ip)

class ErrorScreen(Screen):
    def sync_device(self):
        ip = self.ids.error_device_ip.text
        self.manager.transition.direction = "left"
        self.manager.get_screen('success_loading_screen').ids.loading_device_ip.text = ip
        self.manager.current = "success_loading_screen"
        App.get_running_app().sync_device(ip)

class SuccessLoadingScreen(Screen):
    def sync_device(self):
        ip = self.ids.loading_device_ip.text
        App.get_running_app().sync_device(ip)

class MainScreen(Screen):
    def on_enter(self):
        # Agendar a atualização da imagem a cada 5 segundos
        Clock.schedule_interval(self.update_screenshot, 5)

    def on_leave(self):
        # Cancelar o agendamento da atualização da imagem
        Clock.unschedule(self.update_screenshot)

    def open_browser_link(self):
        link = self.ids.browser_link.text
        try:
            # Executa o comando adb shell
            result = subprocess.run(["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", link], capture_output=True, text=True, check=True)
            # Verifica a saída do comando
            if "Error" in result.stdout:
                error_screen = App.get_running_app().root.get_screen('error_screen')
                error_screen.ids.error_message.text = result.stdout
                App.get_running_app().root.current = "error_screen"
        except subprocess.CalledProcessError as e:
            error_screen = App.get_running_app().root.get_screen('error_screen')
            error_screen.ids.error_message.text = e.stderr
            App.get_running_app().root.current = "error_screen"
    
    # def open_app(self):
    #     app_name = self.ids.app_spinner.text
    #     print(f"Abrindo {app_name}")
    #     # Aqui você pode adicionar a lógica para abrir o aplicativo específico
        
    def update_screenshot(self, dt=None):
        # Captura a tela do dispositivo Android
        subprocess.run(["adb", "shell", "screencap", "/sdcard/screenshot.png"])

        # Copia a imagem para o computador
        subprocess.run(["adb", "pull", "/sdcard/screenshot.png", "prints/screenshot.png"])

        # Atualiza a imagem exibida no aplicativo Kivy
        self.ids.screenshot.reload()

class ADBSyncApp(App):
    def build(self):
        return Builder.load_file('interface.kv')
    
    def sync_device(self, ip):
        try:
            # Executa o comando adb connect
            result = subprocess.run(["adb", "connect", ip], capture_output=True, text=True, check=True)
            # Verifica a saída do comando
            if "connected" in result.stdout:
                self.root.current = "main_screen"
            else:
                error_screen = self.root.get_screen('error_screen')
                error_screen.ids.error_message.text = result.stdout
                self.root.current = "error_screen"
        except subprocess.CalledProcessError as e:
            error_screen = self.root.get_screen('error_screen')
            error_screen.ids.error_message.text = e.stderr
            self.root.current = "error_screen"

    def on_stop(self):
        # Encerra os processos quando o aplicativo é fechado
        if hasattr(self, 'screenrecord_process') and self.screenrecord_process:
            self.screenrecord_process.kill()
        if hasattr(self, 'ffplay_process') and self.ffplay_process:
            self.ffplay_process.kill()

if __name__ == "__main__":
    ADBSyncApp().run()
