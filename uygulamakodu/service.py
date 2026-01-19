import time
import requests
from plyer import notification
from jnius import autoclass

# --- AYARLAR ---
UYGULAMA_BOT_TOKEN = "8258892957:AAHcz395b7Mir1Jd33o0ZstK7qdNPEPzn-U" 
# Servis içinde 'sound' çalmak zordur, sadece bildirim atacağız.

def bildirim_gonder(baslik, mesaj):
    try:
        notification.notify(
            title=baslik,
            message=mesaj,
            app_name='Guvenlik Servisi',
            timeout=10,
            ticker='Guvenlik Uyarisi', # Android eski sürümler için
            toast=True # Ekrana ufak yazı çıkar
        )
    except Exception as e:
        print("Bildirim Hatasi: " + str(e))

def main():
    # --- İŞLEMCİYİ UYANIK TUTMA (WAKE LOCK) ---
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        PowerManager = autoclass('android.os.PowerManager')
        
        activity = PythonActivity.mActivity
        pm = activity.getSystemService(Context.POWER_SERVICE)
        
        # Ekran kapansa bile CPU çalışsın (PARTIAL_WAKE_LOCK)
        wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "OdaKontrol:ServiceLock")
        wake_lock.acquire()
    except Exception as e:
        print("WakeLock alinamadi (PC'de olabilirsin): " + str(e))

    son_update_id = 0
    print("Servis Baslatildi...")
    
    # Servisin başladığını anlaman için telefonuna bir bildirim atalım
    bildirim_gonder("Sistem Aktif", "Arka plan servisi calisiyor.")

    while True:
        try:
            # Telegram kontrolü
            url = f"https://api.telegram.org/bot{UYGULAMA_BOT_TOKEN}/getUpdates"
            params = {'timeout': 5, 'limit': 1}
            if son_update_id != 0:
                params['offset'] = son_update_id + 1
            
            response = requests.get(url, params=params, timeout=10)
            veriler = response.json()

            if veriler.get("ok"):
                for sonuc in veriler.get("result", []):
                    son_update_id = sonuc["update_id"]
                    
                    gelen_mesaj = ""
                    if "message" in sonuc: gelen_mesaj = sonuc["message"].get("text", "")
                    elif "channel_post" in sonuc: gelen_mesaj = sonuc["channel_post"].get("text", "")

                    if gelen_mesaj:
                        if "UYARI" in gelen_mesaj or "ALARM" in gelen_mesaj:
                            bildirim_gonder("🚨 HIRSIZ ALARMI! 🚨", gelen_mesaj)

        except Exception as e:
            # İnternet giderse döngü kırılmasın, 5 sn bekle tekrar dene
            time.sleep(5)
        
        # Pili sömürmemek için 2 saniye bekle
        time.sleep(2)

if __name__ == '__main__':
    main()