# Windows PowerShell Agent Frontend

Modern web arayüzü ile PowerShell komutlarını çalıştırın.

## Özellikler

- 🎨 **Modern UI**: Tailwind CSS ile güzel arayüz
- ⚡ **Tek Komut**: Tek PowerShell komutu çalıştırma
- 🔄 **Batch İşlemler**: Çoklu komut çalıştırma
- 📊 **Sistem Bilgileri**: CPU, RAM, disk kullanımı
- 🔐 **Güvenli**: API token authentication
- 💾 **Ayarlar**: API URL ve token yönetimi

## Kurulum

```bash
# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev
```

## Kullanım

1. **API Ayarları**: Üst kısımda API URL ve token'ı ayarlayın
2. **Tek Komut**: "Single Command" sekmesinde PowerShell komutu çalıştırın
3. **Batch İşlemler**: "Batch Commands" sekmesinde çoklu komut çalıştırın
4. **Sistem Bilgileri**: "System Info" sekmesinde sistem durumunu görün

## Teknolojiler

- **SvelteKit**: Modern web framework
- **TypeScript**: Tip güvenliği
- **Tailwind CSS**: Styling
- **Fetch API**: HTTP istekleri

## Geliştirme

```bash
# Geliştirme sunucusu
npm run dev

# Build
npm run build

# Preview
npm run preview
```

## API Bağlantısı

Frontend, backend API'sine bağlanır:
- **URL**: http://localhost:8000 (varsayılan)
- **Token**: API güvenlik token'ı
- **Endpoints**: `/execute`, `/execute/batch`, `/system/info`
