# DexAgents Production Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Requirements](#server-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Deployment Steps](#deployment-steps)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Rollback Procedure](#rollback-procedure)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for generating secrets)
- Certbot (for SSL certificates)

### Domain & DNS
- Registered domain name
- DNS A records pointing to your server IP
- (Optional) Wildcard SSL certificate or Let's Encrypt setup

## Server Requirements

### Minimum Specifications
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS or CentOS 8+
- **Network**: 100 Mbps connection
- **Ports**: 80, 443, 5432 (PostgreSQL), 6379 (Redis)

### Recommended Specifications
- **CPU**: 8 cores
- **RAM**: 16GB
- **Storage**: 100GB SSD with separate volume for backups
- **Network**: 1 Gbps connection

## Pre-Deployment Checklist

### ✅ Infrastructure
- [ ] Server provisioned and accessible via SSH
- [ ] Docker and Docker Compose installed
- [ ] Firewall configured (ports 80, 443 open)
- [ ] Domain DNS configured
- [ ] SSL certificates obtained

### ✅ Security
- [ ] Strong passwords generated for all services
- [ ] JWT secret keys generated
- [ ] Encryption keys configured
- [ ] Firewall rules configured
- [ ] SSH key-based authentication enabled
- [ ] Fail2ban or similar intrusion prevention configured

### ✅ Testing
- [ ] All API tests passing (87%+ pass rate minimum)
- [ ] Frontend build successful
- [ ] Agent connectivity verified
- [ ] Load testing completed

## Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/dex_agent.git
cd dex_agent
```

### 2. Generate Security Keys
```bash
# Generate PostgreSQL password
openssl rand -base64 32

# Generate JWT secret
openssl rand -hex 64

# Generate encryption key (32 bytes)
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 24
```

### 3. Configure Environment
```bash
# Copy production environment template
cp .env.production .env

# Edit with your values
nano .env
```

**Required configurations:**
- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `SETTINGS_ENCRYPTION_KEY`
- `BACKEND_CORS_ORIGINS`
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_WS_URL`

### 4. SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Generate DH parameters
openssl dhparam -out nginx/ssl/dhparam.pem 2048
```

#### Option B: Commercial SSL Certificate
```bash
# Place your certificates in nginx/ssl/
cp your-cert.crt nginx/ssl/cert.pem
cp your-key.key nginx/ssl/key.pem
```

### 5. Update Nginx Configuration
```bash
# Edit nginx configuration with your domain
sed -i 's/yourdomain.com/YOUR-ACTUAL-DOMAIN/g' nginx/nginx.prod.conf
```

### 6. Build and Deploy
```bash
# Pull latest changes
git pull origin main

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Verify all services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 7. Database Initialization
```bash
# The database will be automatically initialized on first run
# Verify database is ready
docker-compose -f docker-compose.prod.yml exec postgres psql -U dexagents_prod -d dexagents -c "\dt"
```

### 8. Create Admin User (if needed)
```bash
# Access backend container
docker-compose -f docker-compose.prod.yml exec backend bash

# Create admin user via Python script
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
db = SessionLocal()
admin = User(
    username='admin',
    email='admin@yourdomain.com',
    password_hash=get_password_hash('your-secure-password'),
    is_superuser=True
)
db.add(admin)
db.commit()
"
```

## Post-Deployment Verification

### 1. Health Checks
```bash
# Backend health
curl https://api.yourdomain.com/api/v1/health

# Frontend health
curl https://yourdomain.com

# Database connectivity
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Redis connectivity
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

### 2. API Testing
```bash
# Run comprehensive API tests
python comprehensive_api_test.py

# Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

### 3. Agent Connectivity
```bash
# Deploy test agent and verify connection
# Check WebSocket connectivity
# Verify command execution
```

## Monitoring & Maintenance

### Logging
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f [service]

# Log locations:
# - Backend: ./backend/logs/
# - Nginx: ./nginx/logs/
# - PostgreSQL: Check docker logs
```

### Monitoring Endpoints
- Health: `https://api.yourdomain.com/api/v1/health`
- Metrics: `https://api.yourdomain.com/api/v1/metrics`
- Stats: `https://api.yourdomain.com/api/v1/stats`

### Backup Strategy
```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U dexagents_prod dexagents > backup_$(date +%Y%m%d).sql

# Full backup script
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U dexagents_prod dexagents > $BACKUP_DIR/database.sql

# Application data
tar -czf $BACKUP_DIR/app_data.tar.gz backend/data backend/logs

# Keep last 30 days of backups
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### Updates
```bash
# 1. Backup current deployment
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Rebuild and deploy
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Run migrations if needed
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Rollback Procedure

### Quick Rollback
```bash
# 1. Stop current deployment
docker-compose -f docker-compose.prod.yml down

# 2. Checkout previous version
git checkout <previous-tag-or-commit>

# 3. Restore database backup
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U dexagents_prod dexagents < backup.sql

# 4. Rebuild and start
docker-compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.prod.yml logs postgres

# Verify credentials
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U dexagents_prod -d dexagents
```

#### 2. Frontend Not Loading
```bash
# Check frontend logs
docker-compose -f docker-compose.prod.yml logs frontend

# Verify API URL configuration
grep NEXT_PUBLIC_API_URL .env
```

#### 3. Agent Connection Issues
```bash
# Check WebSocket logs
docker-compose -f docker-compose.prod.yml logs backend | grep WebSocket

# Verify firewall rules
sudo ufw status
```

#### 4. High Memory Usage
```bash
# Check resource usage
docker stats

# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service]
```

### Performance Tuning

#### PostgreSQL Optimization
Edit `docker-compose.prod.yml` PostgreSQL command section:
```yaml
command: >
  postgres
  -c max_connections=200
  -c shared_buffers=512MB
  -c effective_cache_size=1GB
```

#### Gunicorn Workers
Adjust in `.env`:
```bash
GUNICORN_WORKERS=8  # 2-4 x CPU cores
```

## Security Considerations

### Regular Updates
- Update Docker images monthly
- Apply security patches promptly
- Monitor CVE databases

### Access Control
- Use strong passwords
- Enable 2FA where possible
- Regularly rotate secrets
- Limit SSH access

### Monitoring
- Set up intrusion detection
- Monitor failed login attempts
- Track API usage patterns
- Regular security audits

## Support & Contact

For deployment issues:
- GitHub Issues: https://github.com/yourusername/dex_agent/issues
- Documentation: https://docs.dexagents.com
- Email: support@yourdomain.com

## Appendix

### Useful Commands
```bash
# View all containers
docker-compose -f docker-compose.prod.yml ps

# Restart all services
docker-compose -f docker-compose.prod.yml restart

# View resource usage
docker stats

# Clean up unused resources
docker system prune -a

# Check disk usage
df -h

# Monitor logs in real-time
tail -f backend/logs/app.log
```

### Environment Variables Reference
See `.env.production` for complete list of configuration options.

---

**Last Updated**: 2025-08-11
**Version**: 3.3.0