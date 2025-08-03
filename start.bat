@echo off
REM DexAgents Startup Script - PostgreSQL Version (Windows)
REM This script starts the entire DexAgents platform with PostgreSQL

echo.
echo 🚀 Starting DexAgents Platform with PostgreSQL...
echo =======================================================================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is available  
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo ✅ Docker Compose is available
echo.

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

echo.
echo 🏗️  Building and starting containers...
echo    - PostgreSQL Database (Port 5433)
echo    - Backend API (Port 8080)
echo    - Frontend Web App (Port 3000)
echo.

REM Start all services
docker-compose up -d --build

REM Wait a moment for containers to initialize
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo 📊 Service Status:
docker-compose ps

REM Check PostgreSQL health
echo.
echo 🗄️  Checking PostgreSQL health...
docker exec dexagents-postgres-dev pg_isready -U dexagents -d dexagents >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL is ready
) else (
    echo ⚠️  PostgreSQL is still starting up...
)

REM Check backend health
echo.
echo 🔧 Checking Backend API health...
timeout /t 5 /nobreak >nul
curl -s http://localhost:8080/api/v1/system/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is ready
) else (
    echo ⚠️  Backend API is still starting up...
)

REM Check frontend health
echo.
echo 🌐 Checking Frontend health...
curl -s http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is ready
) else (
    echo ⚠️  Frontend is still starting up...
)

echo.
echo 🎉 DexAgents Platform Started Successfully!
echo =======================================================================================================
echo.
echo 🌐 Access URLs:
echo    • Web Dashboard: http://localhost:3000
echo    • Backend API: http://localhost:8080
echo    • API Documentation: http://localhost:8080/docs
echo    • PostgreSQL: localhost:5433 (dexagents/dexagents_dev_password)
echo.
echo 📊 Default Login:
echo    • Username: admin
echo    • Password: admin123
echo.
echo 🔧 Manage Services:
echo    • View logs: docker-compose logs -f
echo    • Stop all: docker-compose down
echo    • Restart: docker-compose restart
echo.
echo 💡 Troubleshooting:
echo    • If services aren't ready, wait a few minutes and check again
echo    • View individual service logs: docker-compose logs [service-name]
echo    • For database issues: docker-compose logs postgres
echo.
echo Happy managing! 🎯
echo.
pause