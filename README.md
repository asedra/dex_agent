# DexAgents - Windows Endpoint Management Platform

Modern Windows sistemleri için kapsamlı uzak yönetim ve PowerShell komut çalıştırma platformu. Docker desteği, gelişmiş veritabanı yönetimi ve real-time monitoring ile güçlendirilmiştir.

![DexAgents Dashboard](https://img.shields.io/badge/Platform-Windows-blue) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green) ![Next.js](https://img.shields.io/badge/Frontend-Next.js-black) ![Docker](https://img.shields.io/badge/Deploy-Docker-blue)

## 🚀 Hızlı Başlangıç (Docker)

### Gereksinimler
- **Docker** ve **Docker Compose**
- **Git**

### 1. Projeyi Klonla
```bash
git clone https://github.com/asedra/dex_agent.git
cd dex_agent
```

### 2. Docker ile Başlat
```bash
docker-compose up -d --build
```

### 3. Servislere Erişim
- **🌐 Web Dashboard**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8080
- **📊 Health Check**: http://localhost:8080/api/v1/system/health

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

## 🆕 Yeni Özellikler (v3.0)

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
- **Agent Metrics**: CPU, memory, disk kullanımı izleme
- **Alert System**: Sistem uyarıları ve bildirimler
- **Performance Tracking**: Gerçek zamanlı performans takibi
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
WS     /api/v1/ws/{agent_id}             # Agent WebSocket
WS     /api/v1/ws/dashboard              # Dashboard WebSocket
```

## 🛠️ Agent Features

### 🖥️ Modern GUI Agent
- **Tkinter tabanlı modern arayüz**
- **Real-time sistem monitoring**
- **WebSocket bağlantısı**
- **Configuration management**
- **Auto-start ve service desteği**
- **Log viewer entegrasyonu**

### 📱 Multiple Agent Versions
- **Simple Agent**: Temel özellikler
- **Modern Agent**: Gelişmiş GUI ve özellikler
- **Headless Agent**: GUI olmadan çalışan versiyon

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

## 🐛 Troubleshooting

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

**DexAgents** - Modern Windows Endpoint Management Platform v3.0

🚀 **Ready for Production** | ⭐ **Star this repo** | 🐛 **Report issues**