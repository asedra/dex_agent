# DexAgents - Windows Endpoint Management Platform

Modern Windows sistemleri için kapsamlı uzak yönetim ve PowerShell komut çalıştırma platformu. Real-time WebSocket tabanlı PowerShell execution, gelişmiş sistem monitoring ve Docker desteği ile güçlendirilmiştir.

![DexAgents Dashboard](https://img.shields.io/badge/Platform-Windows-blue) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green) ![Next.js](https://img.shields.io/badge/Frontend-Next.js-black) ![Docker](https://img.shields.io/badge/Deploy-Docker-blue)

## 📋 Sistem Gereksinimleri

### 🐳 Docker ile Kurulum (Önerilen)
- **Docker**: 20.10+ ve **Docker Compose**: 2.0+
- **Git**: 2.20+
- **Port Erişimi**: 3000 (Frontend), 8080 (Backend)
- **RAM**: Minimum 2GB, Önerilen 4GB+
- **Depolama**: Minimum 10GB boş alan

### 💻 Manuel Kurulum Gereksinimleri
#### Backend Gereksinimleri
- **Python**: 3.9+ (3.11 önerilen)
- **pip**: 21.0+
- **SQLite**: 3.35+ (veritabanı için)

#### Frontend Gereksinimleri  
- **Node.js**: 18.0+ (20.x önerilen)
- **npm**: 8.0+ veya **pnpm**: 7.0+

#### Agent Gereksinimleri (Windows)
- **Windows**: 10/11 veya Windows Server 2019+
- **PowerShell**: 5.1+ (PowerShell 7+ önerilen)
- **.NET Framework**: 4.7.2+ (GUI agent için)
- **Python**: 3.9+ (Python agent için)

## 🚀 Hızlı Başlangıç

### 🐳 Docker ile Kurulum (Önerilen)

#### 1. Gerekli Araçları Kontrol Edin
```bash
# Docker versiyonunu kontrol et
docker --version
docker-compose --version

# Git versiyonunu kontrol et
git --version
```

#### 2. Projeyi Klonlayın
```bash
git clone https://github.com/asedra/dex_agent.git
cd dex_agent
```

#### 3. Docker Servisleri Başlatın
```bash
# Tüm servisleri arka planda başlat
docker-compose up -d --build

# Servislerin durumunu kontrol et
docker-compose ps

# Logları takip et (isteğe bağlı)
docker-compose logs -f
```

#### 4. Servislere Erişim
- **🌐 Web Dashboard**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8080
- **📚 API Dokumentasyonu**: http://localhost:8080/docs
- **📊 Health Check**: http://localhost:8080/api/v1/system/health

#### 5. Servis Durumunu Doğrulayın
```bash
# Backend health check
curl http://localhost:8080/api/v1/system/health

# Frontend health check  
curl http://localhost:3000/api/health

# Container durumları
docker-compose ps
```

### 💻 Manuel Kurulum

#### Backend Kurulumu
```bash
# Backend dizinine geçin
cd backend

# Python sanal ortam oluşturun
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS  
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install --upgrade pip
pip install -r requirements.txt

# Veritabanını başlatın
python -c "from app.core.database import db_manager; db_manager.create_tables()"

# Sunucuyu başlatın
python run.py
```

#### Frontend Kurulumu
```bash
# Frontend dizinine geçin (yeni terminal)
cd frontend

# Node bağımlılıklarını yükleyin
npm install
# veya pnpm kullanıyorsanız
pnpm install

# Development sunucusunu başlatın
npm run dev
# veya
pnpm dev
```

#### Production Kurulumu
```bash
# Backend için Gunicorn kullanın
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend build ve başlatma
cd frontend
npm run build
npm start
```

## 🏗️ Proje Mimarisi

```
dexagents/
├── backend/                    # FastAPI Backend Server
│   ├── app/
│   │   ├── api/v1/            # REST API Endpoints
│   │   │   ├── agents.py      # Agent yönetimi
│   │   │   ├── commands.py    # PowerShell komutları
│   │   │   ├── installer.py   # Agent installer
│   │   │   ├── system.py      # Sistem bilgileri
│   │   │   └── websocket.py   # WebSocket endpoints
│   │   ├── core/              # Çekirdek modüller
│   │   │   ├── config.py      # Konfigürasyon
│   │   │   ├── database.py    # SQLite veritabanı (Enhanced)
│   │   │   ├── auth.py        # Authentication
│   │   │   └── websocket_manager.py # WebSocket yönetimi
│   │   ├── models/            # 🆕 Database modelleri
│   │   │   ├── agent.py       # Agent veri modeli
│   │   │   ├── user.py        # User modeli
│   │   │   ├── command.py     # Komut geçmişi
│   │   │   ├── group.py       # Agent grupları
│   │   │   ├── alert.py       # Sistem uyarıları
│   │   │   ├── metric.py      # Performans metrikleri
│   │   │   ├── audit.py       # Audit logları
│   │   │   ├── session.py     # Oturum yönetimi
│   │   │   └── task.py        # Zamanlanmış görevler
│   │   ├── migrations/        # 🆕 Database migration sistemi
│   │   │   ├── migration_manager.py
│   │   │   ├── v001_initial_schema.py
│   │   │   └── v002_add_indexes.py
│   │   ├── schemas/           # Pydantic şemaları
│   │   ├── services/          # İş mantığı servisleri
│   │   └── main.py            # Ana uygulama
│   ├── Dockerfile             # 🆕 Docker yapılandırması
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Server başlatma
├── frontend/                  # Next.js 15 Frontend
│   ├── app/                   # Next.js App Router
│   │   ├── agents/            # Agent yönetimi sayfaları
│   │   ├── powershell/        # PowerShell komut arayüzü
│   │   ├── schedules/         # Zamanlanmış görevler
│   │   ├── audit/             # Audit log görüntüleyici
│   │   └── settings/          # Sistem ayarları
│   ├── components/            # React bileşenleri
│   │   ├── ui/                # shadcn/ui komponenları
│   │   ├── app-sidebar.tsx    # Ana navigasyon
│   │   ├── error-boundary.tsx # Hata yakalama
│   │   └── theme-provider.tsx # Tema yönetimi
│   ├── lib/                   # Utility fonksiyonları
│   │   ├── api.ts             # API client
│   │   └── utils.ts           # Yardımcı fonksiyonlar
│   ├── Dockerfile             # 🆕 Docker yapılandırması
│   ├── package.json           # Node.js dependencies
│   └── next.config.mjs        # Next.js yapılandırması
├── agent/                     # Windows Agent Uygulamaları
│   ├── agent_gui.py           # Modern Tkinter GUI
│   ├── modern_agent_gui.py    # Enhanced GUI versiyonu
│   ├── websocket_agent.py     # WebSocket client
│   ├── config_manager.py      # Konfigürasyon yönetimi
│   ├── logger.py              # Log sistemi
│   ├── build_exe.py           # EXE build script
│   └── requirements.txt       # Agent dependencies
├── docker-compose.yml         # 🆕 Docker Compose yapılandırması
├── docker-compose.prod.yml    # 🆕 Production yapılandırması
├── nginx/                     # 🆕 Nginx reverse proxy
└── scripts/                   # 🆕 Deployment scriptleri
```

## 🆕 Yeni Özellikler (v3.3)

### ⚡ Production-Ready Command Library
- **Command Library**: Kayıtlı PowerShell komutlarının yönetimi ve çalıştırılması
- **Real-time Command Execution**: WebSocket üzerinden PowerShell komutlarının anlık çalıştırılması
- **Agent Selection**: Çoklu agent seçimi ve paralel komut çalıştırma
- **JSON Response Display**: PowerShell komut sonuçlarının JSON formatında görüntülenmesi
- **Parameter Support**: Dinamik parametre girişi ve template sistemi
- **System Commands**: Get System Information, Check Disk Space, Get Network Configuration

### 🔧 Advanced PowerShell Features
- **Interactive Command Management**: Komut oluşturma, düzenleme ve silme arayüzü
- **Edit Button Functionality**: Kullanıcı komutlarının tam düzenleme desteği
- **Category Filtering**: System, Network, Disk, Security, Monitoring kategorileri
- **Real-time Agent Status**: Online agent'ların anlık görüntülenmesi
- **Execution Results**: Detaylı komut sonuçları ve hata raporlama
- **Array/List Support**: PowerShell array sonuçlarının tam desteği

### 🔄 Production-Grade Error Handling
- **WebSocket Message Parsing**: String ve Dict message formatlarının otomatik işlenmesi
- **PowerShell Data Type Support**: Array, Object, String tüm data tiplerinin desteği
- **Robust Result Processing**: Gelişmiş komut sonucu işleme ve hata yakalama
- **Safe Property Access**: Undefined değerler için güvenli erişim
- **Detailed Error Messages**: Kullanıcı dostu hata mesajları
- **Timeout Management**: Komut zaman aşımı ve yeniden deneme mantığı

### 🗄️ Enhanced Database Schema
- **10 Tablo**: agents, users, groups, metrics, alerts, audit_logs, sessions, scheduled_tasks, command_history
- **Migration Sistemi**: Version kontrolü ile database şeması yönetimi
- **Model Sınıfları**: Tam ORM benzeri veri modelleri
- **Index Optimizasyonu**: Performans için optimize edilmiş indexler
- **Audit Logging**: Tüm sistem aktivitelerinin kaydı
- **Session Management**: Güvenli kullanıcı oturum yönetimi

### 🐳 Docker Support
- **Multi-stage Builds**: Optimize edilmiş Docker imajları
- **Health Checks**: Container sağlık kontrolü
- **Volume Management**: Persistent data depolama
- **Network Isolation**: Güvenli container iletişimi
- **Production Ready**: Nginx reverse proxy ile production deployment

### 📊 Advanced Monitoring
- **Real-time System Health**: CPU, memory, disk, network monitoring
- **Alert System**: Sistem uyarıları ve bildirimler
- **Service Monitoring**: Windows services durumu izleme
- **Process Tracking**: Top processes ve kaynak kullanımı
- **Historical Data**: Geçmiş metrik verileri

### 🔐 Enhanced Security
- **User Management**: Kullanıcı hesapları ve roller
- **Session Security**: Güvenli oturum yönetimi
- **Audit Trail**: Tüm işlemlerin audit kaydı
- **API Authentication**: Token bazlı güvenlik

## 🔧 Geliştirme Ortamı

### Local Development (Python/Node)
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python run.py

# Frontend
cd frontend
npm install
npm run dev
```

### Docker Development
```bash
# Development ortamında çalıştır
docker-compose up -d

# Logları takip et
docker-compose logs -f

# Servis durumunu kontrol et
docker-compose ps
```

## 📦 Database Schema

### 🗃️ Ana Tablolar

#### **agents** - Agent bilgileri
```sql
- id (TEXT PRIMARY KEY)
- hostname (TEXT NOT NULL)
- ip, os, version, status
- last_seen, tags, system_info
- connection_id, is_connected
- created_at, updated_at
```

#### **users** - Kullanıcı yönetimi
```sql
- id (INTEGER PRIMARY KEY)
- username, email (UNIQUE)
- password_hash, is_active, is_admin
- created_at, updated_at
```

#### **agent_metrics** - Performans metrikleri
```sql
- id (INTEGER PRIMARY KEY)
- agent_id (FOREIGN KEY)
- cpu_usage, memory_usage, disk_usage
- network_in, network_out, process_count
- timestamp
```

#### **alerts** - Sistem uyarıları
```sql
- id (INTEGER PRIMARY KEY)
- agent_id (FOREIGN KEY)
- alert_type, severity, message
- details, is_resolved, resolved_at
- created_at
```

#### **audit_logs** - Sistem audit kayıtları
```sql
- id (INTEGER PRIMARY KEY)
- user_id (FOREIGN KEY)
- action, resource_type, resource_id
- details, ip_address, user_agent
- timestamp
```

## 🚀 Deployment

### Production Docker Deployment
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d --build

# SSL sertifikası için
# nginx/ssl/ klasörüne sertifikalarınızı koyun

# Reverse proxy ile:
# Frontend: https://yourdomain.com
# API: https://yourdomain.com/api
```

### Manual Production Deployment
```bash
# Backend
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
npm start
```

## 🔄 API Endpoints (v1)

### 🖥️ Agent Management
```http
GET    /api/v1/agents                    # Agent listesi
POST   /api/v1/agents/register           # Agent kayıt
GET    /api/v1/agents/{id}               # Agent detayı
PUT    /api/v1/agents/{id}               # Agent güncelle
DELETE /api/v1/agents/{id}               # Agent sil
GET    /api/v1/agents/connected          # Aktif agent'lar
POST   /api/v1/agents/{id}/command       # Komut çalıştır
GET    /api/v1/agents/{id}/metrics       # Agent metrikleri
GET    /api/v1/agents/{id}/alerts        # Agent uyarıları
```

### 👥 User Management
```http
POST   /api/v1/users/register            # Kullanıcı kayıt
POST   /api/v1/users/login               # Giriş yap
POST   /api/v1/users/logout              # Çıkış yap
GET    /api/v1/users/profile             # Profil bilgisi
PUT    /api/v1/users/profile             # Profil güncelle
```

### 📊 Monitoring
```http
GET    /api/v1/metrics                   # Sistem metrikleri
GET    /api/v1/alerts                    # Aktif uyarılar
POST   /api/v1/alerts/{id}/resolve       # Uyarı çöz
GET    /api/v1/audit                     # Audit logları
```

### 🔌 WebSocket Endpoints
```http
WS     /api/v1/ws/agent                  # Agent registration ve command WebSocket
WS     /api/v1/ws/dashboard              # Dashboard real-time updates
```

### ⚡ PowerShell Integration
```http
GET    /api/v1/commands/saved            # Kayıtlı PowerShell komutları
POST   /api/v1/commands/saved            # Yeni PowerShell komutu oluştur
POST   /api/v1/commands/saved/{id}/execute # Kayıtlı komutu çalıştır
GET    /api/v1/agents/{id}/result/{cmd_id} # Komut sonucunu al
POST   /api/v1/agents/{id}/refresh       # System info PowerShell refresh
POST   /api/v1/installer/create-python   # Updated Python agent download
GET    /api/v1/installer/config          # Agent configuration
```

## 🛠️ Agent Features

### ⚡ PowerShell-Enabled Python Agent (v2.1)
- **WebSocket PowerShell Integration**: Real-time PowerShell komut çalıştırma
- **Comprehensive System Monitoring**: CPU name, services, processes, network adapters
- **JSON Response Handling**: PowerShell çıktılarının structured data olarak işlenmesi
- **Smart Error Handling**: Gelişmiş hata yakalama ve raporlama
- **Fallback System**: PowerShell hatası durumunda psutil fallback
- **Auto-reconnection**: Bağlantı kopması durumunda otomatik yeniden bağlanma

### 🖥️ Modern GUI Agent (Legacy)
- **Tkinter tabanlı modern arayüz**
- **Real-time sistem monitoring**
- **WebSocket bağlantısı**
- **Configuration management**
- **Auto-start ve service desteği**
- **Log viewer entegrasyonu**

### 📱 Multiple Agent Versions
- **PowerShell Python Agent**: En güncel, PowerShell desteği ile (Önerilen)
- **Modern GUI Agent**: Gelişmiş GUI ve özellikler
- **Simple Agent**: Temel özellikler
- **Headless Agent**: GUI olmadan çalışan versiyon

### 🔄 PowerShell WebSocket Protocol

#### Agent → Backend Communication
```json
{
  "type": "register",
  "data": {
    "id": "agent-hostname-agentname",
    "hostname": "DESKTOP-PC",
    "system_info": { /* psutil data */ }
  }
}
```

#### Backend → Agent PowerShell Commands
```json
{
  "type": "powershell_command",
  "request_id": "ps_123456789_abc123",
  "command": "Get-ComputerInfo | ConvertTo-Json",
  "timeout": 30
}
```

#### Agent → Backend PowerShell Response
```json
{
  "type": "powershell_result",
  "request_id": "ps_123456789_abc123",
  "data": {
    "TotalPhysicalMemory": 17179869184,
    "CsProcessors": ["Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz"],
    "WindowsVersion": "10.0.19042"
  },
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Command Library Execution
```json
{
  "command_id": "189b3c17-8eee-478b-8729-745d83c4cc35",
  "executed_command": "Get-WmiObject Win32_LogicalDisk | ConvertTo-Json",
  "results": [
    {
      "agent_id": "desktop-pc-agent",
      "command_id": "ps_1234567890_xyz789",
      "status": "sent"
    }
  ]
}
```

## 🔐 Security Features

### 🛡️ Authentication & Authorization
- JWT token bazlı authentication
- Role-based access control (RBAC)
- Session management
- API key authentication

### 🔒 Security Headers
- CORS protection
- Rate limiting
- Input validation
- SQL injection protection

### 📝 Audit Logging
- Tüm API çağrıları loglanır
- User actions kaydedilir
- System events izlenir
- Compliance reporting

## 📊 Monitoring & Alerting

### 📈 Real-time Metrics Collection
- CPU, Memory, Disk usage
- Network traffic
- Process monitoring
- Service status

### 🚨 Alert System
- Threshold-based alerts
- Custom alert rules
- Email/SMS notifications
- Alert escalation

### 📋 Dashboards
- Real-time system overview
- Historical trend analysis
- Performance analytics
- Capacity planning

## 🧪 Testing

### Unit Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Integration Tests
```bash
# API integration tests
cd backend
python -m pytest tests/integration/

# E2E tests
cd frontend
npm run test:e2e
```

## 🐛 Troubleshooting & Yaygın Problemler

### 🚀 Kurulum Problemleri

#### Docker Kurulum Sorunları
```bash
# Docker servisini kontrol et
sudo systemctl status docker

# Docker daemon çalışmıyor ise
sudo systemctl start docker

# Docker Compose eksik ise
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Docker compose versiyonu kontrol et
docker-compose --version
```

#### Port Çakışması Problemleri
```bash
# Portları kontrol et
netstat -tulpn | grep ":3000\|:8080"

# Port kullanan processleri sonlandır
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8080 | xargs kill -9

# Alternatif portlarla başlat
# docker-compose.yml'de port mapping'i değiştirin:
# ports: ["3001:3000", "8081:8000"]
```

#### Yetki ve İzin Problemleri
```bash
# Docker grubuna kullanıcı ekle
sudo usermod -aG docker $USER
newgrp docker

# Proje dizini izinleri
sudo chown -R $USER:$USER /path/to/dex_agent
chmod -R 755 /path/to/dex_agent
```

### 🔄 Servis Çalışma Problemleri

#### Backend Başlamıyor
```bash
# Backend container loglarını kontrol et
docker-compose logs backend

# Container'ı yeniden başlat  
docker-compose restart backend

# Dependencies problemi varsa
docker-compose down
docker-compose up -d --build --force-recreate

# Manuel test için
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python run.py
```

#### Frontend Başlamıyor
```bash
# Frontend container loglarını kontrol et
docker-compose logs frontend

# Node modules problemi
docker exec -it dexagents-frontend-dev rm -rf node_modules
docker exec -it dexagents-frontend-dev npm install

# Manuel test için
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### Database Bağlantı Problemleri
```bash
# SQLite database dosyasını kontrol et
ls -la backend/data/

# Database migration çalıştır
docker exec -it dexagents-backend-dev python -c "
from app.core.database import db_manager
db_manager.create_tables()
print('Database tables created successfully')
"

# Database'i sıfırla
docker-compose down -v
rm -rf backend/data/dexagents.db
docker-compose up -d --build
```

### 🔌 Agent Bağlantı Problemleri

#### Agent Bağlanamıyor
```bash
# Agent log dosyasını kontrol et (Windows agent dizininde)
type agent.log

# WebSocket bağlantısını test et
# Browser developer tools > Network > WS sekmesi

# Firewall kontrolü (Windows)
netsh advfirewall firewall show rule name="DexAgent"

# Firewall kuralı ekle
netsh advfirewall firewall add rule name="DexAgent" dir=in action=allow protocol=TCP localport=8080
```

#### PowerShell Komutları Çalışmıyor
```bash
# PowerShell execution policy kontrol et (Windows)
Get-ExecutionPolicy -List

# Execution policy değiştir
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Agent PowerShell versiyonu
$PSVersionTable.PSVersion

# Backend loglarında PowerShell komutlarını takip et
docker-compose logs backend | grep "powershell_command\|PowerShell\|powershell_result"
```

#### Agent Registration Problemleri
```bash
# API token kontrolü
curl -H "Authorization: Bearer your-secret-key-here" \
     "http://localhost:8080/api/v1/agents/"

# Agent konfigürasyon dosyası (agent/config.json)
{
  "server_url": "http://localhost:8080",
  "api_token": "your-secret-key-here",
  "agent_name": "MyAgent",
  "auto_reconnect": true
}
```

### 🌐 Network ve API Problemleri

#### API Erişim Problemleri
```bash
# API health check
curl http://localhost:8080/api/v1/system/health

# CORS hatası varsa backend loglarını kontrol et
docker-compose logs backend | grep "CORS"

# API dokumentasyonuna erişim
curl http://localhost:8080/docs
```

#### WebSocket Bağlantı Problemleri
```bash
# WebSocket endpoint test
wscat -c ws://localhost:8080/api/v1/ws/agent

# Proxy arkasında çalışma
# nginx.conf'ta WebSocket upgrade ayarları:
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### 🐳 Docker Özel Problemleri

#### Container Build Hataları
```bash
# Build cache temizle
docker system prune -a

# Specific container rebuild
docker-compose build --no-cache backend
docker-compose build --no-cache frontend

# Build log detayları
docker-compose build --progress=plain
```

#### Volume ve Data Problemleri
```bash
# Volume'ları listele
docker volume ls

# Volume'ları temizle
docker-compose down -v
docker volume prune

# Data persist problemleri
ls -la backend/data/
sudo chown -R 1000:1000 backend/data/
```

#### Memory ve Resource Problemleri
```bash
# Container resource kullanımı
docker stats

# Memory limit ayarla (docker-compose.yml)
mem_limit: 1g
memswap_limit: 2g

# Disk space kontrolü
df -h
docker system df
```

### 🔧 Development Ortamı Problemleri

#### Hot Reload Çalışmıyor
```bash
# Frontend hot reload
# Volume mapping kontrol et:
# volumes: ["./frontend:/app", "/app/node_modules"]

# Backend hot reload için
# uvicorn --reload kullanıldığından emin ol

# File watching limitlerini artır (Linux)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### IDE ve Debug Problemleri
```bash
# VSCode container attach
# Remote-Containers extension kullan

# Debug port açma (docker-compose.yml)
ports:
  - "5678:5678"  # Python debugger
  - "9229:9229"  # Node.js debugger
```

### 📊 Performance Problemleri

#### Yavaş API Response
```bash
# Backend performans logları
docker-compose logs backend | grep -E "INFO|ERROR|WARNING"

# Database query optimizasyonu
# SQLite ANALYZE komutunu çalıştır

# Resource monitoring
docker stats dexagents-backend-dev
docker stats dexagents-frontend-dev
```

#### High Memory/CPU Usage
```bash
# Resource limits ayarla
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      memory: 1G
```

### 🆘 Acil Durum Çözümleri

#### Tamamen Temiz Başlangıç
```bash
# Her şeyi temizle ve yeniden başlat
docker-compose down -v --remove-orphans
docker system prune -a
rm -rf backend/data/
git pull origin main
docker-compose up -d --build --force-recreate
```

#### Log Collection Script
```bash
#!/bin/bash
# debug-collect.sh
echo "=== DexAgents Debug Information ===" > debug.log
date >> debug.log
echo "" >> debug.log

echo "=== Docker Info ===" >> debug.log
docker --version >> debug.log
docker-compose --version >> debug.log
echo "" >> debug.log

echo "=== Container Status ===" >> debug.log
docker-compose ps >> debug.log
echo "" >> debug.log

echo "=== Backend Logs ===" >> debug.log
docker-compose logs --tail=100 backend >> debug.log
echo "" >> debug.log

echo "=== Frontend Logs ===" >> debug.log
docker-compose logs --tail=100 frontend >> debug.log
echo "" >> debug.log

echo "=== System Resources ===" >> debug.log
docker stats --no-stream >> debug.log

echo "Debug bilgileri debug.log dosyasına kaydedildi"
```

### Agent Connection Issues
```bash
# Agent log dosyasını kontrol edin (agent.log)
# - "Processing message type: powershell_command" mesajı görüyor musunuz?
# - "Unknown message type: powershell_command" görüyorsanız agent güncel değil

# Yeni PowerShell-enabled agent indirin
curl -X POST -H "Authorization: Bearer your-secret-key-here" \
     -H "Content-Type: application/json" \
     -d '{"server_url":"http://localhost:8080","api_token":"your-secret-key-here","agent_name":"UpdatedAgent","tags":["v2.1"],"auto_start":true,"run_as_service":false}' \
     "http://localhost:8080/api/v1/installer/create-python" \
     --output updated_agent.zip
```

### Docker Issues
```bash
# Container loglarını kontrol et
docker-compose logs backend
docker-compose logs frontend

# Container'ları yeniden başlat
docker-compose restart

# Volume'ları temizle
docker-compose down -v
docker-compose up -d --build
```

### Database Issues
```bash
# Database migration çalıştır
docker exec -it dexagents-backend-dev python -c "from app.migrations.migration_manager import MigrationManager; MigrationManager('/app/dexagents.db').run_migrations()"

# Database'i sıfırla
docker-compose down -v
docker-compose up -d --build
```

### Network Issues
```bash
# Port kontrolü
netstat -tulpn | grep :8080
netstat -tulpn | grep :3000

# Firewall kontrolü
sudo ufw status
```

## 📈 Performance Optimization

### Database Optimization
- Index optimization
- Query performance tuning
- Connection pooling
- Lazy loading

### Frontend Optimization
- Code splitting
- Image optimization
- Caching strategies
- Bundle size optimization

### Backend Optimization
- Async/await usage
- Memory management
- Response compression
- Database query optimization

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: docker-compose -f docker-compose.test.yml up --abort-on-container-exit
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml up -d --build
```

## 📊 System Requirements

### Minimum Requirements
- **RAM**: 2GB
- **Storage**: 10GB
- **CPU**: 2 cores
- **OS**: Linux/Windows/macOS (Docker)

### Recommended Requirements
- **RAM**: 4GB+
- **Storage**: 50GB+
- **CPU**: 4+ cores
- **OS**: Linux (Production)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Code Standards
- **Python**: PEP 8, Type hints, Docstrings
- **TypeScript**: ESLint, Prettier
- **React**: Hooks, Functional components
- **Docker**: Multi-stage builds, Security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/asedra/dex_agent/issues)
- **Documentation**: [Wiki](https://github.com/asedra/dex_agent/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/asedra/dex_agent/discussions)

---

**DexAgents** - Modern Windows Endpoint Management Platform v3.3

🚀 **Ready for Production** | ⭐ **Star this repo** | 🐛 **Report issues**