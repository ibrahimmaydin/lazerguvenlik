import sys
import os
import certifi
import requests
import threading
from kivy.utils import platform
from plyer import notification 
from kivy.core.audio import SoundLoader 
from kivy.metrics import dp, sp 

os.environ["SSL_CERT_FILE"] = certifi.where()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.uix.popup import Popup

if platform != 'android':
    Window.size = (400, 700)

# --- AYARLAR ---
UYGULAMA_BOT_TOKEN = "8258892957:AAHcz395b7Mir1Jd33o0ZstK7qdNPEPzn-U" 
CHAT_ID = "-1003585595348"

class TiklanabilirResim(ButtonBehavior, Image):
    pass

class YanMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, 1)
        self.width = dp(250)
        self.x = -dp(250)
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.guncelle_rect, size=self.guncelle_rect)
        self.add_widget(Label(text="MENÜ", font_size=sp(24), bold=True, size_hint_y=0.1))
        self.add_widget(Button(text="Kapat", on_press=self.kapat, size_hint_y=None, height=dp(60)))
        self.add_widget(Label())
    def guncelle_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    def kapat(self, instance):
        App.get_running_app().stop()

class AnaEkran(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        self.son_update_id = 0
        self.alarm_sesi = None 
        
        self.ana_icerik = BoxLayout(orientation='vertical')
        
        # --- HEADER ---
        self.header = BoxLayout(size_hint_y=None, height=dp(90), padding=dp(15), spacing=dp(15))
        with self.header.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.header_rect = Rectangle(pos=self.header.pos, size=self.header.size)
        self.header.bind(pos=self.guncelle_header, size=self.guncelle_header)

        self.menu_btn = TiklanabilirResim(source='pngegg.png', size_hint=(None, None), size=(dp(50), dp(50)), allow_stretch=True, pos_hint={'center_y':0.5})
        self.menu_btn.bind(on_press=self.menu_ac_kapat)
        
        self.baslik = Label(text="Lazer Güvenlik Sistem v1.0", font_size=sp(24), bold=True)
        self.header.add_widget(self.menu_btn)
        self.header.add_widget(self.baslik)
        
        # --- ORTA ALAN ---
        self.orta_alan = BoxLayout(orientation='vertical', padding=dp(50), spacing=dp(20))
        self.resim_butonu = TiklanabilirResim(source='dugmekapali.png', allow_stretch=True, size_hint=(1, 0.6))
        self.resim_butonu.bind(on_press=self.resim_tiklandi)
        self.durum_etiketi = Label(text="Sistem Hazır", color=(0.2, 0.2, 0.2, 1), font_size=sp(20), size_hint_y=0.1)

        self.orta_alan.add_widget(self.resim_butonu)
        self.orta_alan.add_widget(self.durum_etiketi)
        self.ana_icerik.add_widget(self.header)
        self.ana_icerik.add_widget(self.orta_alan)
        self.add_widget(self.ana_icerik)
        self.yan_menu = YanMenu()
        self.add_widget(self.yan_menu)
        self.menu_acik = False

        Clock.schedule_interval(self.mesajlari_kontrol_et_baslat, 3)

        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.POST_NOTIFICATIONS, Permission.VIBRATE, Permission.FOREGROUND_SERVICE])
                
                from android import mActivity
                context = mActivity.getApplicationContext()
                
                # Spec dosyasındaki servis adı 'guvenlik' ise burası ServiceGuvenlik olur
                service_name = 'org.ibrahim.lazersistem.ServiceGuvenlik'
                
                import jnius
                PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
                service_class = jnius.autoclass(service_name)
                service_intent = jnius.autoclass('android.content.Intent')(PythonActivity.mActivity, service_class)
                service_intent.putExtra("python_service_argument", "boot")
                PythonActivity.mActivity.startService(service_intent)
                
            except Exception as e:
                print(f"Android hatasi: {e}")

    def on_touch_down(self, touch):
        if self.menu_acik and not self.yan_menu.collide_point(*touch.pos) and not self.menu_btn.collide_point(*touch.pos):
            self.menu_ac_kapat(None)
            return True
        return super().on_touch_down(touch)

    def guncelle_header(self, *args):
        self.header_rect.pos = self.header.pos
        self.header_rect.size = self.header.size

    def menu_ac_kapat(self, instance):
        anim = Animation(x=(-dp(250) if self.menu_acik else 0), duration=0.3, t='out_cubic')
        anim.start(self.yan_menu)
        self.menu_acik = not self.menu_acik

    def resim_tiklandi(self, instance):
        if "kapali" in self.resim_butonu.source:
            self.komut_gonder("ac")
        else:
            self.komut_gonder("kapat")

    def komut_gonder(self, komut):
        threading.Thread(target=self._gonder_thread, args=(komut,)).start()

    def _gonder_thread(self, komut):
        try:
            url = f"https://api.telegram.org/bot{UYGULAMA_BOT_TOKEN}/sendMessage"
            mesaj = "/ac" if komut == "ac" else "/kapat"
            requests.post(url, data={"chat_id": CHAT_ID, "text": mesaj}, timeout=5)
            Clock.schedule_once(lambda dt: self.arayuz_guncelle(komut))
        except: pass

    def arayuz_guncelle(self, komut):
        if komut == "ac":
            self.resim_butonu.source = 'dugmeacik.png'
            self.durum_etiketi.text = "SİSTEM AÇIK"
            self.durum_etiketi.color = (0, 0.7, 0, 1)
        else:
            self.resim_butonu.source = 'dugmekapali.png'
            self.durum_etiketi.text = "SİSTEM KAPALI"
            self.durum_etiketi.color = (0.8, 0, 0, 1)

    def mesajlari_kontrol_et_baslat(self, dt):
        threading.Thread(target=self._kontrol_thread).start()

    def _kontrol_thread(self):
        try:
            url = f"https://api.telegram.org/bot{UYGULAMA_BOT_TOKEN}/getUpdates"
            params = {'timeout': 1}
            if self.son_update_id != 0:
                params['offset'] = self.son_update_id + 1
            
            response = requests.get(url, params=params, timeout=3)
            veriler = response.json()

            if veriler.get("ok"):
                for sonuc in veriler.get("result", []):
                    self.son_update_id = sonuc["update_id"]
                    gelen_mesaj = ""
                    if "message" in sonuc: gelen_mesaj = sonuc["message"].get("text", "")
                    elif "channel_post" in sonuc: gelen_mesaj = sonuc["channel_post"].get("text", "")

                    if gelen_mesaj:
                        if "UYARI" in gelen_mesaj or "ALARM" in gelen_mesaj:
                            Clock.schedule_once(lambda dt: self.uyari_popup_ac(gelen_mesaj))
                            self.sistem_bildirimi_gonder("GÜVENLİK UYARISI", gelen_mesaj)
                            # --- SES ÇALMA TETİKLEME (DÜZELTİLDİ) ---
                            Clock.schedule_once(self.alarm_sesi_cal)
        except: pass

    # --- MP3 UYUMLU SES FONKSİYONU ---
    def alarm_sesi_cal(self, dt=None):
        try:
            # MP3 dosyasını yüklüyoruz
            if self.alarm_sesi is None:
                self.alarm_sesi = SoundLoader.load('alarm.mp3') # <-- MP3 OLARAK GÜNCELLENDİ
            
            if self.alarm_sesi:
                if self.alarm_sesi.state == 'play':
                    self.alarm_sesi.stop()
                self.alarm_sesi.play()
            else:
                print("SES HATASI: alarm.mp3 bulunamadı!")
        except Exception as e: 
            print(f"Ses Hatasi: {e}")

    def sistem_bildirimi_gonder(self, baslik, mesaj):
        try:
            notification.notify(
                title=baslik,
                message=mesaj,
                app_name='Oda Kontrol',
                timeout=10
            )
        except: pass

    def uyari_popup_ac(self, mesaj):
        icerik = BoxLayout(orientation='vertical', padding=10, spacing=10)
        lbl = Label(text=f"ESP32 UYARISI:\n{mesaj}", font_size=sp(16), halign='center')
        btn = Button(text="Tamam", size_hint_y=None, height=dp(50), background_color=(1,0,0,1))
        icerik.add_widget(lbl)
        icerik.add_widget(btn)
        popup = Popup(title='DİKKAT', content=icerik, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class MyApp(App):
    def build(self):
        return AnaEkran()

if __name__ == '__main__':
    MyApp().run()