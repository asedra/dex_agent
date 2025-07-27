# DexAgents - Windows PowerShell Agent Management

Modern ve kullanıcı dostu Windows PowerShell komutlarını API üzerinden güvenli şekilde çalıştıran kapsamlı yönetim sistemi.

## 🚀 Özellikler

### Backend (FastAPI)
- 🔐 **Güvenli API**: Bearer token authentication
- ⚡ **Asenkron İşlem**: Hızlı komut çalıştırma
- 🛡️ **Güvenlik**: Timeout ve komut validasyonu
- 📊 **Sistem Bilgileri**: CPU, RAM, disk kullanımı
- 🔄 **Batch İşlemler**: Çoklu komut çalıştırma
- 📝 **Detaylı Loglama**: Komut çalıştırma geçmişi
- 🗄️ **SQLite Database**: Agent verilerinin kalıcı saklanması
- 👥 **Agent Management**: Agent kayıt, güncelleme, silme
- 🔍 **Real System Information**: PowerShell ile gerçek sistem bilgileri
- 📊 **Performance Monitoring**: Gerçek zamanlı CPU, memory, disk izleme
- 🔄 **Live Updates**: Sistem bilgilerini güncelleme

### Frontend (Next.js)
- 🎨 **Modern UI/UX**: Tailwind CSS ve shadcn/ui
- 📱 **Responsive Design**: Tüm cihazlarda mükemmel görünüm
- ⚡ **Real-time Updates**: Gerçek zamanlı sistem bilgileri
- 🔧 **PowerShell Integration**: Komut çalıştırma ve yönetimi
- 👥 **Agent Management**: Agent'ları izleme ve yönetme
- 🌙 **Dark/Light Mode**: Tema desteği

## 🏗️ Proje Yapısı

```
dexagents/
├── app.py                    # FastAPI backend
├── database.py              # SQLite database manager
├── populate_db.py           # Test database population script
├── populate_real_agents.py  # Real system data population script
├── update_real_system_info.py # Real-time system info updater
├── debug_agents.py          # Agent debugging script
├── test_integration.py      # End-to-end integration tests
├── requirements.txt          # Python bağımlılıkları
├── env.example              # Environment variables
├── .env                     # Environment configuration
├── test_client.py           # API test client
├── start.bat               # Windows başlatma scripti
├── dexagents.db            # SQLite database (auto-created)
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js App Router
│   ├── components/        # UI bileşenleri
│   ├── lib/              # Utility fonksiyonları
│   └── package.json      # Node.js bağımlılıkları
└── README.md             # Bu dosya
```

## 🛠️ Teknolojiler

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **psutil**: System monitoring
- **python-dotenv**: Environment variables
- **SQLite**: Lightweight database for agent data

### Frontend
- **Next.js 15**: React framework
- **TypeScript**: Tip güvenliği
- **Tailwind CSS**: Styling
- **shadcn/ui**: UI bileşenleri
- **Lucide React**: İkonlar

## 📦 Kurulum

### Gereksinimler

- Python 3.11+
- Node.js 18+
- Windows 10/11
- PowerShell 5.1+

### Backend Kurulumu

1. **Python bağımlılıklarını yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Environment dosyasını oluşturun:**
```bash
copy env.example .env
```

3. **API token'ını ayarlayın:**
`.env` dosyasında `API_TOKEN` değerini güvenli bir token ile değiştirin.

4. **Database'i gerçek sistem bilgileriyle başlatın:**
```bash
# Gerçek sistem bilgileri ile database'i doldur
python populate_real_agents.py
```

5. **Gerçek zamanlı sistem bilgilerini güncellemek için:**
```bash
# Mevcut sistem agent'ını güncelle
python update_real_system_info.py
```

### Frontend Kurulumu

1. **Frontend klasörüne gidin:**
```bash
cd frontend
```

2. **Node.js bağımlılıklarını yükleyin:**
```bash
pnpm install
```

3. **Environment dosyasını oluşturun:**
```bash
cp .env.example .env.local
```

## 🚀 Çalıştırma

### Hızlı Başlatma (Windows)

```bash
# Backend ve frontend'i birlikte başlat
start.bat
```

### Manuel Başlatma

1. **Backend'i başlatın:**
```bash
python app.py
```

2. **Frontend'i başlatın (yeni terminal):**
```bash
cd frontend
pnpm dev
```

3. **Tarayıcıda açın:**
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 🔧 API Endpoints

### Backend API

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Health check |
| `/api/health` | GET | Frontend health check |
| `/system/info` | GET | Sistem bilgileri |
| `/execute` | POST | Tek komut çalıştırma |
| `/execute/batch` | POST | Çoklu komut çalıştırma |
| `/api/agents` | GET | Tüm agent'ları listele |
| `/api/agents/{id}` | GET | Agent detayları |
| `/api/agents` | POST | Yeni agent oluştur |
| `/api/agents/{id}` | PUT | Agent güncelle |
| `/api/agents/{id}` | DELETE | Agent sil |
| `/api/agents/{id}/commands` | GET | Agent komut geçmişi |
| `/api/agents/{id}/refresh` | POST | Agent bilgilerini gerçek zamanlı güncelle |
| `/api/agents/register` | POST | Mevcut sistemi agent olarak kaydet |

### Örnek Kullanım

```bash
# Sistem bilgilerini al
curl -X GET "http://localhost:8000/system/info" \
  -H "Authorization: Bearer your_token"

# PowerShell komutu çalıştır
curl -X POST "http://localhost:8000/execute" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"command": "Get-Process | Select-Object Name,Id,CPU"}'
```

## 📱 Frontend Sayfaları

### Dashboard (`/`)
- Sistem genel durumu
- Agent istatistikleri
- Hızlı eylemler
- Son aktiviteler

### Agents (`/agents`)
- Agent listesi
- Filtreleme ve arama
- Toplu eylemler
- Detay görüntüleme

### PowerShell Library (`/powershell`)
- Komut kütüphanesi
- Kategori filtreleme
- Komut çalıştırma
- Sonuç görüntüleme

### Agent Details (`/agents/[id]`)
- Agent detayları
- Sistem bilgileri
- Komut geçmişi
- Ayarlar

## 🔒 Güvenlik

### Backend
- **API Token**: Bearer token authentication
- **Timeout**: Komutlar için maksimum çalışma süresi
- **Working Directory**: Güvenli dizin kontrolü
- **Error Handling**: Hata durumlarında güvenli yanıt

### Frontend
- **CORS**: Backend'de yapılandırılmış
- **Input Validation**: Form validasyonu
- **Error Handling**: Güvenli hata yönetimi
- **Environment Variables**: Güvenli konfigürasyon

## 🧪 Test

### Backend Test

```bash
# Test client'ı çalıştır
python test_client.py
```

### Frontend Test

```bash
cd frontend

# Linting
pnpm lint

# Type checking
pnpm type-check

# Build test
pnpm build
```

## 📊 Yapılandırma

### Environment Variables

#### Backend (.env)
```env
API_TOKEN=your_secure_api_token_here
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
DEFAULT_TIMEOUT=30
MAX_TIMEOUT=300
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TOKEN=default_token
NEXT_PUBLIC_APP_NAME=DexAgents
```

## 🚀 Deployment

### Production Backend

```bash
# Gunicorn ile production
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Production Frontend

```bash
cd frontend
pnpm build
pnpm start
```

## 📝 Geliştirme

### Backend Geliştirme

1. **Yeni endpoint ekleme:**
```python
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "New endpoint"}
```

2. **Model ekleme:**
```python
class NewModel(BaseModel):
    field: str = Field(..., description="Field description")
```

### Frontend Geliştirme

1. **Yeni sayfa ekleme:**
```bash
mkdir frontend/app/new-page
touch frontend/app/new-page/page.tsx
```

2. **API client'a method ekleme:**
```typescript
// lib/api.ts
async newMethod(): Promise<any> {
  return this.request('/new-endpoint')
}
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull request oluşturun

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

- **Proje**: [GitHub Repository](https://github.com/your-username/dexagents)
- **Issues**: [GitHub Issues](https://github.com/your-username/dexagents/issues)

---

**DexAgents** - Windows PowerShell Agent Management System 