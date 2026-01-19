#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>
#include <HTTPClient.h>

// --- AĞ VE TELEGRAM ---
const char* ssid = "Sezai";
const char* password = "sever2215619";
const char* botToken = "8457648478:AAEY_HUHq4hkr0r_Nwr__DuvaptlCz1Dy08";
const char* chatID = "-1003585595348";

WiFiClientSecure client;
UniversalTelegramBot bot(botToken, client);

// Pinler
const int sensorPin1 = 35; 
const int sensorPin2 = 34; 

// --- HASSAS AYAR ---
// Normalde değer 4095 civarıdır.
// Hızlı geçişlerde değer 500'e inmez, 3500'de kalabilir.
// Bu yüzden sınırı 4000 yapıyoruz ki en ufak gölgeyi yakalasın.
const int esikDeger = 3960; 

// Telegram kontrol sıklığı (Milisaniye)
// Bunu artırdık ki işlemci sensöre daha çok vakit ayırsın.
// Komutlarına 2-3 saniye geç cevap verebilir ama hırsızı kaçırmaz.
int botRequestDelay = 2500; 
unsigned long lastTimeBotRan;
bool sistemAcik = false; 
unsigned long sonHirsizMesajZamani = 0;

void mesajGonder(String mesaj) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    mesaj.replace(" ", "%20");
    String url = "https://api.telegram.org/bot";
    url += botToken;
    url += "/sendMessage?chat_id=";
    url += chatID;
    url += "&text=" + mesaj;
    http.begin(url);
    http.GET();
    http.end();
  }
}

void handleNewMessages(int numNewMessages) {
  for (int i = 0; i < numNewMessages; i++) {
    String text = bot.messages[i].text;
    Serial.println("Komut: " + text);

    if (text.indexOf("ac") > -1) {
      sistemAcik = true;
      mesajGonder("Sistem ACILDI (Ultra Hassas Mod).");
      Serial.println("AKTIF");
    }
    
    if (text.indexOf("kapat") > -1) {
      sistemAcik = false;
      mesajGonder("Sistem KAPATILDI.");
      Serial.println("PASIF");
    }
  }
}

void setup() {
  Serial.begin(921600);
  pinMode(sensorPin1, INPUT);
  pinMode(sensorPin2, INPUT);
  analogReadResolution(12);       
  analogSetAttenuation(ADC_11db); 

  Serial.print("WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(200);
  
  client.setInsecure();
  Serial.println("Hazir! 'ac' komutu bekleniyor...");
}

void loop() {
  // 1. ÖNCE SENSÖR (SÜREKLİ TARAMA)
  // Döngü burada binlerce kez döner
  if (sistemAcik) {
    // analogRead işlemi biraz zaman alır, ardışık okuyup en düşüğünü alalım
    int s1 = analogRead(sensorPin1);
    int s2 = analogRead(sensorPin2);
    
    // Debug için değerleri gör (Hızlı geçişte kaça düşüyor?)
    // Serial.print(s1); Serial.print(" - "); Serial.println(s2);

    // Eşik değer 4000. Bunun altına inen her şey TEHLİKEDİR.
    if (s1 < esikDeger || s2 < esikDeger) { 
      
      Serial.println("YAKALANDI!");
      Serial.print("S1: "); Serial.print(s1);
      Serial.print(" S2: "); Serial.println(s2);

      // Spam engelleme (4 saniye)
      if (millis() - sonHirsizMesajZamani > 4000) {
        mesajGonder("ALARM: HIZLI GECIS TESPIT EDILDI!");
        sonHirsizMesajZamani = millis();
      }
    }
  }

  // 2. TELEGRAM (Nadir Kontrol)
  // İnternet kontrolünü sadece 2.5 saniyede bir yapıyoruz.
  // Bu sayede aradaki 2.5 saniye boyunca işlemci SADECE sensöre bakıyor.
  // Kör nokta çok azaldı.
  if (millis() > lastTimeBotRan + botRequestDelay) {
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    while (numNewMessages) {
      handleNewMessages(numNewMessages);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    }
    lastTimeBotRan = millis();
  }
}