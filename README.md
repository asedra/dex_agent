# Windows PowerShell Agent

Windows cihazlarda PowerShell komutlarını API üzerinden güvenli bir şekilde çalıştıran FastAPI tabanlı agent.

## Özellikler

- 🔐 **Güvenli API**: Bearer token authentication
- ⚡ **Asenkron İşlem**: Hızlı komut çalıştırma
- 🛡️ **Güvenlik**: Timeout ve komut validasyonu
- 📊 **Sistem Bilgileri**: CPU, RAM, disk kullanımı
- 🔄 **Batch İşlemler**: Çoklu komut çalıştırma
- 📝 **Detaylı Loglama**: Komut çalıştırma geçmişi

## Kurulum

### Gereksinimler

- Python 3.11+
- Windows 10/11
- PowerShell 5.1+

### Adımlar

1. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Environment dosyasını oluşturun:**
```bash
copy env.example .env
```

3. **API token'ını ayarlayın:**
`.env` dosyasında `API_TOKEN` değerini güvenli bir token ile değiştirin.

## Kullanım

### Sunucuyu Başlatma

```bash
python app.py
```

Veya uvicorn ile:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### 1. Health Check
```http
GET /
```

#### 2. Sistem Bilgileri
```http
GET /system/info
Authorization: Bearer your_api_token
```

#### 3. Tek Komut Çalıştırma
```http
POST /execute
Authorization: Bearer your_api_token
Content-Type: application/json

{
  "command": "Get-Process",
  "timeout": 30,
  "working_directory": "C:\\",
  "run_as_admin": false
}
```

#### 4. Batch Komut Çalıştırma
```http
POST /execute/batch
Authorization: Bearer your_api_token
Content-Type: application/json

[
  {
    "command": "Get-Service",
    "timeout": 30
  },
  {
    "command": "Get-ComputerInfo",
    "timeout": 60
  }
]
```

## Güvenlik

- **API Token**: Tüm istekler için Bearer token gerekli
- **Timeout**: Komutlar için maksimum çalışma süresi
- **Working Directory**: Güvenli dizin kontrolü
- **Error Handling**: Hata durumlarında güvenli yanıt

## Örnek Kullanım

### PowerShell Komutları

```bash
# Sistem bilgilerini al
curl -X GET "http://localhost:8000/system/info" \
  -H "Authorization: Bearer your_token"

# Process listesi al
curl -X POST "http://localhost:8000/execute" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"command": "Get-Process | Select-Object Name,Id,CPU"}'

# Disk kullanımını kontrol et
curl -X POST "http://localhost:8000/execute" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"command": "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID,Size,FreeSpace"}'
```

## Yapılandırma

### Environment Variables

| Değişken | Açıklama | Varsayılan |
|-----------|----------|------------|
| `API_TOKEN` | API güvenlik token'ı | `default_token` |
| `HOST` | Sunucu host adresi | `0.0.0.0` |
| `PORT` | Sunucu port numarası | `8000` |
| `LOG_LEVEL` | Log seviyesi | `INFO` |
| `DEFAULT_TIMEOUT` | Varsayılan timeout (saniye) | `30` |
| `MAX_TIMEOUT` | Maksimum timeout (saniye) | `300` |

## Geliştirme

### Proje Yapısı

```
dexagents/
├── app.py              # Ana FastAPI uygulaması
├── requirements.txt    # Python bağımlılıkları
├── env.example        # Environment variables örneği
├── README.md          # Dokümantasyon
└── .vscode/          # VS Code ayarları
```

### Test Etme

```bash
# Sunucuyu başlat
python app.py

# Başka bir terminal'de test et
curl http://localhost:8000/
```

## Lisans

MIT License 