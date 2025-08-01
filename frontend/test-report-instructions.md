# Test Report Access Instructions

## 🎯 HTML Test Report Access

After running frontend tests, you can access the interactive HTML report in several ways:

### 1. Automatic Server (Recommended)
The test runner automatically starts a report server:
- **URL**: http://localhost:9323
- Server runs in background
- Interactive report with videos, screenshots, and detailed failure analysis

### 2. Manual Commands
```bash
# Navigate to frontend directory
cd frontend

# Start report server manually
npm run test:report:open

# Or with default Playwright command
npm run test:report
```

### 3. Direct File Access
If server methods don't work:
```bash
# Navigate to report directory
cd frontend/playwright-report

# Open with any web server (Python example)
python3 -m http.server 8080

# Then open: http://localhost:8080
```

## 📊 Report Features

### Interactive Elements
- **Test Results Overview**: Summary with pass/fail counts
- **Test Details**: Click on individual tests for details
- **Failure Analysis**: Error messages with stack traces
- **Screenshots**: Visual proof of failures
- **Videos**: Recording of test execution for failed tests
- **Network Logs**: API calls and responses
- **Console Logs**: Browser console output

### Navigation
- **Filter Tests**: By status (passed/failed/skipped)
- **Search**: Find specific test names
- **Timeline View**: See test execution flow
- **Attachments**: Download screenshots/videos

## 🔧 Troubleshooting

### Report Not Loading
1. **Check Port**: Ensure port 9323 is not blocked
2. **Browser Cache**: Try incognito/private browsing
3. **Alternative Port**: Use `playwright show-report --port=8080`

### Server Won't Start
```bash
# Kill existing processes
pkill -f "playwright show-report"

# Start fresh
cd frontend && npm run test:report:open
```

### Report Files Missing
If HTML report is empty or missing:
```bash
# Re-run tests with proper reporting
cd frontend
npm run test:e2e

# Check output folder
ls -la playwright-report/
```

## 📁 File Locations

- **HTML Report**: `frontend/playwright-report/index.html`
- **Test Results**: `frontend/test-results/`
- **Screenshots**: `frontend/test-results/*/test-failed-*.png`
- **Videos**: `frontend/test-results/*/video.webm`
- **JSON Results**: `frontend/test-results/results.json`

## 💡 Tips

1. **Keep Server Running**: Background server stays active for multiple report views
2. **Fresh Results**: Re-run tests to update report data
3. **Share Reports**: Copy entire `playwright-report/` folder for sharing
4. **Archive Results**: Move test-results to archive old runs

## 🚀 Quick Access

After running tests, simply open: **http://localhost:9323** in your browser.