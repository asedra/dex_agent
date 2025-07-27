# DexAgents Frontend

Modern ve kullanıcı dostu Windows PowerShell Agent yönetim arayüzü.

## 🚀 Özellikler

- **Modern UI/UX**: Tailwind CSS ve shadcn/ui ile tasarlanmış
- **Responsive Design**: Tüm cihazlarda mükemmel görünüm
- **Real-time Updates**: Gerçek zamanlı sistem bilgileri
- **PowerShell Integration**: Komut çalıştırma ve yönetimi
- **Agent Management**: Agent'ları izleme ve yönetme
- **Dark/Light Mode**: Tema desteği

## 🛠️ Teknolojiler

- **Next.js 15**: React framework
- **TypeScript**: Tip güvenliği
- **Tailwind CSS**: Styling
- **shadcn/ui**: UI bileşenleri
- **Lucide React**: İkonlar
- **React Hook Form**: Form yönetimi

## 📦 Kurulum

### Gereksinimler

- Node.js 18+
- pnpm (önerilen) veya npm

### Adımlar

1. **Bağımlılıkları yükleyin:**
```bash
cd frontend
pnpm install
```

2. **Environment dosyasını oluşturun:**
```bash
cp .env.example .env.local
```

3. **Environment değişkenlerini ayarlayın:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TOKEN=default_token
```

4. **Development sunucusunu başlatın:**
```bash
pnpm dev
```

## 🏗️ Proje Yapısı

```
frontend/
├── app/                    # Next.js App Router
│   ├── agents/            # Agent yönetimi
│   ├── powershell/        # PowerShell komutları
│   ├── schedules/         # Zamanlanmış görevler
│   ├── audit/            # Denetim logları
│   └── globals.css       # Global stiller
├── components/            # UI bileşenleri
│   ├── ui/               # shadcn/ui bileşenleri
│   └── app-sidebar.tsx   # Ana sidebar
├── lib/                  # Utility fonksiyonları
│   ├── api.ts           # API client
│   └── utils.ts         # Yardımcı fonksiyonlar
└── hooks/               # Custom React hooks
```

## 🔧 API Entegrasyonu

### API Client

`lib/api.ts` dosyası backend API'si ile iletişim kurar:

```typescript
import { apiClient } from '@/lib/api'

// Sistem bilgilerini al
const systemInfo = await apiClient.getSystemInfo()

// PowerShell komutu çalıştır
const result = await apiClient.executeCommand({
  command: "Get-Process",
  timeout: 30
})
```

### Endpoint'ler

- `GET /` - Health check
- `GET /system/info` - Sistem bilgileri
- `POST /execute` - Tek komut çalıştırma
- `POST /execute/batch` - Çoklu komut çalıştırma

## 🎨 UI Bileşenleri

### shadcn/ui Kullanımı

```typescript
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Agent Information</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Agent details here</p>
  </CardContent>
</Card>
```

### Tema Desteği

```typescript
import { ThemeProvider } from "@/components/theme-provider"

<ThemeProvider attribute="class" defaultTheme="system">
  {/* App content */}
</ThemeProvider>
```

## 📱 Sayfalar

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

- **API Token**: Bearer token authentication
- **CORS**: Backend'de yapılandırılmış
- **Input Validation**: Form validasyonu
- **Error Handling**: Güvenli hata yönetimi

## 🚀 Deployment

### Production Build

```bash
pnpm build
pnpm start
```

### Environment Variables

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_API_TOKEN=your-secure-token
NEXT_PUBLIC_APP_NAME=DexAgents
```

## 🧪 Test

```bash
# Linting
pnpm lint

# Type checking
pnpm type-check

# Build test
pnpm build
```

## 📝 Geliştirme

### Yeni Sayfa Ekleme

1. `app/` altında yeni klasör oluşturun
2. `page.tsx` dosyası ekleyin
3. Sidebar'a menü öğesi ekleyin

### Yeni API Endpoint

1. `lib/api.ts`'e yeni method ekleyin
2. Interface'leri güncelleyin
3. Sayfalarda kullanın

### Yeni UI Bileşeni

```bash
# shadcn/ui bileşeni ekle
npx shadcn@latest add button
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📄 Lisans

MIT License 