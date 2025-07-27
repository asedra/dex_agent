# DexAgents - Endpoint Management Platform

DexAgents, Windows sistemlerinde PowerShell komutlarını uzaktan çalıştırmak ve sistem agent'larını yönetmek için geliştirilmiş bir platformdur.

## 📁 Proje Yapısı

```
dexagents/
├── backend/           # FastAPI Backend Server
│   ├── app.py        # Ana server uygulaması
│   ├── database.py   # SQLite veritabanı işlemleri
│   ├── debug_agents.py # Test agent'ları
│   ├── requirements.txt # Python dependencies
│   └── start_server.py # Server başlatma script'i
├── frontend/         # Next.js Frontend
│   ├── app/          # Next.js 14 app router
│   ├── components/   # React components
│   ├── lib/          # Utility functions
│   ├── package.json  # Node.js dependencies
│   └── start_frontend.py # Frontend başlatma script'i
└── agent/            # Windows Agent (GUI)
    ├── agent_gui.py  # Tkinter GUI uygulaması
    ├── requirements.txt # Agent dependencies
    ├── build_exe.py  # EXE build script'i
    └── DexAgentsAgent.exe # Oluşturulan executable
```

## 🚀 Hızlı Başlangıç

### 1. Backend Server'ı Başlat

```bash
cd backend
python start_server.py
```

Backend server http://localhost:8000 adresinde çalışacak.

### 2. Frontend'i Başlat

```bash
cd frontend
python start_frontend.py
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

## 🔧 Agent EXE Oluşturma

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

## 📦 Agent Kurulum Paketi

`DexAgents_Installer.zip` içeriği:
- `DexAgentsAgent.exe` - Ana agent uygulaması
- `config.json` - Varsayılan konfigürasyon
- `README.txt` - Kurulum talimatları

## 🎯 Özellikler

### Backend (FastAPI)
- ✅ REST API endpoints
- ✅ SQLite veritabanı
- ✅ Agent yönetimi
- ✅ PowerShell komut çalıştırma
- ✅ Installer paketi oluşturma
- ✅ Token tabanlı authentication

### Frontend (Next.js)
- ✅ Modern React UI
- ✅ Agent listesi ve detayları
- ✅ Quick Actions (PowerShell komutları)
- ✅ Agent download menüsü
- ✅ Real-time status güncellemeleri
- ✅ Responsive tasarım

### Agent (GUI)
- ✅ Tkinter tabanlı GUI
- ✅ Connection ayarları
- ✅ Real-time system monitoring
- ✅ Log görüntüleme
- ✅ Web interface entegrasyonu
- ✅ Config kaydetme/yükleme

## 🔐 Güvenlik

- API token tabanlı authentication
- PowerShell komut çalıştırma güvenliği
- Agent registration kontrolü
- Log dosyaları ile audit trail

## 📊 Monitoring

### System Metrics
- CPU kullanımı
- Memory kullanımı
- Disk kullanımı
- Network durumu

### Agent Status
- Online/Offline durumu
- Son görülme zamanı
- Connection durumu
- Error logları

## 🛠️ Geliştirme

### Backend Geliştirme
```bash
cd backend
pip install -r requirements.txt
python app.py
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

## 📝 API Endpoints

### Agents
- `GET /api/agents` - Agent listesi
- `POST /api/agents/register` - Agent kayıt
- `GET /api/agents/{agent_id}` - Agent detayı
- `POST /api/agents/{agent_id}/command` - Komut çalıştır

### Installer
- `GET /api/installer/config` - Varsayılan config
- `POST /api/installer/create` - Installer oluştur

## 🔄 Workflow

1. **Backend başlat** → Server API'si aktif
2. **Frontend başlat** → Web interface erişilebilir
3. **Agent çalıştır** → Sistem monitoring başlar
4. **Web interface'den** → Agent'ları yönet
5. **Quick Actions** → PowerShell komutları çalıştır

## 🐛 Troubleshooting

### Backend Sorunları
- Port 8000 kullanımda mı kontrol et
- Python dependencies yüklü mü kontrol et
- SQLite database dosyası yazılabilir mi kontrol et

### Frontend Sorunları
- Node.js yüklü mü kontrol et
- Port 3000 kullanımda mı kontrol et
- npm dependencies yüklü mü kontrol et

### Agent Sorunları
- Server URL doğru mu kontrol et
- API token geçerli mi kontrol et
- Firewall ayarları kontrol et
- Log dosyalarını kontrol et

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