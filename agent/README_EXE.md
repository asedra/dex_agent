# DexAgents Agent Executable

Bu klasör, DexAgents Agent'ının executable (.exe) versiyonunu içerir.

## Dosyalar

- `dist/DexAgentsAgent.exe` - Ana executable dosyası
- `run_agent.bat` - Agent'ı başlatmak için batch dosyası
- `run_agent.ps1` - Agent'ı başlatmak için PowerShell script'i

## Kullanım

### Yöntem 1: Doğrudan exe dosyasını çalıştırma
```cmd
cd agent/dist
DexAgentsAgent.exe
```

### Yöntem 2: Batch dosyası ile çalıştırma
```cmd
cd agent
run_agent.bat
```

### Yöntem 3: PowerShell script ile çalıştırma
```powershell
cd agent
.\run_agent.ps1
```

### Yöntem 4: Windows Explorer'dan çalıştırma
- `agent/dist` klasörüne gidin
- `DexAgentsAgent.exe` dosyasına çift tıklayın

## Özellikler

- **Standalone**: Python yüklü olmadan çalışır
- **Portable**: Başka bilgisayarlara kopyalanabilir
- **GUI Interface**: Kullanıcı dostu arayüz
- **Auto-start**: Yapılandırılabilir otomatik başlatma
- **System Monitoring**: CPU, Memory ve Disk kullanımını izler
- **WebSocket Support**: Gerçek zamanlı iletişim

## Yapılandırma

Agent ilk çalıştırıldığında `config.json` dosyası oluşturulur. Bu dosyayı düzenleyerek:

- Server URL'sini
- API Token'ını
- Agent adını
- Tag'leri
- Otomatik başlatma ayarlarını

değiştirebilirsiniz.

## Sorun Giderme

### Eğer exe dosyası çalışmazsa:
1. Windows Defender'ın dosyayı engellemediğinden emin olun
2. Antivirüs programınızı geçici olarak devre dışı bırakın
3. Dosyayı yönetici olarak çalıştırmayı deneyin
4. Windows Event Viewer'da hata mesajlarını kontrol edin

### "ModuleNotFoundError: No module named 'psutil'" hatası:
Bu hata PyInstaller'ın modülü dahil etmemesinden kaynaklanır. Çözüm:
1. Mevcut exe dosyasını silin
2. Yeniden derleyin:
```cmd
cd agent
pyinstaller --onefile --windowed --add-data "C:\Users\Ali\AppData\Roaming\Python\Python312\site-packages\psutil;psutil" --add-data "C:\Users\Ali\AppData\Roaming\Python\Python312\site-packages\websockets;websockets" --add-data "C:\Users\Ali\AppData\Roaming\Python\Python312\site-packages\requests;requests" --hidden-import=uuid --name DexAgentsAgent agent_gui.py
```

### "ModuleNotFoundError: No module named 'uuid'" hatası:
Bu hata WebSocket bağlantısında oluşabilir. Çözüm:
1. Yukarıdaki komutu kullanarak yeniden derleyin
2. `--hidden-import=uuid` parametresinin dahil edildiğinden emin olun

### Log dosyaları:
- `logs/agent.log` - Detaylı log dosyası
- GUI'deki log paneli - Canlı log görüntüleme

## Yeniden Derleme

Exe dosyasını yeniden oluşturmak için:

```cmd
cd agent
pyinstaller --onefile --windowed --add-data "C:\Users\Ali\AppData\Roaming\Python\Python312\site-packages\psutil;psutil" --add-data "C:\Users\Ali\AppData\Roaming\Python\Python312\site-packages\websockets;websockets" --add-data "C:\Users\Ali\AppData\Roaming\Python\Python312\site-packages\requests;requests" --hidden-import=uuid --name DexAgentsAgent agent_gui.py
```

## Gereksinimler

- Windows 10/11
- .NET Framework 4.5+ (genellikle yüklü)
- İnternet bağlantısı (server ile iletişim için)

## Dağıtım

Exe dosyasını başka bilgisayarlara dağıtmak için:
1. `dist` klasörünü kopyalayın
2. `config.json` dosyasını düzenleyin
3. `run_agent.bat` veya `run_agent.ps1` dosyalarını kullanın

## Özellikler

- **HTTP API**: REST API ile server iletişimi
- **WebSocket**: Gerçek zamanlı komut alma
- **System Monitoring**: CPU, Memory, Disk kullanımı
- **Command Execution**: PowerShell komutları çalıştırma
- **Logging**: Detaylı log sistemi
- **GUI**: Kullanıcı dostu arayüz 