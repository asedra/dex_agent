#!/bin/bash
# Render.com Deployment Script for DexAgents

set -e

echo "🚀 Starting Render.com deployment for DexAgents..."

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found!"
    exit 1
fi

# Validate configuration
echo "📋 Validating Render configuration..."

# Check backend files
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Backend requirements.txt not found!"
    exit 1
fi

if [ ! -f "backend/start.py" ]; then
    echo "❌ Backend start.py not found!"
    exit 1
fi

# Check frontend files
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Frontend package.json not found!"
    exit 1
fi

echo "✅ All required files found"

# Display deployment information
echo "📊 Deployment Configuration:"
echo "  Backend: Python/FastAPI (backend/)"
echo "  Frontend: Node.js/Next.js (frontend/)"
echo "  Health Checks: /api/v1/system/health, /api/health"
echo "  Auto Deploy: Enabled"

echo ""
echo "🎯 Next Steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Render"
echo "3. Use the render.yaml configuration"
echo "4. Deploy and monitor logs"

echo ""
echo "📚 Render Dashboard: https://dashboard.render.com"
echo "🔧 Configuration file: render.yaml"

echo "✅ Render deployment preparation complete!"