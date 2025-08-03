# DexAgents Frontend E2E Tests

Bu dizin, DexAgents frontend uygulaması için Playwright ile yazılmış end-to-end testlerini içerir.

## Test Yapısı

### Test Dosyaları

- **`auth.spec.ts`** - Kullanıcı girişi ve kimlik doğrulama testleri
- **`dashboard.spec.ts`** - Ana sayfa (dashboard) testleri
- **`agents.spec.ts`** - Agent yönetimi sayfası testleri
- **`commands.spec.ts`** - Komut yönetimi sayfası testleri
- **`api-integration.spec.ts`** - API entegrasyonu testleri
- **`comprehensive.spec.ts`** - Kapsamlı senaryo testleri

### Helper Dosyaları

- **`helpers/auth.ts`** - Kimlik doğrulama işlemleri için yardımcı fonksiyonlar
- **`helpers/api-mocks.ts`** - API yanıtlarını mock'lamak için yardımcı fonksiyonlar

## Kurulum

### Ön Gereksinimler

1. Node.js (v18 veya üzeri)
2. npm veya yarn
3. DexAgents backend sunucusunun çalışıyor olması (localhost:8080)
4. DexAgents frontend uygulamasının çalışıyor olması (localhost:3000)

### Bağımlılıkları Yükleme

```bash
# Frontend dizininde
cd frontend
npm install

# Playwright tarayıcılarını yükle
npx playwright install
```

## Testleri Çalıştırma

### Tüm Testler

```bash
# Headless modda (varsayılan)
npm run test:e2e

# Tarayıcı ile birlikte (görsel mod)
npm run test:e2e:headed

# Test UI ile (interaktif mod)
npm run test:e2e:ui
```

### Belirli Test Dosyası

```bash
# Sadece auth testleri
npx playwright test auth.spec.ts

# Sadece dashboard testleri
npx playwright test dashboard.spec.ts
```

### Belirli Tarayıcı

```bash
# Sadece Chromium
npx playwright test --project=chromium

# Sadece Firefox
npx playwright test --project=firefox
```

### Debug Modu

```bash
# Debug modda çalıştır
npx playwright test --debug

# Belirli testi debug et
npx playwright test auth.spec.ts --debug
```

## Test Senaryoları

### Authentication Tests (auth.spec.ts)

- ✅ Giriş formu görüntüleme
- ✅ Boş alanlar için doğrulama hatası
- ✅ Geçersiz kimlik bilgileri için hata mesajı
- ✅ Geçerli kimlik bilgileriyle başarılı giriş (admin/admin123)
- ✅ Kimlik doğrulaması yapılan kullanıcının login sayfasından yönlendirilmesi
- ✅ Giriş yükleme durumu kontrolü
- ✅ Token doğrulama (/me endpoint)

### Dashboard Tests (dashboard.spec.ts)

- ✅ Dashboard bileşenlerinin görüntülenmesi
- ✅ İstatistik kartları (Total/Online Agents, Commands, Jobs)
- ✅ Sistem durumu bilgileri
- ✅ Hızlı eylemler (Quick Actions)
- ✅ Son aktiviteler (Recent Activity)
- ✅ Yükleme durumu işleme
- ✅ Hata durumu işleme
- ✅ Mobil uyumluluk

### Agents Tests (agents.spec.ts)

- ✅ Agent listesi görüntüleme
- ✅ Boş agent listesi işleme
- ✅ Agent bilgilerinin doğru görüntülenmesi
- ✅ Durum filtreleme (online/offline)
- ✅ Agent detay sayfasına navigasyon
- ✅ API hata işleme
- ✅ Liste yenileme
- ✅ Mobil uyumluluk

### Commands Tests (commands.spec.ts)

- ✅ Kayıtlı komutlar listesi
- ✅ Boş komut listesi işleme
- ✅ Agent üzerinde komut çalıştırma
- ✅ Yeni komut oluşturma
- ✅ Kategori ile filtreleme
- ✅ Komut çalıştırma hataları
- ✅ Komut düzenleme
- ✅ Komut silme
- ✅ API hata işleme

### API Integration Tests (api-integration.spec.ts)

- ✅ `/api/v1/auth/login` - Kullanıcı girişi
- ✅ `/api/v1/auth/me` - Token doğrulama
- ✅ `/api/v1/agents` - Agent listesi
- ✅ `/api/v1/commands/saved` - Kayıtlı komutlar
- ✅ `/api/v1/commands/agent/{id}/execute` - Komut çalıştırma
- ✅ `/api/v1/settings` - Ayarlar
- ✅ `/api/v1/system/health` - Sistem durumu
- ✅ Yetkisiz erişim kontrolü
- ✅ WebSocket bağlantısı
- ✅ Veri tutarlılığı

### Comprehensive Tests (comprehensive.spec.ts)

- ✅ Tam kullanıcı iş akışı
- ✅ Tüm API hata senaryoları
- ✅ Farklı ekran boyutları
- ✅ Ağ bağlantısı sorunları
- ✅ Sayfa yenileme sonrası kimlik durumu
- ✅ Tarayıcı geri/ileri navigasyonu
- ✅ Eşzamanlı API çağrıları
- ✅ Veri tutarlılığı doğrulama
- ✅ Sınır koşulları
- ✅ Erişilebilirlik kontrolleri

## Test Konfigürasyonu

### Playwright Config (playwright.config.ts)

```typescript
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### Test Ortamı

- **Base URL**: http://localhost:3000 (Frontend)
- **API URL**: http://localhost:8080 (Backend)
- **Test Credentials**: admin/admin123

## Mock Veriler

Testler, gerçek API yerine mock veriler kullanabilir:

```typescript
import { APIMocks } from './helpers/api-mocks'

// Mock auth
await apiMocks.mockLogin()
await apiMocks.mockUserInfo()

// Mock agents
await apiMocks.mockAgents([
  { id: 1, hostname: 'TEST-PC-001', status: 'online' }
])

// Mock commands
await apiMocks.mockCommands([
  { id: 1, name: 'Test Command', command: 'Get-Date' }
])
```

## CI/CD Entegrasyonu

Testler CI/CD pipeline'ında çalıştırılabilir:

```yaml
- name: Run E2E Tests
  run: |
    npm ci
    npx playwright install --with-deps
    npm run test:e2e
```

## Raporlama

Test sonuçları farklı formatlarda kaydedilir:

- **HTML Report**: `playwright-report/index.html`
- **JSON Report**: `test-results/results.json`
- **JUnit Report**: `test-results/junit.xml`

## Test Geliştirme

### Yeni Test Ekleme

1. `tests/e2e/` dizininde yeni `.spec.ts` dosyası oluştur
2. Helper fonksiyonları kullan
3. API mock'larını kur
4. Test senaryolarını yaz

### Best Practices

1. **Page Object Model** kullan
2. **Wait stratejileri** uygula (`expect` ile)
3. **Mock veriler** kullan
4. **Temizlik** yap (teardown)
5. **Paralel çalışma** için hazırla

## Troubleshooting

### Ortak Sorunlar

1. **Port Çakışması**: Frontend/Backend portlarını kontrol et
2. **Timeout**: Ağ gecikmesi için timeout artır
3. **Browser Issues**: `npx playwright install` çalıştır
4. **Auth Problems**: Credential'ları kontrol et

### Debug İpuçları

```bash
# Verbose output
DEBUG=pw:* npx playwright test

# Test inspector
npx playwright test --debug

# Trace viewer
npx playwright show-trace trace.zip
```

## API Endpoint Referansı

### Kimlik Doğrulama
- `POST /api/v1/auth/login` - Giriş
- `GET /api/v1/auth/me` - Kullanıcı bilgisi

### Agents
- `GET /api/v1/agents` - Agent listesi

### Commands
- `GET /api/v1/commands/saved` - Kayıtlı komutlar
- `POST /api/v1/commands/agent/{id}/execute` - Komut çalıştır

### System
- `GET /api/v1/system/health` - Sistem durumu
- `GET /api/v1/system/info` - Sistem bilgisi

### Settings
- `GET /api/v1/settings` - Ayarlar

Bu testler, DexAgents frontend uygulamasının tüm ana fonksiyonlarını kapsamlı bir şekilde test eder ve API entegrasyonunu doğrular.