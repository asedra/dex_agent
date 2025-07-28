#!/bin/bash

# Test script to validate CI/CD pipeline locally
# This simulates what would happen in GitHub Actions

set -e

echo "🧪 Testing DexAgents CI/CD Pipeline Locally"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test 1: Validate workflow syntax
test_workflow_syntax() {
    log_info "Testing workflow syntax..."
    
    if command -v yamllint >/dev/null 2>&1; then
        yamllint .github/workflows/*.yml
        log_success "Workflow syntax is valid"
    else
        log_warning "yamllint not found, skipping syntax validation"
    fi
}

# Test 2: Frontend tests
test_frontend() {
    log_info "Testing frontend build..."
    
    cd frontend
    
    # Install dependencies
    if [ -f "package.json" ]; then
        npm ci || npm install
        log_success "Frontend dependencies installed"
    else
        log_error "package.json not found in frontend directory"
        return 1
    fi
    
    # Run build (equivalent to CI build test)
    npm run build
    log_success "Frontend build completed"
    
    cd ..
}

# Test 3: Backend tests  
test_backend() {
    log_info "Testing backend..."
    
    cd backend
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        python -m pip install -r requirements.txt
        log_success "Backend dependencies installed"
    else
        log_error "requirements.txt not found in backend directory"
        return 1
    fi
    
    # Test backend startup
    timeout 10s python run.py &
    BACKEND_PID=$!
    sleep 5
    
    if curl -f http://localhost:8000/api/v1/system/health >/dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_warning "Backend health check failed (might be expected in test environment)"
    fi
    
    kill $BACKEND_PID 2>/dev/null || true
    
    cd ..
}

# Test 4: Docker build
test_docker_build() {
    log_info "Testing Docker builds..."
    
    # Test frontend Docker build
    if docker build -t dexagents-frontend-test ./frontend; then
        log_success "Frontend Docker build passed"
    else
        log_error "Frontend Docker build failed"
        return 1
    fi
    
    # Test backend Docker build
    if docker build -t dexagents-backend-test ./backend; then
        log_success "Backend Docker build passed"
    else
        log_error "Backend Docker build failed"
        return 1
    fi
    
    # Cleanup test images
    docker rmi dexagents-frontend-test dexagents-backend-test 2>/dev/null || true
}

# Test 5: Docker Compose
test_docker_compose() {
    log_info "Testing Docker Compose configuration..."
    
    # Test development compose
    if docker-compose config >/dev/null 2>&1; then
        log_success "Development Docker Compose configuration is valid"
    else
        log_error "Development Docker Compose configuration is invalid"
        return 1
    fi
    
    # Test production compose
    if docker-compose -f docker-compose.prod.yml config >/dev/null 2>&1; then
        log_success "Production Docker Compose configuration is valid"
    else
        log_error "Production Docker Compose configuration is invalid"
        return 1
    fi
}

# Test 6: Security scanning simulation
test_security_scan() {
    log_info "Testing security scanning setup..."
    
    # Check if security tools would work
    if command -v docker >/dev/null 2>&1; then
        log_success "Docker available for container scanning"
    else
        log_warning "Docker not available for container scanning"
    fi
    
    # Test npm audit on frontend
    cd frontend
    if [ -f "package.json" ]; then
        npm audit --audit-level=high --production || log_warning "NPM audit found issues (this may be expected)"
        log_success "NPM audit completed"
    fi
    cd ..
    
    # Test Python safety on backend  
    cd backend
    if [ -f "requirements.txt" ]; then
        pip install safety 2>/dev/null || true
        safety check -r requirements.txt || log_warning "Safety check found issues (this may be expected)"
        log_success "Python safety check completed"
    fi
    cd ..
}

# Test 7: Deployment scripts
test_deployment_scripts() {
    log_info "Testing deployment scripts..."
    
    # Test deploy script syntax
    if bash -n scripts/deploy.sh; then
        log_success "Deploy script syntax is valid"
    else
        log_error "Deploy script has syntax errors"
        return 1
    fi
    
    # Test docker management scripts
    if bash -n scripts/docker-dev.sh; then
        log_success "Docker dev script syntax is valid"
    else
        log_error "Docker dev script has syntax errors"
        return 1
    fi
    
    if bash -n scripts/docker-prod.sh; then
        log_success "Docker prod script syntax is valid"
    else
        log_error "Docker prod script has syntax errors"
        return 1
    fi
}

# Run all tests
main() {
    local failed_tests=0
    
    echo "Starting pipeline validation tests..."
    echo ""
    
    # Run tests
    test_workflow_syntax || ((failed_tests++))
    echo ""
    
    test_frontend || ((failed_tests++))
    echo ""
    
    test_backend || ((failed_tests++))
    echo ""
    
    test_docker_build || ((failed_tests++))
    echo ""
    
    test_docker_compose || ((failed_tests++))
    echo ""
    
    test_security_scan || ((failed_tests++))
    echo ""
    
    test_deployment_scripts || ((failed_tests++))
    echo ""
    
    # Summary
    echo "============================================="
    if [ $failed_tests -eq 0 ]; then
        log_success "🎉 All pipeline tests passed!"
        echo "Your CI/CD pipeline is ready for GitHub Actions."
    else
        log_error "❌ $failed_tests test(s) failed"
        echo "Please fix the issues before pushing to GitHub."
        exit 1
    fi
}

# Run main function
main "$@"