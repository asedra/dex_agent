---
description: "Create detailed backend development tasks for a specific story with API specifications and cross-team dependencies"
shortcut: "bed"
arguments: true
---

# Backend Developer

Create comprehensive backend development tasks for an existing story with detailed API specifications and cross-team collaboration tracking.

## Usage

```bash
/backend-developer [story-id]        # Create backend tasks for story
/bed [story-id]                      # Shortcut for backend developer
```

## Backend Task Creation

### 1. Story Context Loading

⚙️ **Backend Developer Mode**
========================

**Story ID Required**: Please provide a story ID to create backend tasks.

**Usage**: `/backend-developer [story-id]` or `/bed [story-id]`

Story ID: **$ARGUMENTS**  
Task Type: **Backend Development**

### 2. Backend Task Generation

Based on the original story from `/create-story`, detailed backend tasks will be created:

#### API Development
- **RESTful API Design**: Resource-based API endpoints with proper HTTP methods
- **API Documentation**: OpenAPI/Swagger specifications with examples
- **Authentication & Authorization**: JWT/OAuth2 implementation with role-based access
- **Data Validation**: Input validation, sanitization, and error handling

#### Business Logic Implementation
- **Service Layer**: Business logic separation and service patterns
- **Data Processing**: Complex data transformations and calculations
- **Integration Services**: Third-party API integrations and webhooks
- **Background Jobs**: Async processing, queues, and scheduled tasks

#### Performance & Scalability
- **Database Optimization**: Query optimization and connection pooling
- **Caching Strategy**: Redis/Memcached integration for performance
- **Rate Limiting**: API throttling and abuse prevention
- **Monitoring & Logging**: Application monitoring and structured logging

### 3. Cross-Team Dependencies

🔗 **Cross-Team Dependencies Analysis**

Each backend task includes detailed dependency tracking:

#### Dependencies FROM Other Teams:
```
## Cross-Team Dependencies

### Requires:
- /database-developer - Database schema design and migrations
- /database-developer - Optimized queries and stored procedures
- /frontend-developer - API requirements and data format specifications
- /ai-developer - ML model integration endpoints and inference requirements
- /devops-engineer - Environment configurations and deployment pipelines

### Infrastructure Requirements:
- Database connection configurations
- External service credentials and API keys
- Environment-specific configuration management
- Load balancing and scaling requirements
- Monitoring and alerting infrastructure
```

#### Dependencies TO Other Teams:
```
### Provides:
- /frontend-developer - RESTful API endpoints with comprehensive documentation
- /frontend-developer - WebSocket connections for real-time data streaming
- /ai-developer - Data preprocessing APIs and model training endpoints
- /qa-engineer - API testing endpoints and mock data services
- /devops-engineer - Application health checks and deployment configurations

### Backend Deliverables:
- Complete API documentation (OpenAPI/Swagger)
- Database interaction layer and ORM configurations
- Authentication and authorization middleware
- Error handling and logging framework
- Performance monitoring and metrics endpoints
```

### 4. Technical Specifications

⚙️ **Backend Technical Specifications**

#### Development Standards
- **Framework**: Express.js/FastAPI/Spring Boot (based on project tech stack)
- **Language**: Node.js/Python/Java with TypeScript/type hints
- **Database**: PostgreSQL/MongoDB integration with ORM/ODM
- **Testing**: Unit tests, integration tests, and API contract testing

#### Architecture Requirements
- **Clean Architecture**: Separation of concerns with layers
- **Database Layer**: Repository pattern and data access layer
- **Security**: Input validation, SQL injection prevention, HTTPS enforcement
- **Error Handling**: Centralized error handling with proper HTTP status codes

#### API Standards
- **RESTful Design**: Resource-based URLs with proper HTTP methods
- **Response Format**: Consistent JSON response structure with metadata
- **Pagination**: Cursor or offset-based pagination for large datasets
- **Versioning**: API versioning strategy for backward compatibility

### 5. Task Creation in Jira

📝 **Backend Task Creation in Jira**

**Task Format:**
- **Title**: `[Story Name] - BE`
- **Type**: Task (linked to parent story)
- **Labels**: `backend`, `api`, `database`, `authentication`
- **Dependencies**: Cross-team dependencies tracked

**Task Details Created:**
- **Title Format**: `[Story Name] - BE`
- **Issue Type**: Task (linked to parent story)
- **Labels**: `backend`, `api`, `database`, `microservice`, `nodejs`
- **Priority**: Based on story priority
- **Story Points**: Estimated based on API complexity

#### Task Description Template:
```markdown
# Backend Development Task

## Story Context
Original Story: [STORY_ID] - [STORY_TITLE]
Related to: [PARENT_EPIC_IF_EXISTS]

## Backend Requirements
- API endpoint design and implementation
- Business logic development and data processing
- Database integration and query optimization
- Authentication, authorization, and security implementation

## Technical Specifications
### Framework & Tools
- Backend Framework: [Express.js/FastAPI/Spring Boot]
- Language: [Node.js/Python/Java] with [TypeScript/type hints]
- Database: [PostgreSQL/MongoDB] with [Prisma/Mongoose/Hibernate]
- Testing: [Jest/Pytest/JUnit] with API contract testing

### API Requirements
- RESTful API design with proper HTTP methods
- OpenAPI/Swagger documentation with examples
- Authentication and authorization middleware
- Input validation and error handling
- Rate limiting and security headers

## API Endpoints Specification

### Core Endpoints:
- GET /api/[resource] - List resources with pagination
- GET /api/[resource]/:id - Get specific resource
- POST /api/[resource] - Create new resource
- PUT /api/[resource]/:id - Update resource
- DELETE /api/[resource]/:id - Delete resource

### Authentication Endpoints:
- POST /api/auth/login - User authentication
- POST /api/auth/refresh - Token refresh
- POST /api/auth/logout - User logout
- GET /api/auth/profile - User profile

## Cross-Team Dependencies

### Requires:
- /database-developer - Schema design and optimized queries
- /frontend-developer - API requirements and data format needs
- /devops-engineer - Environment configuration and deployment setup

### Provides:
- /frontend-developer - Complete API documentation and endpoints
- /ai-developer - Data processing APIs and ML model integration points
- /qa-engineer - API testing endpoints and comprehensive test data

### Blocking/Blocked Status:
- BLOCKS: Frontend development (API endpoints required)
- BLOCKED BY: Database schema (must be designed first)

## Database Integration
- ORM/ODM setup and configuration
- Database connection pooling and optimization
- Migration scripts and seed data
- Query optimization and indexing strategy

## Security Requirements
- JWT token-based authentication
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection and XSS prevention
- Rate limiting and DDoS protection

## Performance Requirements
- API response time < 200ms for simple queries
- Database connection pooling for concurrency
- Caching strategy for frequently accessed data
- Async processing for heavy operations

## Acceptance Criteria
- [ ] All API endpoints implemented and documented
- [ ] Authentication and authorization working correctly
- [ ] Database integration with optimized queries
- [ ] Input validation and error handling complete
- [ ] API tests achieving 90%+ coverage
- [ ] Security audit passed (no critical vulnerabilities)
- [ ] Performance benchmarks met (response times)
- [ ] Integration with frontend successful

## Definition of Done
- [ ] Code review completed and approved
- [ ] Unit and integration tests passing
- [ ] API documentation complete and accurate
- [ ] Security testing passed
- [ ] Performance testing completed
- [ ] Database migrations working
- [ ] Deployed to staging environment
- [ ] Frontend integration verified
```

### 6. Integration Features

#### Story Integration
- Links to parent story issue created by `/create-story`
- Inherits story context and business requirements
- Maintains traceability to original narrative

#### API Documentation
- Generates OpenAPI/Swagger specifications
- Includes request/response examples
- Documents authentication requirements
- Provides integration guides for frontend

#### Dependency Tracking
- Maps database schema requirements
- Identifies frontend integration points
- Tracks DevOps deployment needs
- Links to AI/ML integration requirements

## Example Usage

```bash
# After creating story with /create-story
/story-analysis KAN-15
# Activates role-specific commands

/backend-developer KAN-15
✅ Created: "User Dashboard Analytics - BE" (KAN-26)
📝 Dependencies: Database schema (KAN-27), DevOps config (pending)
🔗 Linked to parent story: KAN-15
📋 API endpoints: 12 endpoints documented
```

## Error Handling

- **Missing Story ID**: Prompts for required story parameter
- **Story Not Found**: Searches for similar story IDs
- **Duplicate Backend Task**: Shows existing task, prevents duplicates
- **Missing Database Dependencies**: Warns about schema requirements

## Next Steps

After creating backend tasks:
1. Review API specifications in Jira web interface
2. Coordinate with database developer for schema design
3. Plan frontend integration with API documentation
4. Set up development environment and database connections

**Ready to create detailed backend development tasks with comprehensive API specifications and cross-team collaboration!**