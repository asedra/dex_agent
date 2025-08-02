---
description: "Implement QA engineering tasks from Jira with task ID parameter"
shortcut: "qae"
arguments: true
---

# QA Engineer

Implement specific QA engineering tasks from Jira by providing the task ID.

## Usage

```bash
/qa-engineer [task-id]               # Implement QA task
/qae [task-id]                       # Shortcut for QA engineer
```

## QA Task Implementation

### 1. Task Loading & Analysis

🧪 **QA Engineer Mode**
==================

**Task ID Required**: Please provide a task ID to implement QA testing.

📋 **Loading task**: $ARGUMENTS  
🔄 **Analyzing QA requirements**...  
🧪 **Starting QA implementation**...

Task ID: **$ARGUMENTS**  
Implementation Type: **Quality Assurance**

### 2. Implementation Workflow

Based on the task details from Jira, the implementation will include:

#### Test Strategy Development
- **Test Plan Creation**: Comprehensive test strategy and scope definition
- **Test Case Design**: Functional, integration, and edge case scenarios
- **Risk Assessment**: Quality risk analysis and mitigation strategies
- **Test Data Management**: Create and manage test data sets

#### Test Automation Implementation
- **E2E Test Automation**: User journey automation with Cypress/Playwright
- **API Testing**: RESTful API testing with Postman/Newman
- **Unit Test Support**: Integration with developer testing practices
- **Regression Testing**: Automated regression test suite development

#### Quality Validation Execution
- **Manual Testing**: Exploratory testing and usability validation
- **Performance Testing**: Load testing and performance benchmarking
- **Security Testing**: Vulnerability assessment and penetration testing
- **Accessibility Testing**: WCAG compliance and screen reader validation

### 3. Development Steps

🔧 **Implementation Process**:

1. **Task Analysis**: Load task details and testing requirements
2. **Test Planning**: Create comprehensive test strategy
3. **Test Development**: Write automated and manual test cases
4. **Test Environment**: Set up testing environments and data
5. **Test Execution**: Run tests and collect results
6. **Defect Management**: Report and track bugs through resolution
7. **Quality Reporting**: Generate test reports and metrics

### 4. Code Implementation

#### E2E Test Automation Example
```javascript
// Cypress E2E test implementation
describe('User Dashboard Analytics', () => {
  beforeEach(() => {
    cy.login('test.user@example.com', 'testpassword');
    cy.visit('/dashboard/analytics');
  });

  it('should display analytics dashboard correctly', () => {
    // Verify main dashboard elements
    cy.get('[data-testid="analytics-dashboard"]').should('be.visible');
    cy.get('[data-testid="chart-container"]').should('exist');
    cy.get('[data-testid="data-table"]').should('be.visible');
    
    // Verify data loading
    cy.get('[data-testid="loading-spinner"]').should('not.exist');
    cy.get('[data-testid="chart-container"]').within(() => {
      cy.get('canvas').should('be.visible');
    });
  });

  it('should filter analytics data correctly', () => {
    // Test date range filter
    cy.get('[data-testid="date-filter"]').click();
    cy.get('[data-testid="last-30-days"]').click();
    
    // Verify API call and data update
    cy.intercept('GET', '/api/analytics*').as('getAnalytics');
    cy.get('[data-testid="apply-filter"]').click();
    cy.wait('@getAnalytics');
    
    // Verify filtered results
    cy.get('[data-testid="data-table"]').should('contain', 'Last 30 days');
  });

  it('should handle error states gracefully', () => {
    // Mock API error
    cy.intercept('GET', '/api/analytics*', { statusCode: 500 }).as('getAnalyticsError');
    cy.reload();
    cy.wait('@getAnalyticsError');
    
    // Verify error handling
    cy.get('[data-testid="error-message"]').should('be.visible');
    cy.get('[data-testid="retry-button"]').should('be.visible');
  });
});
```

#### API Testing Example
```javascript
// Newman/Postman API test collection
const newman = require('newman');

newman.run({
  collection: {
    info: { name: 'Analytics API Tests' },
    item: [
      {
        name: 'Get Analytics Data',
        request: {
          method: 'GET',
          url: '{{baseUrl}}/api/analytics',
          header: [
            {
              key: 'Authorization',
              value: 'Bearer {{authToken}}'
            }
          ]
        },
        event: [
          {
            listen: 'test',
            script: {
              exec: [
                'pm.test("Status code is 200", function () {',
                '    pm.response.to.have.status(200);',
                '});',
                'pm.test("Response has data property", function () {',
                '    const jsonData = pm.response.json();',
                '    pm.expect(jsonData).to.have.property("data");',
                '});'
              ]
            }
          }
        ]
      }
    ]
  },
  environment: {
    values: [
      { key: 'baseUrl', value: 'http://localhost:3000' },
      { key: 'authToken', value: 'test-token' }
    ]
  }
}, (err, summary) => {
  if (err) throw err;
  console.log('API tests completed');
});
```

#### Performance Testing Example
```javascript
// K6 performance testing script
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 50, // 50 virtual users
  duration: '5m', // Run for 5 minutes
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_rate: ['rate>100'], // More than 100 requests per second
    http_req_failed: ['rate<0.01'], // Less than 1% errors
  },
};

export default function() {
  const response = http.get('http://localhost:3000/api/analytics', {
    headers: { 'Authorization': 'Bearer test-token' },
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has analytics data': (r) => JSON.parse(r.body).data !== undefined,
  });
  
  sleep(1);
}
```

### 5. Task Completion Validation

✅ **Implementation Checklist**:
- [ ] Test strategy document created and approved
- [ ] All test cases written and reviewed
- [ ] Automated test suite implemented and passing
- [ ] Manual testing completed with documented results
- [ ] Performance testing executed with benchmarks met
- [ ] Security testing completed with no critical issues
- [ ] Accessibility testing passed WCAG 2.1 AA compliance
- [ ] Defect tracking and resolution completed

### 6. Integration with Development Tools

#### Test Execution
- Run `npm run test:e2e` for end-to-end testing
- Execute `npm run test:api` for API testing
- Use `npm run test:performance` for load testing
- Run `npm run test:accessibility` for accessibility validation

#### Quality Reporting
- Generate test reports with `npm run test:report`
- Create coverage reports with `npm run coverage`
- Export performance metrics to monitoring tools
- Update quality dashboards with test results

## Example Usage

```bash
# Implement specific QA task
/qa-engineer KAN-32
📋 Loading task: KAN-32 - "User Dashboard Analytics - QA"
🧪 Implementing test strategy...
✅ E2E tests created: 15 test scenarios covering main user flows
🔧 API tests implemented: 25 endpoint validations
⚡ Performance tests configured: Load testing for 50 concurrent users
🛡️ Security tests executed: OWASP Top 10 vulnerability assessment
♿ Accessibility tests passed: WCAG 2.1 AA compliance validated
📊 Test coverage: 94% overall coverage achieved
🚀 Ready for production deployment validation
```

## Error Handling

- **Missing Task ID**: Prompts for required task parameter
- **Task Not Found**: Searches for similar task IDs in project
- **Test Environment Issues**: Guides through environment setup
- **Test Failures**: Provides debugging guidance and resolution steps

## Integration Features

- **Jira Integration**: Automatic defect creation and test execution tracking
- **CI/CD Integration**: Automated test execution in deployment pipeline
- **Quality Metrics**: Real-time quality dashboards and reporting
- **Team Collaboration**: Test result sharing and defect triage workflows

**Ready to implement QA tasks efficiently with comprehensive testing workflow and quality assurance!**