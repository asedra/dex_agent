---
description: "Implement backend development tasks from Jira with task ID parameter"
shortcut: "bed"
arguments: true
---

# Backend Developer

Implement specific backend development tasks from Jira by providing the task ID.

## Usage

```bash
/backend-developer [task-id]         # Implement backend task
/bed [task-id]                       # Shortcut for backend developer
```

## Backend Task Implementation

### 1. Task Loading & Analysis

⚙️ **Backend Developer Mode**
========================

**Task ID Required**: Please provide a task ID to implement backend features.

📋 **Loading task**: $ARGUMENTS  
🔄 **Analyzing backend requirements**...  
⚙️ **Starting backend implementation**...

Task ID: **$ARGUMENTS**  
Implementation Type: **Backend Development**

### 2. Implementation Workflow

Based on the task details from Jira, the implementation will include:

#### API Development
- **Endpoint Creation**: Build RESTful API endpoints with proper HTTP methods
- **Request Validation**: Input validation, sanitization, and error handling
- **Response Format**: Consistent JSON responses with proper status codes
- **Authentication**: JWT/OAuth2 integration and middleware setup

#### Business Logic Implementation
- **Service Layer**: Business logic separation and service patterns
- **Data Processing**: Complex calculations and data transformations
- **Integration Services**: Third-party API integrations and webhooks
- **Background Jobs**: Async processing with queues and scheduled tasks

#### Database Integration
- **ORM Setup**: Database connection and model configuration
- **Query Optimization**: Efficient database queries and indexing
- **Migration Scripts**: Schema changes and data migrations
- **Transaction Management**: ACID compliance and data integrity

### 3. Development Steps

🔧 **Implementation Process**:

1. **Task Analysis**: Load task details and API specifications
2. **Environment Setup**: Configure development database and services
3. **API Development**: Build endpoints according to specifications
4. **Business Logic**: Implement core functionality and data processing
5. **Database Integration**: Set up models and optimize queries
6. **Testing**: Write unit tests and API integration tests
7. **Documentation**: Generate OpenAPI/Swagger documentation

### 4. Code Implementation

#### API Endpoint Structure
```javascript
// Example Express.js endpoint implementation
const express = require('express');
const router = express.Router();

// GET endpoint with validation and error handling
router.get('/api/resource/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Input validation
    if (!id || isNaN(id)) {
      return res.status(400).json({ 
        error: 'Invalid ID parameter' 
      });
    }

    // Business logic implementation
    const result = await resourceService.getById(id);
    
    if (!result) {
      return res.status(404).json({ 
        error: 'Resource not found' 
      });
    }

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ 
      error: 'Internal server error' 
    });
  }
});
```

#### Service Layer Implementation
```javascript
// Business logic service
class ResourceService {
  async getById(id) {
    // Database query with error handling
    const resource = await Resource.findByPk(id, {
      include: ['relatedEntities']
    });
    
    if (!resource) {
      return null;
    }

    // Data transformation and business logic
    return this.transformResource(resource);
  }

  transformResource(resource) {
    // Apply business rules and data formatting
    return {
      id: resource.id,
      name: resource.name,
      status: resource.status,
      // Additional transformation logic
    };
  }
}
```

#### Testing Implementation
```javascript
// API endpoint tests
const request = require('supertest');
const app = require('../app');

describe('GET /api/resource/:id', () => {
  test('should return resource when valid ID provided', async () => {
    const response = await request(app)
      .get('/api/resource/1')
      .expect(200);

    expect(response.body).toHaveProperty('success', true);
    expect(response.body.data).toHaveProperty('id', 1);
  });

  test('should return 404 when resource not found', async () => {
    const response = await request(app)
      .get('/api/resource/999')
      .expect(404);

    expect(response.body).toHaveProperty('error', 'Resource not found');
  });
});
```

### 5. Task Completion Validation

✅ **Implementation Checklist**:
- [ ] All API endpoints implemented according to specifications
- [ ] Input validation and error handling complete
- [ ] Business logic tested and working correctly
- [ ] Database integration optimized and secure
- [ ] API tests written and passing (90%+ coverage)
- [ ] OpenAPI/Swagger documentation generated
- [ ] Security audit passed (authentication, authorization)
- [ ] Performance benchmarks met

### 6. Integration with Development Tools

#### Build & Development
- Run `npm run dev` or equivalent for development server
- Execute `npm run test` for API testing
- Use `npm run docs` for API documentation generation

#### Database Management
- Run `npm run migrate` for database migrations
- Execute `npm run seed` for test data population
- Use `npm run db:reset` for database reset

## Example Usage

```bash
# Implement specific backend task
/backend-developer KAN-26
📋 Loading task: KAN-26 - "User Dashboard Analytics - BE"
⚙️ Implementing API endpoints...
✅ Endpoints created: GET /api/analytics, POST /api/analytics/filter
🗄️ Database models configured and optimized
🧪 API tests written and passing (94% coverage)
📋 OpenAPI documentation generated
🚀 Ready for integration testing
```

## Error Handling

- **Missing Task ID**: Prompts for required task parameter
- **Task Not Found**: Searches for similar task IDs in project
- **Database Connection Issues**: Guides through database setup
- **API Integration Errors**: Provides debugging and troubleshooting

## Integration Features

- **Jira Integration**: Automatic task status updates and progress tracking
- **Database Integration**: Automated migration and seeding
- **API Documentation**: Auto-generated OpenAPI/Swagger specs
- **Testing Integration**: Automated test running and coverage reporting

**Ready to implement backend tasks efficiently with comprehensive API development workflow!**