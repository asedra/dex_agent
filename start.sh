#!/bin/bash

# DexAgents Startup Script - PostgreSQL Version
# This script starts the entire DexAgents platform with PostgreSQL

echo "🚀 Starting DexAgents Platform with PostgreSQL..."
echo "======================================================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Docker Compose is available"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

echo ""
echo "🏗️  Building and starting containers..."
echo "   - PostgreSQL Database (Port 5433)"
echo "   - Backend API (Port 8080)" 
echo "   - Frontend Web App (Port 3000)"
echo ""

# Start all services
docker-compose up -d --build

# Wait a moment for containers to initialize
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

# Check PostgreSQL health
echo ""
echo "🗄️  Checking PostgreSQL health..."
if docker exec dexagents-postgres-dev pg_isready -U dexagents -d dexagents > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "⚠️  PostgreSQL is still starting up..."
fi

# Check backend health
echo ""
echo "🔧 Checking Backend API health..."
sleep 5
if curl -s http://localhost:8080/api/v1/system/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "⚠️  Backend API is still starting up..."
fi

# Check frontend health  
echo ""
echo "🌐 Checking Frontend health..."
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Frontend is ready"
else
    echo "⚠️  Frontend is still starting up..."
fi

echo ""
echo "🎉 DexAgents Platform Started Successfully!"
echo "======================================================================================================="
echo ""
echo "🌐 Access URLs:"
echo "   • Web Dashboard: http://localhost:3000"
echo "   • Backend API: http://localhost:8080"
echo "   • API Documentation: http://localhost:8080/docs"
echo "   • PostgreSQL: localhost:5433 (dexagents/dexagents_dev_password)"
echo ""
echo "📊 Default Login:"
echo "   • Username: admin"
echo "   • Password: admin123"
echo ""
echo "🔧 Manage Services:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop all: docker-compose down"
echo "   • Restart: docker-compose restart"
echo ""
echo "💡 Troubleshooting:"
echo "   • If services aren't ready, wait a few minutes and check again"
echo "   • View individual service logs: docker-compose logs [service-name]"
echo "   • For database issues: docker-compose logs postgres"
echo ""
echo "Happy managing! 🎯"