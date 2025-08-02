---
description: "Create detailed DevOps engineering tasks for a specific story with infrastructure, deployment, and monitoring requirements"
shortcut: "doe"
arguments: true
---

# DevOps Engineer

Create comprehensive DevOps engineering tasks for an existing story with detailed infrastructure, deployment, and monitoring specifications.

## Usage

```bash
/devops-engineer [story-id]          # Create DevOps tasks for story
/doe [story-id]                      # Shortcut for DevOps engineer
```

## DevOps Task Creation

### 1. Story Context Loading

🚀 **DevOps Engineer Mode**
=======================

**Story ID Required**: Please provide a story ID to create DevOps tasks.

**Usage**: `/devops-engineer [story-id]` or `/doe [story-id]`

Story ID: **$ARGUMENTS**  
Task Type: **DevOps Engineering**

### 2. DevOps Task Generation

Based on the original story from `/create-story`, detailed DevOps tasks will be created:

#### Infrastructure & Platform
- **Container Orchestration**: Docker containerization and Kubernetes deployment
- **Cloud Infrastructure**: AWS/GCP/Azure resource provisioning and management
- **Load Balancing**: Traffic distribution and high availability setup
- **Auto-scaling**: Horizontal and vertical scaling based on demand

#### CI/CD Pipeline
- **Build Automation**: Automated build processes and artifact management
- **Deployment Pipeline**: Multi-environment deployment with approval gates
- **Testing Integration**: Automated testing in CI/CD pipeline
- **Release Management**: Blue-green deployments and rollback strategies

#### Monitoring & Operations
- **Application Monitoring**: Performance metrics and health checks
- **Log Management**: Centralized logging and log analysis
- **Alerting Systems**: Proactive monitoring and incident response
- **Security Operations**: Security scanning and compliance monitoring

### 3. Cross-Team Dependencies

🔗 **DevOps Cross-Team Dependencies Analysis**

Each DevOps task includes detailed dependency tracking:

#### Dependencies FROM Other Teams:
```
## Cross-Team Dependencies

### Requires:
- /backend-developer - Application configuration and environment variables
- /backend-developer - Health check endpoints and performance requirements
- /frontend-developer - Build specifications and static asset requirements
- /database-developer - Database backup, migration, and scaling requirements
- /ai-developer - ML model serving infrastructure and GPU resource needs
- /qa-engineer - Automated testing integration and deployment validation

### Infrastructure Requirements:
- Application performance and scaling requirements
- Security compliance and regulatory requirements
- Data backup and disaster recovery specifications
- Environment-specific configuration management
- Third-party service integrations and API keys
```

#### Dependencies TO Other Teams:
```
### Provides:
- /backend-developer - Deployment environments and configuration management
- /frontend-developer - CDN setup and static asset optimization
- /database-developer - Database infrastructure and backup systems
- /ai-developer - ML infrastructure with GPU support and model serving
- /qa-engineer - Testing environments and automated deployment validation
- /ux-designer - Performance monitoring affecting user experience

### DevOps Deliverables:
- Complete CI/CD pipeline with automated deployments
- Infrastructure as Code (IaC) with version control
- Monitoring and alerting system with dashboards
- Security scanning and compliance automation
- Disaster recovery and backup procedures
- Performance optimization and scaling automation
```

### 4. Technical Specifications

⚙️ **DevOps Technical Specifications**

#### Platform Standards
- **Containerization**: Docker with multi-stage builds and security scanning
- **Orchestration**: Kubernetes with Helm charts for deployment management
- **Cloud Platform**: AWS/GCP/Azure with terraform for infrastructure provisioning
- **CI/CD**: GitHub Actions/Jenkins/GitLab CI with automated testing integration

#### Infrastructure Requirements
- **Scalability**: Auto-scaling groups with load balancing
- **Security**: Network security groups, SSL certificates, and secret management
- **Monitoring**: Prometheus/Grafana or cloud-native monitoring solutions
- **Backup**: Automated backup and disaster recovery procedures

#### Operational Standards
- **High Availability**: Multi-AZ deployment with 99.9% uptime SLA
- **Performance**: Response time monitoring and optimization
- **Security**: Vulnerability scanning and compliance automation
- **Cost Optimization**: Resource utilization monitoring and optimization

### 5. Task Creation in Jira

📝 **DevOps Task Creation in Jira**

**Task Format:**
- **Title**: `[Story Name] - DevOps`
- **Type**: Task (linked to parent story)
- **Labels**: `devops`, `infrastructure`, `kubernetes`, `ci-cd`, `monitoring`
- **Dependencies**: Cross-team dependencies tracked

**Task Details Created:**
- **Title Format**: `[Story Name] - DevOps`
- **Issue Type**: Task (linked to parent story)
- **Labels**: `devops`, `infrastructure`, `kubernetes`, `ci-cd`, `monitoring`, `aws`
- **Priority**: Based on story priority and infrastructure criticality
- **Story Points**: Estimated based on infrastructure complexity and deployment requirements

#### Task Description Template:
```markdown
# DevOps Engineering Task

## Story Context
Original Story: [STORY_ID] - [STORY_TITLE]
Related to: [PARENT_EPIC_IF_EXISTS]

## DevOps Requirements
- Infrastructure setup and container orchestration
- CI/CD pipeline implementation and deployment automation
- Monitoring, logging, and alerting system configuration
- Security, backup, and disaster recovery implementation

## Technical Specifications
### Platform & Tools
- Container Platform: Docker with Kubernetes orchestration
- Cloud Provider: [AWS/GCP/Azure] with Terraform IaC
- CI/CD Platform: [GitHub Actions/Jenkins/GitLab CI]
- Monitoring Stack: [Prometheus/Grafana/CloudWatch/Datadog]

### Infrastructure Architecture
- Multi-environment setup (dev, staging, production)
- Auto-scaling with load balancing
- High availability with multi-AZ deployment
- Security groups and network configuration

## Infrastructure Requirements

### Container & Orchestration:
```yaml
# Kubernetes deployment specification
apiVersion: apps/v1
kind: Deployment
metadata:
  name: [story-app]
spec:
  replicas: 3
  selector:
    matchLabels:
      app: [story-app]
  template:
    spec:
      containers:
      - name: [story-app]
        image: [registry/story-app:tag]
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Infrastructure as Code:
```hcl
# Terraform infrastructure specification
resource "aws_ecs_cluster" "story_cluster" {
  name = "[story-name]-cluster"
  
  capacity_providers = ["FARGATE"]
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_lb" "story_alb" {
  name               = "[story-name]-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = var.public_subnets
}
```

## CI/CD Pipeline Specification

### Build Pipeline:
1. **Source Code**: Git webhook triggers build
2. **Build & Test**: Automated testing and code quality checks
3. **Security Scan**: Container vulnerability scanning and SAST
4. **Artifact Build**: Docker image build and registry push
5. **Deploy**: Environment-specific deployment with approval gates

### Deployment Strategy:
- **Blue-Green Deployment**: Zero-downtime deployments
- **Rollback Strategy**: Automated rollback on health check failure
- **Environment Promotion**: Dev → Staging → Production pipeline
- **Feature Flags**: Gradual feature rollout and A/B testing

## Monitoring & Observability

### Application Monitoring:
- **Health Checks**: Application liveness and readiness probes
- **Performance Metrics**: Response time, throughput, error rates
- **Resource Monitoring**: CPU, memory, disk, and network utilization
- **Custom Metrics**: Business-specific KPIs and application metrics

### Logging & Alerting:
- **Centralized Logging**: ELK stack or cloud-native logging
- **Log Aggregation**: Structured logging with correlation IDs
- **Alert Rules**: SLA-based alerting with escalation procedures
- **Dashboard Creation**: Real-time monitoring dashboards

### Observability Tools:
```yaml
# Prometheus monitoring configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: '[story-app]'
      static_configs:
      - targets: ['[story-app]:8080']
      metrics_path: /metrics
```

## Security & Compliance

### Security Measures:
- **Network Security**: VPC, security groups, and network ACLs
- **Secret Management**: AWS Secrets Manager/HashiCorp Vault
- **SSL/TLS**: Certificate management and HTTPS enforcement
- **Access Control**: IAM roles and RBAC configuration

### Compliance Requirements:
- **Security Scanning**: Automated vulnerability assessment
- **Audit Logging**: Compliance audit trail and log retention
- **Data Protection**: Encryption at rest and in transit
- **Backup Verification**: Regular backup testing and validation

## Cross-Team Dependencies

### Requires:
- /backend-developer - Application health check endpoints and configuration
- /database-developer - Database backup and migration requirements
- /ai-developer - ML infrastructure and GPU resource specifications

### Provides:
- /backend-developer - Deployment environments and monitoring infrastructure
- /frontend-developer - CDN configuration and static asset optimization
- /qa-engineer - Testing environments and deployment validation

### Blocking/Blocked Status:
- BLOCKS: Production deployment (infrastructure must be ready)
- BLOCKED BY: Application configuration (backend) and performance requirements

## Performance & Scaling Requirements

### Performance Targets:
- **Response Time**: 95th percentile < 500ms
- **Throughput**: Support [X] requests per second
- **Availability**: 99.9% uptime SLA
- **Recovery Time**: RTO < 15 minutes, RPO < 5 minutes

### Scaling Configuration:
- **Horizontal Scaling**: Auto-scaling based on CPU/memory thresholds
- **Vertical Scaling**: Resource limit adjustments based on demand
- **Database Scaling**: Read replicas and connection pooling
- **CDN**: Global content distribution for static assets

## Disaster Recovery & Backup

### Backup Strategy:
- **Database Backups**: Daily automated backups with point-in-time recovery
- **Application Data**: Regular backup of persistent volumes
- **Configuration Backup**: Infrastructure and configuration versioning
- **Recovery Testing**: Monthly disaster recovery drills

### High Availability:
- **Multi-AZ Deployment**: Cross-availability zone redundancy
- **Load Balancing**: Traffic distribution across healthy instances
- **Failover Procedures**: Automated failover with health monitoring
- **Data Replication**: Real-time data synchronization across regions

## Acceptance Criteria
- [ ] Infrastructure provisioned and configured correctly
- [ ] CI/CD pipeline automated and tested across environments
- [ ] Monitoring and alerting system operational
- [ ] Security scanning and compliance measures implemented
- [ ] Load testing completed with performance targets met
- [ ] Disaster recovery procedures tested and validated
- [ ] Documentation complete for operations and troubleshooting
- [ ] Team training completed for new infrastructure

## Definition of Done
- [ ] Infrastructure code reviewed and approved
- [ ] CI/CD pipeline tested with successful deployments
- [ ] Monitoring dashboards created and alerting configured
- [ ] Security audit completed and vulnerabilities addressed
- [ ] Performance testing passed with SLA requirements
- [ ] Disaster recovery tested and procedures documented
- [ ] Production deployment successful and stable
- [ ] Operational runbooks created and team trained
```

### 6. Integration Features

#### Story Integration
- Links to parent story issue created by `/create-story`
- Inherits story context and infrastructure requirements
- Maintains traceability to original deployment narrative

#### Infrastructure Management
- Manages Infrastructure as Code (IaC) with version control
- Tracks resource utilization and cost optimization
- Integrates with application deployment workflow
- Maintains security and compliance standards

#### Operational Integration
- Monitors application performance and user experience
- Manages incident response and resolution procedures
- Integrates with development workflow for continuous deployment
- Tracks SLA compliance and performance metrics

## Example Usage

```bash
# After creating story with /create-story
/story-analysis KAN-15
# Activates role-specific commands

/devops-engineer KAN-15
✅ Created: "User Dashboard Analytics - DevOps" (KAN-31)
📝 Dependencies: Backend config (KAN-26), Database backup (KAN-29)
🔗 Linked to parent story: KAN-15
🚀 Infrastructure: Kubernetes cluster, CI/CD pipeline, monitoring stack
```

## Error Handling

- **Missing Story ID**: Prompts for required story parameter
- **Story Not Found**: Searches for similar story IDs
- **Duplicate DevOps Task**: Shows existing task, prevents duplicates
- **Infrastructure Dependencies**: Warns about missing configuration requirements

## Next Steps

After creating DevOps tasks:
1. Review infrastructure requirements in Jira web interface
2. Coordinate with backend developer for application configuration
3. Plan infrastructure provisioning and deployment timeline
4. Set up monitoring and alerting system integration

**Ready to create detailed DevOps engineering tasks with comprehensive infrastructure specifications and cross-team collaboration!**