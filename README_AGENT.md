# DexAgent - Windows PowerShell Agent

Windows üzerinde çalışan, DexAgents sunucusuna bağlanan ve PowerShell komutlarını çalıştırabilen standalone agent.

## Özellikler

- 🖥️ **Full GUI Interface** - Kullanıcı dostu arayüz
- 🔌 **WebSocket Connection** - Real-time sunucu bağlantısı
- ⚡ **PowerShell Execution** - Windows PowerShell komutlarını çalıştırma
- 📊 **System Monitoring** - Sistem bilgilerini toplama ve gönderme
- 🔄 **Auto-Reconnect** - Bağlantı koptuğunda otomatik yeniden bağlanma
- 📝 **Activity Logging** - Tüm aktiviteleri loglar
- ⚙️ **Easy Configuration** - GUI üzerinden kolay yapılandırma

## Gereksinimler

- **Python 3.8+** (Windows için python.org'dan indirin)
- **Internet bağlantısı** (ilk kurulum için)
- **Windows 10/11** (PowerShell desteği için)

## Kurulum

### Otomatik Kurulum (Önerilen)

1. Tüm dosyaları bir klasöre kopyalayın
2. `install_dexagent.bat` dosyasını **yönetici olarak** çalıştırın
3. Kurulum otomatik olarak tamamlanacak

### Manuel Kurulum

1. Python 3.8+ kurun (python.org'dan)
2. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements_agent.txt
   ```
   veya tek tek:
   ```bash
   pip install websockets psutil requests
   ```

## Yapılandırma

`dexagent_windows.py` dosyasının başındaki `CONFIG` bölümünü düzenleyin:

```python
CONFIG = {
    # Sunucu bağlantı ayarları
    "server_url": "ws://YOUR_SERVER:8080",     # Sunucunuzun WebSocket URL'i
    "api_token": "YOUR_API_TOKEN",             # API token'ınız
    
    # Agent kimlik bilgileri
    "agent_name": "My-Windows-Agent",          # Agent adı
    "tags": ["windows", "desktop", "office"],  # Agent etiketleri
    
    # Davranış ayarları
    "auto_start": True,                        # Başlangıçta otomatik bağlan
    "reconnect_interval": 30,                  # Yeniden bağlanma aralığı (saniye)
    "heartbeat_interval": 60,                  # Heartbeat aralığı (saniye)
}
```

## Çalıştırma

### GUI Modunda (Önerilen)
```bash
python dexagent_windows.py
```
veya masaüstündeki `DexAgent.bat` dosyasını çift tıklayın.

### Komut Satırından
```bash
cd path\to\dexagent
python dexagent_windows.py
```

## GUI Kullanımı

Agent GUI'si şu bileşenleri içerir:

### 1. Connection Status
- **Status**: Bağlantı durumu (Connected/Disconnected/Connecting)
- **Server**: Bağlanılan sunucu URL'i
- **Agent ID**: Benzersiz agent kimliği

### 2. Control Buttons
- **Connect/Disconnect**: Bağlantıyı başlat/durdur
- **Config**: Yapılandırma ayarlarını düzenle
- **Test**: Sunucu bağlantısını test et

### 3. Activity Log
- Tüm agent aktivitelerini gösterir
- **Clear Log**: Logu temizle
- **Save Log**: Logu dosyaya kaydet

## Özellikler Detayı

### PowerShell Command Execution
Agent, sunucudan gelen PowerShell komutlarını güvenli şekilde çalıştırır:
- Komut çıktısı ve hata mesajları döndürülür
- Çalışma süresi kaydedilir
- Exit code rapor edilir

### System Information
Agent düzenli olarak sistem bilgilerini toplar ve gönderir:
- CPU kullanımı
- Bellek kullanımı
- Disk kullanımı
- Ağ arayüzleri
- Platform bilgileri

### Auto-Reconnection
Bağlantı koptuğunda otomatik olarak yeniden bağlanmaya çalışır:
- Akıllı yeniden deneme algoritması
- Maksimum deneme sayısı sınırı
- Artan gecikme süresi

### Logging
Tüm aktiviteler kaydedilir:
- Konsol ve dosya logging
- Farklı log seviyeleri (DEBUG, INFO, WARNING, ERROR)
- GUI'de real-time log görüntüleme

## Güvenlik

- Agent sadece PowerShell komutlarını çalıştırır
- Bütün bağlantılar WebSocket üzerinden şifrelenir
- API token ile kimlik doğrulama
- Agent ID ile benzersiz tanımlama

## Sorun Giderme

### Python bulunamıyor
```
ERROR: Python is not installed or not in PATH
```
**Çözüm**: Python'u python.org'dan indirin ve "Add Python to PATH" seçeneğini işaretleyin.

### Paket yükleme hatası
```
ERROR: Failed to install required packages
```
**Çözüm**: 
1. İnternet bağlantınızı kontrol edin
2. Yönetici olarak çalıştırın
3. Manuel kurulum deneyin: `pip install websockets psutil requests`

### Bağlantı hatası
```
WebSocket connection failed
```
**Çözüm**:
1. Sunucu URL'ini kontrol edin
2. Güvenlik duvarı ayarlarını kontrol edin
3. "Test" butonuyla bağlantıyı test edin

### Komut çalışmıyor
```
Command execution error
```
**Çözüm**:
1. PowerShell'in etkin olduğunu kontrol edin
2. Yürütme politikasını kontrol edin: `Get-ExecutionPolicy`
3. Gerekirse: `Set-ExecutionPolicy RemoteSigned`

## Gelişmiş Kullanım

### Otomatik Başlatma
Windows başlangıcında otomatik çalıştırmak için:
1. `dexagent_windows.py` için kısayol oluşturun
2. Kısayolu `shell:startup` klasörüne kopyalayın

### Servis Olarak Çalıştırma
Windows servisine dönüştürmek için `pywin32` kullanabilirsiniz:
```bash
pip install pywin32
```

### Log Yapılandırması
CONFIG içerisindeki log ayarlarını değiştirebilirsiniz:
```python
"log_level": "DEBUG",        # DEBUG, INFO, WARNING, ERROR
"log_file": "dexagent.log",  # Log dosyası yolu
```

## Dosya Yapısı

```
dexagent/
├── dexagent_windows.py      # Ana agent kodu
├── install_dexagent.bat     # Otomatik kurulum script'i
├── requirements_agent.txt   # Python gereksinimleri
├── README_AGENT.md         # Bu dosya
└── dexagent.log            # Log dosyası (çalıştırıldıktan sonra oluşur)
```

## API Referansı

Agent aşağıdaki WebSocket mesaj tiplerini destekler:

### Gelen Mesajlar
- `command`: PowerShell komutu çalıştır
- `ping`: Bağlantı testi
- `system_info_request`: Sistem bilgisi isteği

### Giden Mesajlar  
- `register`: Agent kaydı
- `command_result`: Komut sonucu
- `heartbeat`: Yaşam sinyali
- `system_info`: Sistem bilgileri
- `pong`: Ping yanıtı

## Lisans

Bu kod DexAgents sistemi ile birlikte kullanılmak üzere tasarlanmıştır.

## Destek

Sorunlar için:
1. Bu README'yi kontrol edin
2. Log dosyalarını inceleyin  
3. DexAgents dokümantasyonuna başvurun
4. "Test" fonksiyonunu kullanarak bağlantıyı test edin