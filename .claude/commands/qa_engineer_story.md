---
description: "Create detailed QA engineering tasks for a specific story with testing strategies, automation, and quality assurance requirements"
shortcut: "qae"
arguments: true
---

# QA Engineer

Create comprehensive QA engineering tasks for an existing story with detailed testing strategies, automation frameworks, and quality assurance specifications.

## Usage

```bash
/qa-engineer [story-id]              # Create QA tasks for story
/qae [story-id]                      # Shortcut for QA engineer
```

## QA Task Creation

### 1. Story Context Loading

🧪 **QA Engineer Mode**
==================

**Story ID Required**: Please provide a story ID to create QA tasks.

**Usage**: `/qa-engineer [story-id]` or `/qae [story-id]`

Story ID: **$ARGUMENTS**  
Task Type: **Quality Assurance**

### 2. QA Task Generation

Based on the original story from `/create-story`, detailed QA tasks will be created:

#### Test Strategy & Planning
- **Test Plan Development**: Comprehensive test strategy and scope definition
- **Risk Assessment**: Quality risk analysis and mitigation strategies
- **Test Case Design**: Functional, non-functional, and edge case scenarios
- **Test Data Management**: Test data creation, management, and maintenance

#### Test Automation
- **Automation Framework**: Test automation setup and framework development
- **Unit Test Support**: Integration with developer unit testing practices
- **Integration Testing**: API testing and service integration validation
- **End-to-End Testing**: User journey automation and regression testing

#### Quality Validation
- **Manual Testing**: Exploratory testing and usability validation
- **Performance Testing**: Load, stress, and scalability testing
- **Security Testing**: Vulnerability assessment and penetration testing
- **Accessibility Testing**: WCAG compliance and assistive technology validation

### 3. Cross-Team Dependencies

🔗 **QA Cross-Team Dependencies Analysis**

Each QA task includes detailed dependency tracking:

#### Dependencies FROM Other Teams:
```
## Cross-Team Dependencies

### Requires:
- /frontend-developer - Testable components with data-testid attributes
- /frontend-developer - Component documentation and usage examples
- /backend-developer - API documentation and test endpoints
- /backend-developer - Health check endpoints and monitoring capabilities
- /database-developer - Test database setup and data seeding procedures
- /ux-designer - Usability testing scenarios and accessibility requirements
- /devops-engineer - Testing environments and deployment validation
- /ai-developer - Model testing frameworks and performance benchmarks

### Testing Requirements:
- Test environment setup and configuration
- Test data generation and management tools
- Performance benchmarking and load testing infrastructure
- Security testing tools and vulnerability scanners
- Accessibility testing tools and screen reader setup
```

#### Dependencies TO Other Teams:
```
### Provides:
- /frontend-developer - Component testing feedback and bug reports
- /backend-developer - API testing results and performance validation
- /database-developer - Data integrity testing and query performance feedback
- /ux-designer - Usability testing results and accessibility compliance reports
- /devops-engineer - Deployment validation and environment testing feedback
- /ai-developer - Model performance validation and accuracy testing results

### QA Deliverables:
- Comprehensive test strategy and execution reports
- Automated test suites with continuous integration
- Performance and load testing benchmarks
- Security testing reports and vulnerability assessments
- Accessibility compliance validation and reports
- Quality metrics and defect tracking dashboard
```

### 4. Technical Specifications

⚙️ **QA Technical Specifications**

#### Testing Standards
- **Automation Framework**: Cypress/Playwright/Selenium for E2E testing
- **API Testing**: Postman/Newman/REST Assured for API validation
- **Performance Testing**: JMeter/K6/Artillery for load and stress testing
- **Security Testing**: OWASP ZAP/Burp Suite for vulnerability assessment

#### Quality Requirements
- **Test Coverage**: Minimum 80% code coverage for critical paths
- **Automation Rate**: 70% of regression tests automated
- **Performance Standards**: Response time and throughput benchmarks
- **Security Standards**: OWASP Top 10 vulnerability assessment

#### Testing Documentation
- **Test Cases**: Detailed test scenarios with expected outcomes
- **Test Data**: Reusable test data sets and generation procedures
- **Bug Reports**: Standardized defect reporting and tracking
- **Quality Metrics**: Test execution reports and quality dashboards

### 5. Task Creation in Jira

📝 **QA Task Creation in Jira**

**Task Format:**
- **Title**: `[Story Name] - QA`
- **Type**: Task (linked to parent story)
- **Labels**: `qa`, `testing`, `automation`, `performance`, `security`
- **Dependencies**: Cross-team dependencies tracked

**Task Details Created:**
- **Title Format**: `[Story Name] - QA`
- **Issue Type**: Task (linked to parent story)
- **Labels**: `qa`, `testing`, `automation`, `performance`, `security`, `accessibility`
- **Priority**: Based on story priority and quality risk assessment
- **Story Points**: Estimated based on testing complexity and automation requirements

#### Task Description Template:
```markdown
# QA Engineering Task

## Story Context
Original Story: [STORY_ID] - [STORY_TITLE]
Related to: [PARENT_EPIC_IF_EXISTS]

## QA Requirements
- Comprehensive test strategy development and execution
- Test automation framework implementation and maintenance
- Performance, security, and accessibility testing validation
- Quality assurance processes and continuous improvement

## Technical Specifications
### Testing Framework & Tools
- E2E Testing: [Cypress/Playwright/Selenium]
- API Testing: [Postman/Newman/REST Assured]
- Performance Testing: [JMeter/K6/Artillery]
- Security Testing: [OWASP ZAP/Burp Suite]
- Accessibility Testing: [axe-core/WAVE/Lighthouse]

### Quality Standards
- Test Coverage: Minimum 80% for critical user journeys
- Automation Coverage: 70% of regression tests automated
- Performance SLA: 95th percentile response time < 500ms
- Security Compliance: OWASP Top 10 vulnerability assessment

## Test Strategy & Planning

### Test Scope:
- **Functional Testing**: Core feature functionality and business logic
- **Integration Testing**: API endpoints and service interactions
- **User Interface Testing**: UI components and user interactions
- **Data Testing**: Data integrity and database operations
- **Performance Testing**: Load, stress, and scalability validation
- **Security Testing**: Authentication, authorization, and vulnerability assessment
- **Accessibility Testing**: WCAG 2.1 AA compliance validation

### Risk Assessment:
- **High Risk Areas**: [Critical user flows and data operations]
- **Medium Risk Areas**: [Secondary features and integrations]
- **Low Risk Areas**: [UI cosmetic changes and minor enhancements]

### Testing Approach:
- **Shift-Left**: Early testing integration in development cycle
- **Risk-Based**: Focus testing effort on high-risk areas
- **Continuous**: Automated testing in CI/CD pipeline
- **Exploratory**: Manual exploratory testing for edge cases

## Test Case Development

### Functional Test Cases:
```gherkin
# Example test scenarios using Gherkin syntax
Feature: [Story Feature Name]

Scenario: User successfully [performs main action]
  Given the user is on the [page/screen]
  When they [perform action]
  Then they should see [expected result]
  And the system should [expected behavior]

Scenario: Error handling for [error condition]
  Given the user has [precondition]
  When they [trigger error condition]
  Then they should see [error message]
  And the system should [recovery action]
```

### API Test Cases:
```javascript
// Example API test cases with Postman/Newman
describe('[API Endpoint Name]', () => {
  test('Should return successful response for valid request', async () => {
    const response = await request(app)
      .get('/api/[endpoint]')
      .set('Authorization', 'Bearer [token]')
      .expect(200);
    
    expect(response.body).toHaveProperty('[expected_field]');
    expect(response.body.[field]).toBe('[expected_value]');
  });
  
  test('Should return error for invalid request', async () => {
    const response = await request(app)
      .post('/api/[endpoint]')
      .send({ invalid: 'data' })
      .expect(400);
    
    expect(response.body.error).toContain('[expected_error]');
  });
});
```

## Test Automation Implementation

### E2E Test Automation:
```javascript
// Example Cypress/Playwright test automation
describe('[Story Feature] E2E Tests', () => {
  beforeEach(() => {
    cy.login('[test_user]');
    cy.visit('/[feature_page]');
  });

  it('should complete main user journey', () => {
    cy.get('[data-testid="main-action"]').click();
    cy.get('[data-testid="form-input"]').type('[test_data]');
    cy.get('[data-testid="submit-button"]').click();
    
    cy.get('[data-testid="success-message"]')
      .should('be.visible')
      .and('contain', '[expected_message]');
  });

  it('should handle error scenarios gracefully', () => {
    cy.get('[data-testid="error-trigger"]').click();
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', '[expected_error]');
  });
});
```

### Performance Test Automation:
```javascript
// Example K6 performance testing script
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 50, // 50 virtual users
  duration: '5m', // Run for 5 minutes
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_rate: ['rate>100'], // More than 100 requests per second
  },
};

export default function() {
  let response = http.get('[API_ENDPOINT]');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

## Cross-Team Dependencies

### Requires:
- /frontend-developer - Testable components with proper data attributes
- /backend-developer - API documentation and test endpoints
- /devops-engineer - Testing environments and CI/CD integration

### Provides:
- /frontend-developer - UI testing feedback and component validation
- /backend-developer - API testing results and performance benchmarks
- /devops-engineer - Deployment validation and quality gates

### Blocking/Blocked Status:
- BLOCKS: Production deployment (quality validation required)
- BLOCKED BY: Feature implementation (frontend/backend) and test environment setup

## Test Data Management

### Test Data Strategy:
- **Synthetic Data**: Generated test data for consistent testing
- **Anonymized Production Data**: Realistic data for integration testing
- **Edge Case Data**: Boundary values and error condition testing
- **Performance Data**: Large datasets for scalability testing

### Test Environment Management:
- **Development**: Continuous testing during development
- **Staging**: Pre-production validation and integration testing
- **Performance**: Dedicated environment for load and stress testing
- **Security**: Isolated environment for security and vulnerability testing

## Quality Metrics & Reporting

### Test Execution Metrics:
- **Test Coverage**: Percentage of code/requirements covered by tests
- **Pass/Fail Rate**: Test execution success rate over time
- **Defect Density**: Number of defects per feature/module
- **Automation Rate**: Percentage of tests automated vs manual

### Performance Benchmarks:
- **Response Time**: 95th percentile response time < 500ms
- **Throughput**: Minimum [X] requests per second
- **Resource Usage**: CPU and memory utilization under load
- **Error Rate**: Less than 0.1% error rate under normal load

### Security Testing Results:
- **Vulnerability Assessment**: OWASP Top 10 compliance
- **Penetration Testing**: Security testing results and remediation
- **Authentication Testing**: Login and session management validation
- **Authorization Testing**: Role-based access control validation

## Acceptance Criteria
- [ ] Test strategy developed and approved by stakeholders
- [ ] Test cases created covering all functional requirements
- [ ] Test automation framework implemented and integrated
- [ ] Performance testing completed with benchmarks met
- [ ] Security testing completed with no critical vulnerabilities
- [ ] Accessibility testing completed with WCAG 2.1 AA compliance
- [ ] Defect tracking and resolution process established
- [ ] Quality metrics dashboard created and operational

## Definition of Done
- [ ] Test plan reviewed and approved by team
- [ ] All test cases executed with acceptable pass rate
- [ ] Automation suite integrated into CI/CD pipeline
- [ ] Performance benchmarks validated and documented
- [ ] Security assessment completed and approved
- [ ] Accessibility compliance verified and documented
- [ ] Quality metrics collected and reported
- [ ] Production readiness validated and signed off
```

### 6. Integration Features

#### Story Integration
- Links to parent story issue created by `/create-story`
- Inherits story context and quality requirements
- Maintains traceability to original testing narrative

#### Test Management Integration
- Manages test case repository and execution tracking
- Tracks defect lifecycle and resolution status
- Integrates with CI/CD pipeline for automated testing
- Maintains quality metrics and reporting dashboard

#### Cross-Team Quality Integration
- Validates frontend component testability
- Monitors backend API performance and reliability
- Assesses infrastructure stability and scalability
- Ensures overall system quality and user experience

## Example Usage

```bash
# After creating story with /create-story
/story-analysis KAN-15
# Activates role-specific commands

/qa-engineer KAN-15
✅ Created: "User Dashboard Analytics - QA" (KAN-32)
📝 Dependencies: Frontend components (KAN-25), Backend APIs (KAN-26)
🔗 Linked to parent story: KAN-15
🧪 Testing: E2E automation, performance validation, security assessment
```

## Error Handling

- **Missing Story ID**: Prompts for required story parameter
- **Story Not Found**: Searches for similar story IDs
- **Duplicate QA Task**: Shows existing task, prevents duplicates
- **Missing Test Dependencies**: Warns about required component testability

## Next Steps

After creating QA tasks:
1. Review test strategy in Jira web interface
2. Coordinate with development teams for testability requirements
3. Set up test automation framework and CI/CD integration
4. Plan performance and security testing execution

**Ready to create detailed QA engineering tasks with comprehensive testing strategies and cross-team collaboration!**