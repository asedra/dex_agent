# DexAgents Backend

FastAPI tabanlı Windows PowerShell agent yönetim sistemi.

## 🏗️ Proje Yapısı

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── agents.py
│   │   │   ├── commands.py
│   │   │   ├── installer.py
│   │   │   └── system.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── auth.py
│   ├── schemas/
│   │   ├── agent.py
│   │   ├── command.py
│   │   └── system.py
│   ├── services/
│   │   ├── powershell_service.py
│   │   └── agent_installer_service.py
│   └── main.py
├── tests/
│   └── test_api.py
├── requirements.txt
├── run.py
└── README.md
```

## 🚀 Kurulum

1. **Sanal ortam oluşturun:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # veya
   venv\Scripts\activate     # Windows
   ```

2. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ortam değişkenlerini ayarlayın:**
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyin
   ```

## 🏃‍♂️ Çalıştırma

```bash
python run.py
```

Veya doğrudan uvicorn ile:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Dokümantasyonu

Uygulama çalıştıktan sonra:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Kimlik Doğrulama

API, Bearer token ile korunmaktadır. Tüm korumalı endpoint'ler için Authorization header'ı gereklidir:

```
Authorization: Bearer your-secret-key-here
```

## 📋 Ana Endpoint'ler

### Agents
- `GET /api/v1/agents/` - Tüm agent'ları listele
- `GET /api/v1/agents/{agent_id}` - Belirli agent'ı getir
- `POST /api/v1/agents/` - Yeni agent oluştur
- `PUT /api/v1/agents/{agent_id}` - Agent güncelle
- `DELETE /api/v1/agents/{agent_id}` - Agent sil

### Commands
- `POST /api/v1/commands/execute` - PowerShell komutu çalıştır
- `POST /api/v1/commands/execute/batch` - Birden fazla komut çalıştır

### System
- `GET /api/v1/system/info` - Sistem bilgilerini getir
- `GET /api/v1/system/health` - Sağlık kontrolü

### Installer
- `POST /api/v1/installer/create` - Agent installer oluştur
- `GET /api/v1/installer/config` - Varsayılan installer konfigürasyonu

## 🧪 Testler

```bash
pytest tests/
```

## 📦 Geliştirme

### Yeni Endpoint Ekleme

1. `app/api/v1/` altında yeni router dosyası oluşturun
2. `app/api/__init__.py` dosyasına router'ı ekleyin
3. Gerekli schema'ları `app/schemas/` altında tanımlayın

### Yeni Service Ekleme

1. `app/services/` altında yeni service dosyası oluşturun
2. Business logic'i service katmanında tutun
3. API router'larında sadece HTTP işlemlerini yapın

## 🔧 Konfigürasyon

`app/core/config.py` dosyasında tüm ayarları bulabilirsiniz:

- API ayarları
- Güvenlik ayarları
- CORS ayarları
- Veritabanı ayarları
- PowerShell ayarları

## 📝 Logging

Uygulama, yapılandırılmış logging kullanır. Log seviyesi ve formatı `app/main.py` dosyasında ayarlanabilir.

## 🛡️ Güvenlik

- Tüm endpoint'ler token doğrulaması gerektirir
- CORS ayarları yapılandırılabilir
- Input validation Pydantic ile sağlanır
- SQL injection koruması için parametrized queries kullanılır 