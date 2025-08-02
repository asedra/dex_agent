# Claude.md

## Proje Ortamı

Bu proje Windows WSL (Windows Subsystem for Linux) üzerinde çalışmaktadır.

### Sistem Bilgileri
- Platform: Linux (WSL2)
- OS Version: Linux 5.15.167.4-microsoft-standard-WSL2
- Çalışma dizini: /home/ali/claude

### Windows Dosya Sistemi Erişimi
Windows dosya sistemine WSL'den `/mnt/c/` üzerinden erişilebilir. Örneğin:
- Windows Downloads: `/mnt/c/Users/Ali/Downloads/`
- Windows Desktop: `/mnt/c/Users/Ali/Desktop/`

## Claude Code Hierarchical Commands

Bu proje, Claude Code için hiyerarşik komut sistemi sağlar. Aşağıdaki komutlar kullanılabilir:

### Root Komutlar
- `/all_modes` - Tüm modları görüntüle (Developer, Reviewer, Architect modları)
- `/help` - Yardım menüsü
- `/status` - Sistem durumu

### Developer Mode (`/developer_mode`)
Developer moduna geçtikten sonra kullanılabilir komutlar:
- `/select_project [abbreviation]` - Jira projesini seç (KAN, SAM1)
- `/create_branch` - Yeni git branch oluştur
- `/run_tests` - Test süitini çalıştır  
- `/deploy` - Deploy işlemi başlat

### Reviewer Mode (`/reviewer_mode`)  
Code review ve kalite analizi komutları:
- `/analyze_pr` - Pull request analizi (kısayol: `apr`)
- `/check_standards` - Kod standartları kontrolü (kısayol: `cs`)
- `/security_scan` - Güvenlik taraması (kısayol: `ss`)
- `/performance_review` - Performans incelemesi (kısayol: `pr`)

### Architect Mode (`/architect_mode`)
Sistem tasarımı ve mimari komutları:
- `/design_system` - Sistem tasarımı oluştur (kısayol: `ds`)
- `/create_diagram` - Mimari diagramlar (kısayol: `cd`)
- `/architecture_review` - Mimari inceleme (kısayol: `ar`)
- `/tech_stack_analysis` - Teknoloji analizi (kısayol: `tsa`)

### MCP Jira Entegrasyonu
- **Jira URL**: https://sipsy.atlassian.net  
- **Cloud ID**: e9ed7bab-c21a-4b0c-b996-fa7146d8e58b
- **Projeler**: KAN (Claude Code Development), SAM1 (Annual Product Roadmap)
- **Kullanım**: `/select_project KAN` ile proje seçimi

### Komut Kullanım Örneği
```
/all_modes
→ 🔧 developer_mode - Development-focused commands
→ 🔍 reviewer_mode - Code review and quality commands  
→ 🏗️ architect_mode - System design and architecture commands

/developer_mode
→ Developer mode activated. Available commands:
→ - /select_project - Select project from Jira
→ - /create_branch - Create new git branch
→ - /run_tests - Execute test suite
→ - /deploy - Deploy to environment

/select_project
→ Connecting to Jira...
→ Available projects:
→ 1. KAN - Claude Code Development
→ 2. SAM1 - (Example) Annual Product Roadmap Planning
```

### Story-Teller Mode (`/story-teller-mode`)
Hikaye tabanlı geliştirme ve rol bazlı görev oluşturma:
- `/create-story` - Yeni hikaye oluştur
- `/story-analysis [story-id]` - Hikaye analizi ve rol aktivasyonu (kısayol: `sa`)

#### Aktif Rol Komutları (Story Analysis sonrası)
- `/frontend_developer_story [story-id]` - Frontend geliştirme görevleri (kısayol: `fed`)  
- `/backend_developer_story [story-id]` - Backend geliştirme görevleri (kısayol: `bed`)
- `/database_developer_story [story-id]` - Veritabanı geliştirme görevleri (kısayol: `dbd`)
- `/qa_engineer_story [story-id]` - QA test görevleri (kısayol: `qae`)
- `/ux-designer [story-id]` - UX tasarım görevleri (kısayol: `uxd`)
- `/devops-engineer [story-id]` - DevOps görevleri (kısayol: `doe`)
- `/ai-developer [story-id]` - AI geliştirme görevleri (kısayol: `aid`)

### Konfigürasyon
Komut konfigürasyonları `.claude/` dizininde JSON dosyaları olarak saklanır:
- `.claude/config.json` - Ana konfigürasyon
- `.claude/commands/` - Komut tanımları
- `.claude/integrations/jira-mcp.json` - Jira MCP ayarları