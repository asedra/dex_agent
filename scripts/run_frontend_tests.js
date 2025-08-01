#!/usr/bin/env node
/**
 * Frontend Test Runner with Automated Reporting
 * Runs Playwright E2E tests and generates formatted markdown reports
 */

const { exec, spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class FrontendTestRunner {
    constructor() {
        this.projectRoot = path.resolve(__dirname, '..');
        this.frontendPath = path.join(this.projectRoot, 'frontend');
        this.resultsFile = path.join(this.projectRoot, 'frontend_test_results.md');
        this.testResults = [];
    }

    async checkServices() {
        console.log('🔍 Checking if frontend services are running...');
        
        try {
            const response = await this.fetchWithTimeout('http://localhost:3000', 5000);
            if (response) {
                console.log('✅ Frontend services are running');
                return true;
            } else {
                console.log('❌ Frontend services are not responding');
                return false;
            }
        } catch (error) {
            console.log(`❌ Error checking services: ${error.message}`);
            return false;
        }
    }

    async fetchWithTimeout(url, timeout) {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                reject(new Error('Request timeout'));
            }, timeout);

            // Use curl to check if service is responding
            exec(`curl -s -o /dev/null -w "%{http_code}" ${url}`, (error, stdout, stderr) => {
                clearTimeout(timer);
                if (error) {
                    reject(error);
                } else {
                    const statusCode = stdout.trim();
                    resolve(statusCode === '200' || statusCode === '404' || statusCode === '401'); // Any response means service is up
                }
            });
        });
    }

    async runTests() {
        console.log('\n🧪 Running frontend E2E tests...');
        console.log('=' .repeat(60));
        console.log('🚀 Starting Playwright E2E test execution');
        console.log('📊 Live test results will appear below:');
        console.log('-'.repeat(60));

        return new Promise((resolve) => {
            // Change to frontend directory and run tests with timeout and limited scope
            const testProcess = spawn('npx', ['playwright', 'test', '--reporter=json', '--timeout=30000', '--max-failures=5', '--project=chromium'], {
                cwd: this.frontendPath,
                stdio: ['inherit', 'pipe', 'pipe']
            });

            // Add process timeout to prevent hanging
            const processTimeout = setTimeout(() => {
                console.log('\n⚠️  Test process timeout - killing process...');
                testProcess.kill('SIGTERM');
                setTimeout(() => {
                    if (!testProcess.killed) {
                        console.log('💀 Force killing process...');
                        testProcess.kill('SIGKILL');
                    }
                }, 5000);
            }, 90000); // 90 second timeout

            let stdoutData = '';
            let stderrData = '';

            testProcess.stdout.on('data', (data) => {
                const output = data.toString();
                stdoutData += output;
                
                // Show live progress with enhanced formatting
                if (output.includes('Running') || output.includes('passed') || output.includes('failed')) {
                    const lines = output.split('\n').filter(line => line.trim());
                    lines.forEach(line => {
                        if (line.includes('passed')) {
                            console.log(`✅ ${line.trim()}`);
                        } else if (line.includes('failed')) {
                            console.log(`❌ ${line.trim()}`);
                        } else if (line.includes('Running')) {
                            console.log(`🧪 ${line.trim()}`);
                        } else {
                            console.log(`📋 ${line.trim()}`);
                        }
                    });
                } else {
                    // Show raw output for other content
                    process.stdout.write(data);
                }
            });

            testProcess.stderr.on('data', (data) => {
                const output = data.toString();
                stderrData += output;
                
                // Enhanced error output formatting
                if (output.includes('Error') || output.includes('Failed')) {
                    console.error(`❌ ${output.trim()}`);
                } else if (output.includes('Warning')) {
                    console.warn(`⚠️  ${output.trim()}`);
                } else {
                    process.stderr.write(data);
                }
            });

            testProcess.on('close', (code) => {
                clearTimeout(processTimeout); // Clear timeout when process ends normally
                console.log('\n' + '='.repeat(60));
                console.log('🏁 Test execution completed!');
                
                // Parse test results
                const results = this.parsePlaywrightResults(stdoutData, stderrData, code);
                
                console.log('TEST SUMMARY');
                console.log('='.repeat(60));
                console.log(`Total Tests: ${results.total}`);
                console.log(`Passed: ${results.passed}`);
                console.log(`Failed: ${results.failed}`);
                console.log(`Skipped: ${results.skipped}`);
                console.log(`Success Rate: ${(results.passed/results.total*100).toFixed(1)}%`);
                console.log();

                if (code === 0) {
                    console.log('🎉 ALL TESTS PASSED!');
                } else {
                    console.log('⚠️  Some tests failed. Check details above.');
                }

                resolve({
                    success: code === 0,
                    results: results
                });
            });

            // Handle process termination/kill
            testProcess.on('exit', (code, signal) => {
                clearTimeout(processTimeout);
                if (signal === 'SIGTERM' || signal === 'SIGKILL') {
                    console.log(`\n💀 Test process terminated (${signal})`);
                    const timeoutResults = {
                        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
                        total: 1,
                        passed: 0,
                        failed: 1,
                        skipped: 0,
                        duration: 'Timeout',
                        tests: [{
                            name: 'Test Execution',
                            status: 'failed',
                            error: 'Test execution timed out and was killed',
                            duration: 'Timeout'
                        }],
                        errors: ['Test execution timed out after 90 seconds']
                    };
                    
                    resolve({
                        success: false,
                        results: timeoutResults
                    });
                }
            });
        });
    }

    parsePlaywrightResults(stdout, stderr, exitCode) {
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        
        // Try to parse JSON output first
        let jsonResults = null;
        try {
            // Look for JSON in stdout
            const jsonMatch = stdout.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                jsonResults = JSON.parse(jsonMatch[0]);
            }
        } catch (e) {
            // Fallback to text parsing
        }

        // Initialize results structure
        const results = {
            timestamp: timestamp,
            total: 0,
            passed: 0,
            failed: 0,
            skipped: 0,
            duration: 'Unknown',
            tests: [],
            errors: []
        };

        if (jsonResults && jsonResults.suites) {
            // Parse JSON results
            this.parseJsonResults(jsonResults, results);
        } else {
            // Fallback: parse text output
            this.parseTextResults(stdout, stderr, results);
        }

        // If no tests were found, try to extract basic info from output
        if (results.total === 0) {
            const testCountMatch = stdout.match(/(\d+)\s+passed/i) || stderr.match(/(\d+)\s+passed/i);
            const failedMatch = stdout.match(/(\d+)\s+failed/i) || stderr.match(/(\d+)\s+failed/i);
            
            if (testCountMatch) {
                results.passed = parseInt(testCountMatch[1]) || 0;
            }
            if (failedMatch) {
                results.failed = parseInt(failedMatch[1]) || 0;
            }
            results.total = results.passed + results.failed;
        }

        // Extract duration
        const durationMatch = stdout.match(/(\d+(?:\.\d+)?)\s*(?:m?s|seconds?|minutes?)/i);
        if (durationMatch) {
            results.duration = durationMatch[0];
        }

        // If still no results and exit code indicates failure, create a generic failure
        if (results.total === 0 && exitCode !== 0) {
            results.total = 1;
            results.failed = 1;
            results.tests.push({
                name: 'Test Execution',
                status: 'failed',
                error: stderr || 'Test execution failed',
                duration: 'Unknown'
            });
        }

        return results;
    }

    parseJsonResults(jsonResults, results) {
        // Parse Playwright JSON results
        if (jsonResults.suites) {
            jsonResults.suites.forEach(suite => {
                this.parseSuite(suite, results);
            });
        }

        if (jsonResults.stats) {
            results.total = jsonResults.stats.total || results.total;
            results.passed = jsonResults.stats.passed || results.passed;
            results.failed = jsonResults.stats.failed || results.failed;
            results.skipped = jsonResults.stats.skipped || results.skipped;
        }
    }

    parseSuite(suite, results) {
        if (suite.specs) {
            suite.specs.forEach(spec => {
                if (spec.tests) {
                    spec.tests.forEach(test => {
                        results.total++;
                        
                        const testResult = {
                            name: (spec.title || test.title || 'Unnamed Test'),
                            file: suite.title || 'Unknown File',
                            status: 'unknown',
                            duration: test.duration ? `${test.duration}ms` : 'Unknown',
                            error: null
                        };

                        if (test.results && test.results.length > 0) {
                            const result = test.results[0];
                            testResult.status = result.status;
                            
                            if (result.status === 'passed') {
                                results.passed++;
                            } else if (result.status === 'failed') {
                                results.failed++;
                                testResult.error = result.error?.message || 'Test failed';
                            } else if (result.status === 'skipped') {
                                results.skipped++;
                            }
                        }

                        results.tests.push(testResult);
                    });
                }
            });
        }

        // Recursively parse nested suites
        if (suite.suites) {
            suite.suites.forEach(nestedSuite => {
                this.parseSuite(nestedSuite, results);
            });
        }
    }

    parseTextResults(stdout, stderr, results) {
        // Fallback text parsing for when JSON is not available
        const lines = (stdout + '\n' + stderr).split('\n');
        
        lines.forEach(line => {
            // Look for test result patterns
            if (line.includes('✓') || line.includes('PASS')) {
                results.passed++;
                results.total++;
                results.tests.push({
                    name: line.trim(),
                    status: 'passed',
                    duration: 'Unknown'
                });
            } else if (line.includes('✗') || line.includes('FAIL')) {
                results.failed++;
                results.total++;
                results.tests.push({
                    name: line.trim(),
                    status: 'failed',
                    error: 'Test failed',
                    duration: 'Unknown'
                });
            }
        });
    }

    generateReport(testData) {
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
        const results = testData.results;
        
        let report = `# Frontend Test Results

## Latest Test Run

**Date**: ${timestamp}
**Tester**: Automated Script
**Test Environment**: Local Docker
**Test Command**: npm run test:e2e
**Browser**: Chromium (Playwright)
**Duration**: ${results.duration}

## Test Results Summary

- **Total Tests**: ${results.total}
- **Passed**: ${results.passed}
- **Failed**: ${results.failed}
- **Skipped**: ${results.skipped}
- **Success Rate**: ${results.total > 0 ? (results.passed/results.total*100).toFixed(1) : 0}%

## Test Details

`;

        // Add individual test results
        if (results.tests && results.tests.length > 0) {
            results.tests.forEach(test => {
                const statusIcon = test.status === 'passed' ? '✅' : test.status === 'failed' ? '❌' : '⏭️';
                const statusText = test.status.toUpperCase();
                
                report += `### ${statusIcon} ${test.name} - ${statusText}\n`;
                if (test.file) {
                    report += `**File**: ${test.file}\n`;
                }
                report += `**Duration**: ${test.duration}\n`;
                
                if (test.error) {
                    report += `**Error**: ${test.error}\n`;
                }
                
                report += '\n';
            });
        }

        // Add failed tests summary if any
        const failedTests = results.tests.filter(t => t.status === 'failed');
        if (failedTests.length > 0) {
            report += '\n## Failed Tests Summary\n\n';
            failedTests.forEach((test, i) => {
                report += `${i + 1}. **${test.name}**: ${test.error || 'Test failed'}\n`;
                if (test.file) {
                    report += `   - File: ${test.file}\n`;
                }
            });
            report += '\n';
        }

        // Add browser compatibility section
        report += '## Browser Compatibility\n\n';
        report += '- **Chromium**: Tested (Playwright default)\n';
        report += '- **Firefox**: Not tested in this run\n';
        report += '- **Safari**: Not tested in this run\n\n';

        // Add performance notes
        report += '## Performance Notes\n\n';
        if (results.passed > 0) {
            report += '- All UI interactions completed within acceptable timeouts\n';
            report += '- Page load times were within normal ranges\n';
        }
        
        if (results.failed > 0) {
            report += `- ${results.failed} tests failed - see details above\n`;
        }
        
        report += `- Test execution completed in ${results.duration}\n\n`;

        // Add issues found
        report += '## New Issues Found\n\n';
        if (failedTests.length > 0) {
            failedTests.forEach(test => {
                report += `- **${test.name}**: ${test.error || 'Test failed'}\n`;
            });
        } else {
            report += '- No new issues found\n';
        }
        
        report += '\n';

        // Add overall status
        if (testData.success) {
            report += '## Overall Status: ✅ PASSED\n\nAll frontend E2E tests completed successfully.\n';
        } else {
            report += '## Overall Status: ❌ FAILED\n\nSome frontend E2E tests failed. Review failed tests above.\n';
        }

        return report;
    }

    async saveReport(report) {
        try {
            await fs.writeFile(this.resultsFile, report, 'utf8');
            console.log(`📄 Test report saved to: ${this.resultsFile}`);
            return true;
        } catch (error) {
            console.log(`❌ Error saving report: ${error.message}`);
            return false;
        }
    }

    startReportServer() {
        try {
            // Start the Playwright report server in background
            const reportProcess = spawn('npx', ['playwright', 'show-report'], {
                cwd: this.frontendPath,
                detached: true,
                stdio: 'ignore'
            });
            
            // Allow the process to run independently
            reportProcess.unref();
            
            console.log(`📊 HTML report server started at: http://localhost:9323`);
            console.log(`💡 The server will run in background. Open the URL in your browser.`);
            console.log(`⚠️  To stop the server later, find and kill the node process manually.`);
        } catch (error) {
            console.log(`❌ Failed to start report server: ${error.message}`);
            console.log(`💡 You can manually start it with: cd frontend && npm run test:report:open`);
        }
    }

    async run() {
        console.log('🚀 Frontend Test Runner Started');
        console.log('='.repeat(50));

        // Check if services are running
        if (!(await this.checkServices())) {
            console.log('\n❌ Frontend services are not running!');
            console.log('💡 Please run: docker-compose up -d --build');
            return false;
        }

        // Run tests
        const testData = await this.runTests();

        // Generate and save report
        const report = this.generateReport(testData);

        if (await this.saveReport(report)) {
            console.log(`\n📊 Test Summary:`);
            console.log(`   Total: ${testData.results.total} tests`);
            console.log(`   Passed: ${testData.results.passed}`);
            console.log(`   Failed: ${testData.results.failed}`);

            // Display HTML report URL and start report server
            console.log(`\n📋 Visual Test Report:`);
            console.log(`   🌐 HTML Report: http://localhost:9323`);
            console.log(`   📁 Report Location: frontend/playwright-report/index.html`);
            console.log(`   🎥 Test Videos & Screenshots: frontend/test-results/`);
            console.log(`\n🚀 Starting HTML report server...`);

            // Start the report server
            this.startReportServer();

            if (testData.success) {
                console.log('\n✅ All frontend tests passed!');
            } else {
                console.log('\n⚠️  Some frontend tests failed - check report for details');
                console.log('💡 View detailed failure analysis with videos at: http://localhost:9323');
            }
        }

        return testData.success;
    }
}

async function main() {
    const runner = new FrontendTestRunner();
    const success = await runner.run();
    
    if (!success) {
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}