#!/usr/bin/env node
/**
 * Quick Frontend Test Runner
 * Runs a minimal set of frontend tests for fast feedback
 */

const { exec, spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class QuickTestRunner {
    constructor() {
        this.projectRoot = path.resolve(__dirname, '..');
        this.frontendPath = path.join(this.projectRoot, 'frontend');
        this.resultsFile = path.join(this.projectRoot, 'frontend_test_results.md');
    }

    async checkServices() {
        console.log('🔍 Quick service check...');
        
        try {
            const response = await this.fetchWithTimeout('http://localhost:3000', 3000);
            if (response) {
                console.log('✅ Frontend service is running');
                return true;
            } else {
                console.log('❌ Frontend service is not responding');
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

            exec(`curl -s -o /dev/null -w "%{http_code}" ${url}`, (error, stdout, stderr) => {
                clearTimeout(timer);
                if (error) {
                    reject(error);
                } else {
                    const statusCode = stdout.trim();
                    resolve(statusCode === '200' || statusCode === '404' || statusCode === '401');
                }
            });
        });
    }

    async runQuickTests() {
        console.log('\n🚀 Running quick frontend tests...');
        console.log('📋 Running auth and dashboard tests only');
        console.log('=' .repeat(50));

        return new Promise((resolve) => {
            // Run only specific test files for speed
            const testProcess = spawn('npm', ['run', 'test:e2e', '--', 
                '--reporter=json', 
                '--timeout=15000',
                '--project=chromium',
                'auth.spec.ts',
                'dashboard.spec.ts'
            ], {
                cwd: this.frontendPath,
                stdio: ['inherit', 'pipe', 'pipe']
            });

            // 60 second timeout for quick tests
            const processTimeout = setTimeout(() => {
                console.log('\n⚠️  Quick test timeout - killing process...');
                testProcess.kill('SIGTERM');
                setTimeout(() => {
                    if (!testProcess.killed) {
                        testProcess.kill('SIGKILL');
                    }
                }, 3000);
            }, 60000);

            let stdoutData = '';
            let stderrData = '';

            testProcess.stdout.on('data', (data) => {
                const output = data.toString();
                stdoutData += output;
                process.stdout.write(data);
            });

            testProcess.stderr.on('data', (data) => {
                const output = data.toString();
                stderrData += output;
                process.stderr.write(data);
            });

            testProcess.on('close', (code) => {
                clearTimeout(processTimeout);
                console.log('\n🏁 Quick tests completed!');
                
                const results = this.parseResults(stdoutData, stderrData, code);
                
                resolve({
                    success: code === 0,
                    results: results
                });
            });

            testProcess.on('exit', (code, signal) => {
                clearTimeout(processTimeout);
                if (signal === 'SIGTERM' || signal === 'SIGKILL') {
                    console.log(`\n💀 Quick test terminated (${signal})`);
                    resolve({
                        success: false,
                        results: {
                            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
                            total: 1,
                            passed: 0,
                            failed: 1,
                            skipped: 0,
                            duration: 'Timeout',
                            tests: [{
                                name: 'Quick Test Execution',
                                status: 'failed',
                                error: 'Quick test execution timed out',
                                duration: 'Timeout'
                            }]
                        }
                    });
                }
            });
        });
    }

    parseResults(stdout, stderr, exitCode) {
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        
        // Try to parse JSON output
        let jsonResults = null;
        try {
            const jsonMatch = stdout.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                jsonResults = JSON.parse(jsonMatch[0]);
            }
        } catch (e) {
            // Fallback parsing
        }

        const results = {
            timestamp: timestamp,
            total: 0,
            passed: 0,
            failed: 0,
            skipped: 0,
            duration: 'Unknown',
            tests: []
        };

        if (jsonResults && jsonResults.stats) {
            results.total = jsonResults.stats.expected + jsonResults.stats.unexpected || 0;
            results.passed = jsonResults.stats.expected || 0;
            results.failed = jsonResults.stats.unexpected || 0;
            results.skipped = jsonResults.stats.skipped || 0;
        }

        return results;
    }

    async generateQuickReport(testData) {
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
        const results = testData.results;
        
        const report = `# Frontend Test Results (Quick Test)

## Latest Test Run

**Date**: ${timestamp}
**Tester**: Quick Test Script
**Test Environment**: Local Docker
**Test Command**: npm run test:e2e (auth + dashboard only)
**Browser**: Chromium (Playwright)
**Duration**: ${results.duration}

## Test Results Summary

- **Total Tests**: ${results.total}
- **Passed**: ${results.passed}
- **Failed**: ${results.failed}
- **Skipped**: ${results.skipped}
- **Success Rate**: ${results.total > 0 ? (results.passed/results.total*100).toFixed(1) : 0}%

## Test Scope

This was a **quick test run** focusing on:
- Authentication tests (login/logout)
- Dashboard functionality tests

For comprehensive testing, use: \`node scripts/run_frontend_tests.js\`

## Overall Status: ${testData.success ? '✅ PASSED' : '❌ FAILED'}

${testData.success ? 'Quick tests passed successfully.' : 'Quick tests found issues - run full test suite for details.'}
`;

        return report;
    }

    async saveReport(report) {
        try {
            await fs.writeFile(this.resultsFile, report, 'utf8');
            console.log(`📄 Quick test report saved to: ${this.resultsFile}`);
            return true;
        } catch (error) {
            console.log(`❌ Error saving report: ${error.message}`);
            return false;
        }
    }

    async run() {
        console.log('⚡ Quick Frontend Test Runner Started');
        console.log('='.repeat(40));

        // Check if services are running
        if (!(await this.checkServices())) {
            console.log('\n❌ Frontend services are not running!');
            return false;
        }

        // Run quick tests
        const testData = await this.runQuickTests();

        // Generate and save report
        const report = await this.generateQuickReport(testData);

        if (await this.saveReport(report)) {
            console.log(`\n📊 Quick Test Summary:`);
            console.log(`   Total: ${testData.results.total} tests`);
            console.log(`   Passed: ${testData.results.passed}`);
            console.log(`   Failed: ${testData.results.failed}`);

            if (testData.success) {
                console.log('\n✅ Quick tests passed!');
            } else {
                console.log('\n⚠️  Quick tests found issues');
            }
        }

        return testData.success;
    }
}

async function main() {
    const runner = new QuickTestRunner();
    const success = await runner.run();
    
    if (!success) {
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}