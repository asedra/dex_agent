---
description: "Implement database development tasks from Jira with task ID parameter"
shortcut: "dbd"
arguments: true
---

# Database Developer

Implement specific database development tasks from Jira by providing the task ID.

## Usage

```bash
/database-developer [task-id]        # Implement database task
/dbd [task-id]                       # Shortcut for database developer
```

## Database Task Implementation

### 1. Task Loading & Analysis

🗄️ **Database Developer Mode**
=========================

**Task ID Required**: Please provide a task ID to implement database features.

📋 **Loading task**: $ARGUMENTS  
🔄 **Analyzing database requirements**...  
🗄️ **Starting database implementation**...

Task ID: **$ARGUMENTS**  
Implementation Type: **Database Development**

### 2. Implementation Workflow

Based on the task details from Jira, the implementation will include:

#### Schema Design & Implementation
- **Table Creation**: Design and create normalized database tables
- **Relationship Setup**: Foreign keys and referential integrity constraints
- **Index Strategy**: Performance optimization through strategic indexing
- **Data Validation**: Constraints, triggers, and integrity rules

#### Migration Management
- **Schema Evolution**: Create migration scripts for schema changes
- **Data Migration**: Transform and migrate existing data safely
- **Rollback Strategy**: Implement rollback procedures for failed migrations
- **Version Control**: Track schema changes with proper versioning

#### Performance Optimization
- **Query Tuning**: Optimize slow queries and execution plans
- **Index Analysis**: Monitor and optimize index usage
- **Connection Pooling**: Configure database connection management
- **Caching Strategy**: Implement query result caching where appropriate

### 3. Development Steps

🔧 **Implementation Process**:

1. **Task Analysis**: Load task details and schema requirements
2. **Environment Setup**: Configure development database
3. **Schema Design**: Create ERD and table specifications
4. **Migration Scripts**: Write forward and rollback migrations
5. **Data Population**: Create seed data and test fixtures
6. **Performance Testing**: Analyze query performance and optimize
7. **Documentation**: Generate schema documentation and guides

### 4. Code Implementation

#### Migration Script Example
```sql
-- Migration: Create analytics tables
-- File: 001_create_analytics_tables.sql

-- Create main analytics table
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_analytics_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at);
CREATE INDEX idx_analytics_event_data_gin ON analytics_events USING GIN(event_data);

-- Create aggregation table for reporting
CREATE TABLE analytics_daily_summary (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_counts JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, user_id)
);

-- Create index for reporting queries
CREATE INDEX idx_analytics_summary_date_user ON analytics_daily_summary(date, user_id);
```

#### ORM Model Configuration
```javascript
// Sequelize model definition
const { Model, DataTypes } = require('sequelize');

class AnalyticsEvent extends Model {
  static associate(models) {
    // Define associations
    AnalyticsEvent.belongsTo(models.User, {
      foreignKey: 'user_id',
      as: 'user'
    });
  }
}

AnalyticsEvent.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  user_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  event_type: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [1, 100]
    }
  },
  event_data: {
    type: DataTypes.JSONB,
    allowNull: true
  }
}, {
  sequelize,
  modelName: 'AnalyticsEvent',
  tableName: 'analytics_events',
  underscored: true,
  timestamps: true
});
```

#### Query Optimization Example
```sql
-- Optimized analytics query with proper indexing
EXPLAIN ANALYZE
SELECT 
    u.email,
    COUNT(ae.id) as event_count,
    ae.event_type,
    DATE_TRUNC('day', ae.created_at) as event_date
FROM analytics_events ae
JOIN users u ON ae.user_id = u.id
WHERE ae.created_at >= CURRENT_DATE - INTERVAL '30 days'
    AND ae.event_type IN ('page_view', 'button_click', 'form_submit')
GROUP BY u.email, ae.event_type, DATE_TRUNC('day', ae.created_at)
ORDER BY event_date DESC, event_count DESC;
```

### 5. Task Completion Validation

✅ **Implementation Checklist**:
- [ ] Database schema designed and implemented correctly
- [ ] All migration scripts tested in development environment
- [ ] Indexes created for optimal query performance
- [ ] Data validation constraints properly implemented
- [ ] Seed data created for testing purposes
- [ ] Query performance benchmarked and optimized
- [ ] Backup and recovery procedures tested
- [ ] Database security measures implemented

### 6. Integration with Development Tools

#### Database Management
- Run `npm run migrate` for applying migrations
- Execute `npm run migrate:rollback` for rollback operations
- Use `npm run seed` for populating test data
- Run `npm run db:backup` for database backups

#### Performance Monitoring
- Analyze slow query logs with `EXPLAIN ANALYZE`
- Monitor index usage with database statistics
- Check connection pool status and optimization
- Validate query performance with load testing

## Example Usage

```bash
# Implement specific database task
/database-developer KAN-29
📋 Loading task: KAN-29 - "User Dashboard Analytics - DB"
🗄️ Implementing database schema...
✅ Tables created: analytics_events, analytics_daily_summary
📊 Indexes optimized: 6 performance indexes created
🧪 Migration scripts tested and validated
📋 Schema documentation generated
🚀 Ready for backend integration
```

## Error Handling

- **Missing Task ID**: Prompts for required task parameter
- **Task Not Found**: Searches for similar task IDs in project
- **Migration Errors**: Provides rollback guidance and error resolution
- **Performance Issues**: Suggests query optimization strategies

## Integration Features

- **Jira Integration**: Automatic task status updates and progress tracking
- **Migration Tracking**: Version control for schema changes
- **Performance Monitoring**: Query analysis and optimization recommendations
- **Documentation Generation**: Automated ERD and schema documentation

**Ready to implement database tasks efficiently with comprehensive schema development workflow!**