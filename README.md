# DexAgents - Windows Endpoint Management Platform

DexAgents, Windows sistemlerinde PowerShell komutlarını uzaktan çalıştırmak ve sistem agent'larını yönetmek için geliştirilmiş modern bir platformdur. Backend, Frontend ve Agent olmak üzere üç ana bileşenden oluşur.

## 🏗️ Proje Mimarisi

```
dexagents/
├── backend/           # FastAPI Backend Server
│   ├── app/          # Ana uygulama modülü
│   │   ├── api/      # API endpoint'leri
│   │   │   └── v1/   # API v1 endpoint'leri
│   │   │       ├── agents.py      # Agent yönetimi
│   │   │       ├── commands.py    # PowerShell komutları
│   │   │       ├── installer.py   # Installer yönetimi
│   │   │       └── system.py      # Sistem bilgileri
│   │   ├── core/     # Çekirdek modüller
│   │   │   ├── config.py          # Konfigürasyon
│   │   │   ├── database.py        # Veritabanı işlemleri
│   │   │   └── auth.py            # Kimlik doğrulama
│   │   ├── schemas/  # Pydantic modelleri
│   │   │   ├── agent.py           # Agent şemaları
│   │   │   ├── command.py         # Komut şemaları
│   │   │   └── system.py          # Sistem şemaları
│   │   ├── services/ # İş mantığı servisleri
│   │   │   ├── powershell_service.py    # PowerShell servisi
│   │   │   └── agent_installer_service.py # Installer servisi
│   │   └── main.py   # Ana uygulama girişi
│   ├── tests/        # Test dosyaları
│   │   └── test_api.py
│   ├── requirements.txt # Python dependencies
│   ├── run.py        # Server başlatma script'i
│   ├── env.example   # Environment variables örneği
│   ├── .gitignore    # Git ignore dosyası
│   └── README.md     # Backend dokümantasyonu
├── frontend/         # Next.js Frontend
│   ├── app/          # Next.js 14 app router
│   │   ├── agents/   # Agent sayfaları
│   │   ├── powershell/ # PowerShell sayfası
│   │   ├── schedules/ # Zamanlanmış görevler
│   │   └── audit/    # Audit logları
│   ├── components/   # React components
│   │   └── ui/       # shadcn/ui bileşenleri
│   ├── lib/          # Utility functions
│   │   └── api.ts    # API client
│   ├── package.json  # Node.js dependencies
│   └── next.config.mjs # Next.js konfigürasyonu
├── agent/            # Windows Agent (GUI)
│   ├── agent_gui.py  # Tkinter GUI uygulaması
│   ├── requirements.txt # Agent dependencies
│   ├── build_exe.py  # EXE build script'i
│   ├── config.json   # Agent konfigürasyonu
│   ├── DexAgents_Installer.zip # Kurulum paketi
│   ├── DexAgents_Installer/ # Kurulum klasörü
│   │   ├── DexAgentsAgent.exe # Ana executable
│   │   ├── config.json # Varsayılan konfigürasyon
│   │   └── README.txt # Kurulum talimatları
│   └── logs/         # Log dosyaları
├── README.md         # Bu dosya
└── .gitignore        # Git ignore dosyası
```

## 🚀 Hızlı Başlangıç

### Gereksinimler
- **Python 3.11+**
- **Node.js 18+**
- **Windows 10/11**
- **PowerShell 5.1+**

### 1. Backend Server'ı Başlat

```bash
cd backend
pip install -r requirements.txt
python run.py
```

Backend server http://localhost:8000 adresinde çalışacak.

### 2. Frontend'i Başlat

```bash
cd frontend
npm install
npm run dev
```

Frontend http://localhost:3000 adresinde çalışacak.

### 3. Agent'ı Çalıştır

```bash
cd agent
python agent_gui.py
```

Veya executable'ı çalıştır:
```bash
cd agent
DexAgentsAgent.exe
```

## 🔧 Geliştirme Ortamı

### Backend Geliştirme
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend Geliştirme
```bash
cd frontend
npm install
npm run dev
```

### Agent Geliştirme
```bash
cd agent
pip install -r requirements.txt
python agent_gui.py
```

## 📦 Agent EXE Oluşturma

Agent'ı executable olarak oluşturmak için:

```bash
cd agent
python build_exe.py
```

Bu işlem:
- Python dependencies'leri yükler
- PyInstaller ile EXE oluşturur
- Kurulum paketi hazırlar
- `DexAgents_Installer.zip` dosyası oluşturur

## 🎯 Bileşen Detayları

### 🔧 Backend (FastAPI)

**Teknolojiler:**
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- SQLite (veritabanı)
- psutil (sistem monitoring)

**Mimari:**
- **Modüler Yapı**: API, Core, Schemas, Services ayrımı
- **Separation of Concerns**: İş mantığı ve API endpoint'leri ayrı
- **Versioned API**: `/api/v1/` prefix ile API versiyonlama
- **Centralized Config**: Merkezi konfigürasyon yönetimi
- **Structured Logging**: Yapılandırılmış log sistemi

**Özellikler:**
- ✅ REST API endpoints (v1)
- ✅ Agent yönetimi (CRUD işlemleri)
- ✅ PowerShell komut çalıştırma
- ✅ Sistem bilgileri toplama
- ✅ Installer paketi oluşturma
- ✅ Token tabanlı authentication
- ✅ Real-time agent monitoring
- ✅ Batch komut çalıştırma
- ✅ Test data seeding

**API Endpoints:**
```
GET  /                    # Health check
GET  /api/v1/agents/     # Agent listesi
POST /api/v1/agents/register # Agent kayıt
GET  /api/v1/agents/{id} # Agent detayı
POST /api/v1/agents/seed # Test data oluştur
POST /api/v1/agents/{id}/command # Komut çalıştır
GET  /api/v1/installer/config # Varsayılan config
POST /api/v1/installer/create # Installer oluştur
GET  /api/v1/system/info # Sistem bilgileri
```

### 🌐 Frontend (Next.js)

**Teknolojiler:**
- Next.js 15.2.4
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Lucide React icons

**Özellikler:**
- ✅ Modern React UI
- ✅ Agent dashboard
- ✅ Quick Actions (PowerShell komutları)
- ✅ Agent download menüsü
- ✅ Real-time status güncellemeleri
- ✅ Responsive tasarım
- ✅ Dark/Light mode
- ✅ Form validasyonu
- ✅ Error handling

**Sayfalar:**
- `/` - Dashboard
- `/agents` - Agent listesi
- `/agents/[id]` - Agent detayı
- `/powershell` - PowerShell komutları
- `/schedules` - Zamanlanmış görevler
- `/audit` - Audit logları

### 🖥️ Agent (GUI)

**Teknolojiler:**
- Tkinter (GUI framework)
- requests (HTTP client)
- psutil (sistem monitoring)
- PyInstaller (EXE oluşturma)

**Özellikler:**
- ✅ Tkinter tabanlı GUI
- ✅ Connection ayarları
- ✅ Real-time system monitoring
- ✅ Log görüntüleme
- ✅ Web interface entegrasyonu
- ✅ Config kaydetme/yükleme
- ✅ Windows service desteği
- ✅ Auto-start seçeneği

**GUI Bileşenleri:**
- Connection Settings (Server URL, API Token, Agent Name, Tags)
- Options (Auto-start, Run as service)
- Status Display (Connection, Agent, CPU, Memory)
- Log Management (Built-in log viewer)
- Action Buttons (Start/Stop, Test Connection, Save Config)

## 🔐 Güvenlik

### Authentication
- Bearer token tabanlı API authentication
- Güvenli token doğrulama
- CORS middleware yapılandırması

### PowerShell Güvenliği
- Komut timeout kontrolü
- Working directory kısıtlaması
- Admin yetki kontrolü
- Hata durumunda güvenli yanıt

### Agent Güvenliği
- Config dosyası şifreleme
- Log dosyası güvenliği
- Network bağlantı güvenliği

## 📊 Monitoring ve Logging

### Sistem Metrikleri
- CPU kullanımı (real-time)
- Memory kullanımı (real-time)
- Disk kullanımı (partition bazında)
- Network durumu
- Process listesi

### Agent Durumu
- Online/Offline durumu
- Son görülme zamanı
- Connection durumu
- Error logları
- Performance metrikleri

### Log Yönetimi
- Backend: Console ve file logging
- Frontend: Browser console logging
- Agent: File-based logging (logs/agent.log)

## 🚀 Deployment

### Production Backend
```bash
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Production Frontend
```bash
cd frontend
npm run build
npm start
```

### Agent Distribution
```bash
cd agent
python build_exe.py
# DexAgents_Installer.zip dosyası oluşturulur
```

## 📦 Agent Kurulum Paketi

**Dosya:** `DexAgents_Installer.zip` (12MB)

**İçerik:**
- `DexAgentsAgent.exe` (12MB) - Ana uygulama
- `config.json` - Varsayılan konfigürasyon
- `README.txt` - Kurulum talimatları

**Kurulum Adımları:**
1. ZIP dosyasını hedef bilgisayara kopyala
2. Dosyayı aç ve içeriğini çıkar
3. `DexAgentsAgent.exe` dosyasını çalıştır
4. Connection ayarlarını yapılandır
5. "Start Agent" butonuna tıkla

## 🔄 Workflow

### 1. Sistem Başlatma
```bash
# Terminal 1: Backend
cd backend && python run.py

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: Agent (opsiyonel)
cd agent && python agent_gui.py
```

### 2. Agent Yönetimi
1. Web interface'den agent'ları görüntüle
2. Agent detaylarını incele
3. Quick Actions ile PowerShell komutları çalıştır
4. Agent download menüsünden installer oluştur

### 3. Monitoring
- Real-time sistem metrikleri
- Agent durumu takibi
- Log dosyaları inceleme
- Performance analizi

## 🐛 Troubleshooting

### Backend Sorunları
- **Port 8000 kullanımda**: `netstat -ano | findstr :8000`
- **Python dependencies**: `pip install -r requirements.txt`
- **Database erişimi**: Dosya yazma izinlerini kontrol et
- **Module import hataları**: `python -m app.main` ile çalıştır

### Frontend Sorunları
- **Node.js yüklü değil**: https://nodejs.org/
- **Port 3000 kullanımda**: `netstat -ano | findstr :3000`
- **npm dependencies**: `npm install`
- **API endpoint hataları**: Backend'in çalıştığından emin ol

### Agent Sorunları
- **Server URL yanlış**: Backend'in çalıştığından emin ol
- **API token geçersiz**: Backend'deki token'ı kontrol et
- **Firewall**: Windows Firewall ayarlarını kontrol et
- **Log dosyaları**: `logs/agent.log` dosyasını incele

## 📝 API Dokümantasyonu

### Agent Endpoints

#### Agent Listesi
```bash
GET /api/v1/agents/
Authorization: Bearer your-secret-key-here
```

#### Agent Kayıt
```bash
POST /api/v1/agents/register
Authorization: Bearer your-secret-key-here
Content-Type: application/json

{
  "hostname": "DESKTOP-ABC123",
  "os": "Windows 10",
  "version": "2.1.4",
  "status": "online",
  "tags": ["windows", "gui-agent"],
  "system_info": {
    "cpu_usage": 25.5,
    "memory_usage": 60.2,
    "disk_usage": {"C:": 75.0}
  }
}
```

#### Test Data Oluşturma
```bash
POST /api/v1/agents/seed
Authorization: Bearer your-secret-key-here
```

#### PowerShell Komut Çalıştırma
```bash
POST /api/v1/agents/{agent_id}/command
Authorization: Bearer your-secret-key-here
Content-Type: application/json

{
  "command": "Get-Process | Select-Object Name,Id,CPU",
  "timeout": 30
}
```

### Installer Endpoints

#### Varsayılan Config
```bash
GET /api/v1/installer/config
Authorization: Bearer your-secret-key-here
```

#### Installer Oluşturma
```bash
POST /api/v1/installer/create
Authorization: Bearer your-secret-key-here
Content-Type: application/json

{
  "server_url": "http://localhost:8000",
  "api_token": "your-secret-key-here",
  "agent_name": "test_agent",
  "tags": ["windows", "test"],
  "auto_start": true,
  "run_as_service": true
}
```

### System Endpoints

#### Sistem Bilgileri
```bash
GET /api/v1/system/info
Authorization: Bearer your-secret-key-here
```

## 🛠️ Geliştirme

### Yeni Endpoint Ekleme
```python
# backend/app/api/v1/new_endpoint.py
from fastapi import APIRouter, Depends
from ...core.auth import verify_token

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint(token: str = Depends(verify_token)):
    return {"message": "New endpoint"}
```

### Yeni Model Ekleme
```python
# backend/app/schemas/new_model.py
from pydantic import BaseModel, Field

class NewModel(BaseModel):
    field: str = Field(..., description="Field description")
```

### Frontend Sayfa Ekleme
```bash
mkdir frontend/app/new-page
touch frontend/app/new-page/page.tsx
```

### API Client'a Method Ekleme
```typescript
// frontend/lib/api.ts
async newMethod(): Promise<any> {
  return this.request('/api/v1/new-endpoint')
}
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 İletişim

Proje hakkında sorularınız için issue açabilirsiniz.

---

**DexAgents** - Windows Endpoint Management Platform v2.1.4 