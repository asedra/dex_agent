---
description: "Create detailed database development tasks for a specific story with schema design and optimization requirements"
shortcut: "dbd"
arguments: true
---

# Database Developer

Create comprehensive database development tasks for an existing story with detailed schema design and performance optimization specifications.

## Usage

```bash
/database-developer [story-id]       # Create database tasks for story
/dbd [story-id]                      # Shortcut for database developer
```

## Database Task Creation

### 1. Story Context Loading

🗄️ **Database Developer Mode**
=========================

**Story ID Required**: Please provide a story ID to create database tasks.

**Usage**: `/database-developer [story-id]` or `/dbd [story-id]`

Story ID: **$ARGUMENTS**  
Task Type: **Database Development**

### 2. Database Task Generation

Based on the original story from `/create-story`, detailed database tasks will be created:

#### Schema Design & Architecture
- **Entity Relationship Design**: Normalized database schema with proper relationships
- **Data Modeling**: Conceptual, logical, and physical data model design
- **Index Strategy**: Performance optimization through strategic indexing
- **Partitioning & Sharding**: Scalability planning for large datasets

#### Data Management
- **Migration Scripts**: Database schema evolution and version control
- **Seed Data**: Initial data population and test data generation
- **Data Validation**: Constraints, triggers, and data integrity enforcement
- **Backup & Recovery**: Disaster recovery planning and automated backups

#### Performance Optimization
- **Query Optimization**: Efficient query design and execution plan analysis
- **Connection Pooling**: Database connection management and optimization
- **Caching Strategy**: Database-level caching and query result optimization
- **Monitoring & Analytics**: Database performance metrics and health monitoring

### 3. Cross-Team Dependencies

🔗 **Database Cross-Team Dependencies Analysis**

Each database task includes detailed dependency tracking:

#### Dependencies FROM Other Teams:
```
## Cross-Team Dependencies

### Requires:
- /backend-developer - Business logic requirements and data access patterns
- /backend-developer - API endpoint specifications and query requirements
- /ai-developer - Feature store requirements and ML data pipeline needs
- /frontend-developer - Data format requirements and user interface data needs
- /devops-engineer - Database infrastructure setup and deployment configurations

### Infrastructure Requirements:
- Database server provisioning and configuration
- Security configurations and access control setup
- Backup and disaster recovery infrastructure
- Monitoring and alerting system integration
- Environment-specific database configurations
```

#### Dependencies TO Other Teams:
```
### Provides:
- /backend-developer - Optimized database schema and query performance
- /backend-developer - Database connection configurations and ORM setup
- /ai-developer - Data warehouse design and feature store infrastructure
- /ai-developer - ETL pipelines and data preprocessing capabilities
- /frontend-developer - Data models and API response structures
- /qa-engineer - Test database setup and data seeding for testing

### Database Deliverables:
- Complete database schema with documentation
- Migration scripts and version control system
- Optimized queries and stored procedures
- Data validation rules and integrity constraints
- Performance benchmarks and monitoring setup
- Backup and recovery procedures
```

### 4. Technical Specifications

⚙️ **Database Technical Specifications**

#### Development Standards
- **Database System**: PostgreSQL/MySQL/MongoDB (based on project requirements)
- **Schema Management**: Migration-based schema evolution with version control
- **ORM Integration**: Prisma/Sequelize/Mongoose compatibility and optimization
- **Testing**: Database testing with fixtures and transaction rollback

#### Architecture Requirements
- **Normalization**: Proper database normalization (3NF/BCNF) with performance considerations
- **Relationships**: Foreign key constraints and referential integrity
- **Indexing**: Strategic index design for query performance optimization
- **Security**: Row-level security, encryption at rest, and access control

#### Performance Standards
- **Query Performance**: Sub-100ms response time for simple queries
- **Concurrency**: Support for concurrent read/write operations
- **Scalability**: Horizontal scaling capabilities and read replicas
- **Data Integrity**: ACID compliance and transaction management

### 5. Task Creation in Jira

📝 **Database Task Creation in Jira**

**Task Format:**
- **Title**: `[Story Name] - DB`
- **Type**: Task (linked to parent story)
- **Labels**: `database`, `schema`, `postgresql`, `optimization`
- **Dependencies**: Cross-team dependencies tracked

**Task Details Created:**
- **Title Format**: `[Story Name] - DB`
- **Issue Type**: Task (linked to parent story)
- **Labels**: `database`, `schema`, `postgresql`, `migration`, `optimization`
- **Priority**: Based on story priority and data complexity
- **Story Points**: Estimated based on schema complexity and performance requirements

#### Task Description Template:
```markdown
# Database Development Task

## Story Context
Original Story: [STORY_ID] - [STORY_TITLE]
Related to: [PARENT_EPIC_IF_EXISTS]

## Database Requirements
- Database schema design and optimization
- Data modeling and relationship management
- Query performance tuning and indexing strategy
- Migration scripts and data integrity enforcement

## Technical Specifications
### Database & Tools
- Database System: [PostgreSQL/MySQL/MongoDB]
- Schema Management: [Prisma/Sequelize/TypeORM] migrations
- Version Control: Git-based migration versioning
- Testing: Database testing with fixtures and test data

### Schema Design
- Entity relationship modeling with proper normalization
- Foreign key constraints and referential integrity
- Index strategy for query performance optimization
- Data validation rules and constraints

## Data Model Specification

### Core Entities:
```sql
-- Example schema structure
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE [story_specific_entities] (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    -- Story-specific columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relationships:
- One-to-Many: [Specify relationships]
- Many-to-Many: [Junction tables and constraints]
- Foreign Keys: [Reference integrity rules]

### Indexes:
```sql
-- Performance optimization indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_[entity]_user_id ON [entity](user_id);
CREATE INDEX idx_[entity]_created_at ON [entity](created_at);
```

## Migration Strategy

### Schema Evolution:
- Forward-only migration scripts
- Rollback strategies for schema changes
- Data migration and transformation scripts
- Environment-specific configuration management

### Version Control:
- Sequential migration numbering
- Migration dependency tracking
- Automated migration testing
- Production deployment procedures

## Performance Optimization

### Query Optimization:
- Execution plan analysis and optimization
- Index usage monitoring and tuning
- Query rewriting for performance improvement
- Stored procedure optimization where applicable

### Database Configuration:
- Connection pooling setup and tuning
- Memory allocation optimization
- Query cache configuration
- Performance monitoring and alerting

## Cross-Team Dependencies

### Requires:
- /backend-developer - Data access patterns and business logic requirements
- /ai-developer - Feature store specifications and ML data pipeline needs
- /devops-engineer - Database infrastructure and deployment configuration

### Provides:
- /backend-developer - Optimized schema and query performance
- /ai-developer - Data warehouse design and ETL pipeline infrastructure
- /qa-engineer - Test database setup and seeding procedures

### Blocking/Blocked Status:
- BLOCKS: Backend API development (schema must be ready)
- BLOCKS: AI model training (data infrastructure required)
- BLOCKED BY: Infrastructure setup (DevOps) and requirements gathering (Backend)

## Data Integrity & Security

### Constraints:
- Primary key and unique constraints
- Foreign key relationships and cascading rules
- Check constraints for data validation
- Not-null constraints for required fields

### Security Measures:
- Row-level security policies
- Encryption at rest for sensitive data
- Access control and user privilege management
- Audit logging for data modifications

## Testing Strategy

### Database Testing:
- Unit tests for stored procedures and functions
- Integration tests for ORM queries
- Performance testing for query optimization
- Data integrity testing for constraints

### Test Data Management:
- Fixtures and seed data for development
- Anonymized production data for testing
- Test database setup and teardown procedures
- Automated test data generation

## Acceptance Criteria
- [ ] Database schema designed and normalized properly
- [ ] All migration scripts created and tested
- [ ] Indexes implemented for performance optimization
- [ ] Data validation constraints in place
- [ ] ORM integration working with backend
- [ ] Query performance meets requirements (<100ms simple queries)
- [ ] Backup and recovery procedures tested
- [ ] Security measures implemented and verified

## Definition of Done
- [ ] Schema design reviewed and approved
- [ ] Migration scripts tested in all environments
- [ ] Performance benchmarking completed
- [ ] Documentation updated (ERD, schema docs)
- [ ] Integration testing with backend complete
- [ ] Security audit passed
- [ ] Monitoring and alerting configured
- [ ] Production deployment successful
```

### 6. Integration Features

#### Story Integration
- Links to parent story issue created by `/create-story`
- Inherits story context and data requirements
- Maintains traceability to original data narrative

#### Schema Documentation
- Generates Entity Relationship Diagrams (ERD)
- Includes data dictionary and field specifications
- Documents query patterns and performance considerations
- Provides migration guides and rollback procedures

#### Performance Tracking
- Monitors query performance and optimization
- Tracks database growth and scaling requirements
- Manages index usage and optimization recommendations
- Integrates with application performance monitoring

## Example Usage

```bash
# After creating story with /create-story
/story-analysis KAN-15
# Activates role-specific commands

/database-developer KAN-15
✅ Created: "User Dashboard Analytics - DB" (KAN-29)
📝 Dependencies: Backend requirements (KAN-26), DevOps infrastructure (pending)
🔗 Linked to parent story: KAN-15
🗄️ Schema: 5 tables, 12 indexes, performance optimized
```

## Error Handling

- **Missing Story ID**: Prompts for required story parameter
- **Story Not Found**: Searches for similar story IDs
- **Duplicate Database Task**: Shows existing task, prevents duplicates
- **Infrastructure Dependencies**: Warns about required DevOps setup

## Next Steps

After creating database tasks:
1. Review schema design in Jira web interface
2. Coordinate with backend developer for data access patterns
3. Plan infrastructure requirements with DevOps engineer
4. Set up development database and migration pipeline

**Ready to create detailed database development tasks with comprehensive schema design and cross-team collaboration!**