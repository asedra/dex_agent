# DexAgents Heartbeat System

Bu dokümantasyon, DexAgents sistemindeki heartbeat (kalp atışı) mekanizmasını açıklar. Agent'lar her 30 saniyede bir heartbeat göndererek backend'e online olduklarını bildirir.

## Özellikler

### Backend Heartbeat Sistemi

1. **HTTP Heartbeat Endpoint**: `/api/v1/agents/{agent_id}/heartbeat`
   - Agent'lar bu endpoint'e POST isteği gönderir
   - Sistem bilgilerini (CPU, RAM, disk kullanımı) toplar
   - Agent'ın `last_seen` zamanını günceller
   - Agent durumunu "online" olarak işaretler

2. **WebSocket Heartbeat**: Mevcut WebSocket bağlantısı üzerinden heartbeat mesajları
   - Agent WebSocket bağlantısı varsa ek olarak WebSocket üzerinden de heartbeat gönderir
   - Gerçek zamanlı iletişim sağlar

3. **Otomatik Offline Tespiti**: Backend her 30 saniyede bir kontrol eder
   - 60 saniyeden fazla heartbeat almayan agent'ları "offline" olarak işaretler
   - Agent durumlarını otomatik olarak günceller

### Agent Heartbeat Sistemi

1. **GUI Agent**: `agent_gui.py`
   - Her 30 saniyede bir HTTP heartbeat gönderir
   - WebSocket bağlantısı varsa WebSocket heartbeat de gönderir
   - Sistem bilgilerini toplar ve GUI'de gösterir

2. **Standalone Heartbeat Agent**: `heartbeat_agent.py`
   - Bağımsız çalışan basit heartbeat agent'ı
   - Komut satırından çalıştırılabilir
   - Test ve geliştirme için kullanılır

## API Endpoints

### Heartbeat Endpoints

```http
POST /api/v1/agents/{agent_id}/heartbeat
Authorization: Bearer {api_token}
```

**Response:**
```json
{
  "message": "Heartbeat received",
  "agent": {
    "id": "agent-001",
    "hostname": "DESKTOP-ABC123",
    "status": "online",
    "last_seen": "2025-07-27T17:47:54.661",
    "system_info": {
      "cpu_usage": 25.5,
      "memory_usage": 65.2,
      "disk_usage": {
        "C:\\": 45.1
      }
    }
  },
  "timestamp": "2025-07-27T17:47:54.661"
}
```

### Status Endpoints

```http
GET /api/v1/agents/status/{agent_id}
Authorization: Bearer {api_token}
```

**Response:**
```json
{
  "agent_id": "agent-001",
  "overall_status": "online",
  "websocket_connected": true,
  "heartbeat_status": "recent",
  "seconds_since_heartbeat": 15.5,
  "last_seen": "2025-07-27T17:47:54.661",
  "agent_data": { ... }
}
```

```http
GET /api/v1/agents/offline
Authorization: Bearer {api_token}
```

**Response:**
```json
[
  {
    "id": "agent-002",
    "hostname": "LAPTOP-XYZ789",
    "status": "offline",
    "last_seen": "2025-07-27T17:45:30.123"
  }
]
```

## Kullanım

### GUI Agent ile Heartbeat

1. Agent GUI'yi başlatın:
```bash
cd agent
python agent_gui.py
```

2. Agent'ı kaydedin ve bağlantıyı başlatın
3. Heartbeat otomatik olarak her 30 saniyede bir gönderilir

### Standalone Heartbeat Agent

```bash
# Agent'ı kaydet ve heartbeat gönder
python heartbeat_agent.py --agent-id "my-agent-001" --register

# Sadece heartbeat gönder (agent zaten kayıtlı)
python heartbeat_agent.py --agent-id "my-agent-001"

# Farklı server URL'i ile
python heartbeat_agent.py --agent-id "my-agent-001" --server-url "http://192.168.1.100:8000"
```

### Test Etme

```bash
# Heartbeat fonksiyonlarını test et
python test_heartbeat.py
```

## Konfigürasyon

### Backend Konfigürasyonu

Backend otomatik olarak:
- Her 30 saniyede bir agent durumlarını kontrol eder
- 60 saniyeden fazla heartbeat almayan agent'ları offline olarak işaretler
- Sistem bilgilerini toplar ve saklar

### Agent Konfigürasyonu

`config.json` dosyasında:
```json
{
  "server_url": "http://localhost:8000",
  "api_token": "your-secret-key-here",
  "agent_name": "DESKTOP-ABC123",
  "tags": ["windows", "gui-agent"],
  "auto_start": false,
  "run_as_service": false
}
```

## Loglar

### Backend Logları
- Heartbeat alındığında: `INFO - Heartbeat received from agent {agent_id}`
- Agent offline olduğunda: `INFO - Marking agent {agent_id} as offline`
- Agent online olduğunda: `INFO - Marking agent {agent_id} as online`

### Agent Logları
- Heartbeat gönderildiğinde: `INFO - HTTP heartbeat sent successfully`
- WebSocket heartbeat gönderildiğinde: `INFO - WebSocket heartbeat sent successfully`
- Hata durumunda: `ERROR - Heartbeat error: {error_message}`

## Monitoring

### Agent Durumları

1. **Online**: Son 30 saniyede heartbeat alınmış
2. **Warning**: Son 30-60 saniye arasında heartbeat alınmış
3. **Offline**: 60 saniyeden fazla heartbeat alınmamış

### Sistem Bilgileri

Her heartbeat'te toplanan bilgiler:
- CPU kullanımı (%)
- RAM kullanımı (%)
- Disk kullanımı (her partition için %)
- Hostname
- OS bilgileri

## Sorun Giderme

### Heartbeat Gönderilmiyor

1. Backend'in çalıştığından emin olun
2. API token'ın doğru olduğunu kontrol edin
3. Network bağlantısını kontrol edin
4. Agent ID'nin doğru olduğunu kontrol edin

### Agent Offline Görünüyor

1. Agent'ın çalıştığından emin olun
2. Heartbeat thread'inin çalıştığını kontrol edin
3. Log dosyalarını kontrol edin
4. Network bağlantısını kontrol edin

### Performans Sorunları

1. Heartbeat aralığını artırabilirsiniz (şu anda 30 saniye)
2. Sistem bilgisi toplama işlemini optimize edebilirsiniz
3. Log seviyesini azaltabilirsiniz

## Geliştirme

### Yeni Heartbeat Özellikleri Ekleme

1. Backend'de yeni endpoint ekleyin
2. Agent'da yeni heartbeat türü ekleyin
3. Test script'ini güncelleyin
4. Dokümantasyonu güncelleyin

### Monitoring Geliştirme

1. Heartbeat istatistikleri ekleyin
2. Alert sistemi ekleyin
3. Dashboard geliştirin
4. Email/SMS bildirimleri ekleyin 