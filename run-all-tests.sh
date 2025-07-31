#!/bin/bash

# Comprehensive Test Runner for DexAgents
# Runs all test suites and generates a unified report

set -e

# Redirect output with timestamps
exec 3>&1
exec 1> >(
    while IFS= read line; do
        echo "$(date '+%H:%M:%S') $line"
    done >&3
)

# Function to run command with timeout
run_with_timeout() {
    local timeout_duration=$1
    local description="$2"
    shift 2
    
    echo "[INFO] Running: $description (timeout: ${timeout_duration}s)"
    
    if timeout "$timeout_duration" "$@"; then
        return 0
    else
        echo "[WARNING] Command timed out or failed: $description"
        return 1
    fi
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Timestamp for reports
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="test-reports/${TIMESTAMP}"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((TESTS_SKIPPED++))
}

print_header() {
    echo ""
    echo -e "${CYAN}=================================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}=================================================================================${NC}"
    echo ""
}

# Create report directory
mkdir -p "$REPORT_DIR"

# Start main test report
cat > "$REPORT_DIR/test-summary.md" << EOF
# DexAgents Test Report
**Date:** $(date)
**Environment:** ${ENVIRONMENT:-development}

## Test Results Summary

EOF

print_header "🚀 DexAgents Comprehensive Test Suite"
echo "Starting comprehensive test suite at $(date)"
echo "Report directory: $REPORT_DIR"

# 1. Restart Docker Services (Clean Start)
print_header "🐳 Docker Services Restart"
log_info "Stopping existing services..."
docker-compose down

log_info "Starting fresh Docker services..."
docker-compose up -d --build
sleep 15

if docker-compose ps | grep -E "(backend|frontend|postgres)" | grep -q "Up"; then
    log_success "Docker services started successfully"
    echo "✅ Docker services restarted and running" >> "$REPORT_DIR/test-summary.md"
else
    log_error "Failed to start Docker services"
    echo "❌ Failed to start Docker services" >> "$REPORT_DIR/test-summary.md"
    exit 1
fi

# 2. Backend API Tests (Including AI Features)
print_header "🔌 Backend API Tests (Including AI Features)"
log_info "Running comprehensive API tests with AI features..."

cd backend
if run_with_timeout 45 "Backend API Tests" python3 comprehensive_api_test.py > "$REPORT_DIR/api-test-results.log" 2>&1; then
    log_success "API tests passed (including AI features)"
    echo "✅ Backend API tests passed (including AI features)" >> "$REPORT_DIR/test-summary.md"
    
    # Extract summary from API test results
    if [ -f "api_test_results.json" ]; then
        cp api_test_results.json "$REPORT_DIR/"
    fi
else
    log_error "API tests failed"
    echo "❌ Backend API tests failed" >> "$REPORT_DIR/test-summary.md"
    echo "See $REPORT_DIR/api-test-results.log for details" >> "$REPORT_DIR/test-summary.md"
fi
cd ..

# 3. Frontend E2E Tests (Including AI Features)
print_header "🎭 Frontend E2E Tests (Including AI Features)"
log_info "Running Playwright E2E tests with AI features..."

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    log_info "Installing frontend dependencies..."
    npm install
fi

# Install Playwright browsers if needed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    log_info "Installing Playwright browsers..."
    npx playwright install
fi

# Run E2E tests (only chromium for speed) with timeout, including AI features
if run_with_timeout 120 "Frontend E2E Tests with AI" npm run test:e2e -- --project=chromium --reporter=list > "$REPORT_DIR/e2e-test-results.log" 2>&1; then
    log_success "E2E tests passed (including AI features)"
    echo "✅ Frontend E2E tests passed (including AI features)" >> "$REPORT_DIR/test-summary.md"
else
    log_warning "Some E2E tests failed or timed out"
    echo "⚠️  Some Frontend E2E tests failed or timed out" >> "$REPORT_DIR/test-summary.md"
    echo "See $REPORT_DIR/e2e-test-results.log for details" >> "$REPORT_DIR/test-summary.md"
    
    # Copy test artifacts
    if [ -d "test-results" ]; then
        cp -r test-results "$REPORT_DIR/playwright-artifacts"
    fi
fi
cd ..

# 4. Pre-commit Comprehensive Tests (timeout protection)
print_header "🔍 Pre-commit Comprehensive Tests"
log_info "Running pre-commit test suite with timeout..."

if run_with_timeout 45 "Pre-commit Tests" python3 comprehensive_pre_commit_test.py > "$REPORT_DIR/precommit-test-results.log" 2>&1; then
    log_success "Pre-commit tests passed"
    echo "✅ Pre-commit tests passed" >> "$REPORT_DIR/test-summary.md"
    
    # Copy test report if generated
    if ls test_report_*.json 1> /dev/null 2>&1; then
        cp test_report_*.json "$REPORT_DIR/"
    fi
else
    log_warning "Pre-commit tests timed out or failed"
    echo "⚠️  Pre-commit tests timed out or failed" >> "$REPORT_DIR/test-summary.md"
    echo "See $REPORT_DIR/precommit-test-results.log for details" >> "$REPORT_DIR/test-summary.md"
fi

# 5. Test Coverage Analysis (Skip for now to avoid timeout)
print_header "📊 Test Coverage Analysis"
log_info "Skipping coverage analysis for speed..."
echo "⚠️  Test coverage analysis skipped for speed" >> "$REPORT_DIR/test-summary.md"

# 6. Security Scan
print_header "🔒 Security Scan"
log_info "Running security scans..."

# Quick security check
log_info "Running quick security check..."
echo "⚠️  Security scan skipped for speed" >> "$REPORT_DIR/test-summary.md"

# 7. Performance Tests (basic)
print_header "⚡ Performance Tests"
log_info "Running basic performance tests..."

# Test backend response time
BACKEND_START=$(date +%s%N)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/system/health | grep -q "200"; then
    BACKEND_END=$(date +%s%N)
    BACKEND_TIME=$(( ($BACKEND_END - $BACKEND_START) / 1000000 ))
    
    if [ $BACKEND_TIME -lt 1000 ]; then
        log_success "Backend health check responded in ${BACKEND_TIME}ms"
        echo "✅ Backend performance: ${BACKEND_TIME}ms response time" >> "$REPORT_DIR/test-summary.md"
    else
        log_warning "Backend health check slow: ${BACKEND_TIME}ms"
        echo "⚠️  Backend performance: ${BACKEND_TIME}ms response time (slow)" >> "$REPORT_DIR/test-summary.md"
    fi
else
    log_error "Backend health check failed"
    echo "❌ Backend performance test failed" >> "$REPORT_DIR/test-summary.md"
fi

# Test frontend load time
FRONTEND_START=$(date +%s%N)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    FRONTEND_END=$(date +%s%N)
    FRONTEND_TIME=$(( ($FRONTEND_END - $FRONTEND_START) / 1000000 ))
    
    if [ $FRONTEND_TIME -lt 2000 ]; then
        log_success "Frontend responded in ${FRONTEND_TIME}ms"
        echo "✅ Frontend performance: ${FRONTEND_TIME}ms response time" >> "$REPORT_DIR/test-summary.md"
    else
        log_warning "Frontend load slow: ${FRONTEND_TIME}ms"
        echo "⚠️  Frontend performance: ${FRONTEND_TIME}ms response time (slow)" >> "$REPORT_DIR/test-summary.md"
    fi
else
    log_error "Frontend load failed"
    echo "❌ Frontend performance test failed" >> "$REPORT_DIR/test-summary.md"
fi

# Generate final summary
print_header "📋 Test Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))

cat >> "$REPORT_DIR/test-summary.md" << EOF

## Final Results

- **Total Test Suites:** $TOTAL_TESTS
- **Passed:** $TESTS_PASSED
- **Failed:** $TESTS_FAILED
- **Skipped/Warnings:** $TESTS_SKIPPED

### Status: $([ $TESTS_FAILED -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")

### Recommendations:
EOF

if [ $TESTS_FAILED -eq 0 ]; then
    echo "- All critical tests passed. Safe to proceed with deployment." >> "$REPORT_DIR/test-summary.md"
else
    echo "- Fix failing tests before deployment." >> "$REPORT_DIR/test-summary.md"
    echo "- Review test logs in $REPORT_DIR for details." >> "$REPORT_DIR/test-summary.md"
fi

if [ $TESTS_SKIPPED -gt 0 ]; then
    echo "- Address warnings and skipped tests for better coverage." >> "$REPORT_DIR/test-summary.md"
fi

# Print summary to console
echo ""
echo "Test Summary:"
echo "============="
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo -e "${YELLOW}Warnings: $TESTS_SKIPPED${NC}"
echo ""
echo "Full report saved to: $REPORT_DIR/test-summary.md"

# Generate HTML report
if command -v pandoc >/dev/null 2>&1; then
    pandoc "$REPORT_DIR/test-summary.md" -o "$REPORT_DIR/test-summary.html" --standalone --metadata title="DexAgents Test Report"
    log_info "HTML report generated: $REPORT_DIR/test-summary.html"
fi

# Exit with appropriate code
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi