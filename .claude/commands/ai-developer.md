---
description: "Create detailed AI/ML development tasks for a specific story with model specifications and data pipeline requirements"
shortcut: "aid"
arguments: true
---

# AI Developer

Create comprehensive AI/ML development tasks for an existing story with detailed model specifications and cross-team collaboration tracking.

## Usage

```bash
/ai-developer [story-id]             # Create AI/ML tasks for story
/aid [story-id]                      # Shortcut for AI developer
```

## AI/ML Task Creation

### 1. Story Context Loading

🤖 **AI Developer Mode**
===================

**Story ID Required**: Please provide a story ID to create AI/ML tasks.

**Usage**: `/ai-developer [story-id]` or `/aid [story-id]`

Story ID: **$ARGUMENTS**  
Task Type: **AI/ML Development**

### 2. AI/ML Task Generation

Based on the original story from `/create-story`, detailed AI/ML tasks will be created:

#### Model Development
- **Data Analysis & EDA**: Exploratory data analysis and feature engineering
- **Model Architecture**: Neural network/ML model design and selection
- **Training Pipeline**: Model training, validation, and hyperparameter tuning
- **Model Evaluation**: Performance metrics, A/B testing, and model comparison

#### AI Integration
- **Inference Pipeline**: Real-time and batch inference optimization
- **Model Serving**: REST/gRPC API endpoints for model predictions
- **Model Monitoring**: Performance tracking, drift detection, and retraining
- **Feature Store**: Feature management and versioning system

#### Intelligent Features
- **Natural Language Processing**: Text analysis, sentiment, and classification
- **Computer Vision**: Image processing, object detection, and recognition
- **Recommendation Systems**: Collaborative filtering and content-based recommendations
- **Predictive Analytics**: Time series forecasting and anomaly detection

### 3. Cross-Team Dependencies

🔗 **AI/ML Cross-Team Dependencies Analysis**

Each AI/ML task includes detailed dependency tracking:

#### Dependencies FROM Other Teams:
```
## Cross-Team Dependencies

### Requires:
- /database-developer - Data warehouse design and ETL pipelines
- /database-developer - Feature store infrastructure and data versioning
- /backend-developer - API endpoints for model integration and data access
- /backend-developer - Real-time data streaming and preprocessing services
- /devops-engineer - ML infrastructure, GPU resources, and container orchestration
- /devops-engineer - Model deployment pipelines (MLOps) and monitoring systems

### Data Requirements:
- Training datasets with proper labeling and validation
- Real-time data streams for online learning
- Feature engineering pipeline and data transformations
- Data quality monitoring and validation frameworks
```

#### Dependencies TO Other Teams:
```
### Provides:
- /backend-developer - ML model APIs and inference endpoints
- /backend-developer - Batch prediction services and data processing
- /frontend-developer - AI-powered features and intelligent UI components
- /qa-engineer - Model testing frameworks and performance benchmarks
- /database-developer - Feature requirements and data schema specifications

### AI/ML Deliverables:
- Trained ML models with performance documentation
- Model inference APIs with latency and accuracy guarantees
- Feature engineering pipelines and data transformations
- Model monitoring dashboards and performance metrics
- AI integration documentation and best practices
```

### 4. Technical Specifications

⚙️ **AI/ML Technical Specifications**

#### Development Standards
- **Framework**: TensorFlow/PyTorch/Scikit-learn (based on model requirements)
- **Language**: Python with type hints and data science libraries
- **MLOps**: MLflow/Weights&Biases for experiment tracking and model versioning
- **Infrastructure**: Docker containers with GPU support for training and inference

#### Model Requirements
- **Performance Metrics**: Accuracy, precision, recall, F1-score, latency
- **Scalability**: Horizontal scaling for batch and real-time inference
- **Reliability**: Model fallback strategies and error handling
- **Interpretability**: Model explainability and feature importance

#### Data Pipeline
- **Data Ingestion**: Batch and streaming data processing
- **Feature Engineering**: Automated feature extraction and transformation
- **Data Validation**: Data quality checks and schema validation
- **Model Training**: Automated retraining and model evaluation

### 5. Task Creation in Jira

📝 **AI/ML Task Creation in Jira**

**Task Format:**
- **Title**: `[Story Name] - AI`
- **Type**: Task (linked to parent story)
- **Labels**: `ai`, `ml`, `python`, `tensorflow`, `data-science`
- **Dependencies**: Cross-team dependencies tracked

**Task Details Created:**
- **Title Format**: `[Story Name] - AI`
- **Issue Type**: Task (linked to parent story)
- **Labels**: `ai`, `ml`, `python`, `tensorflow`, `data-science`, `mlops`
- **Priority**: Based on story priority and model complexity
- **Story Points**: Estimated based on model development complexity

#### Task Description Template:
```markdown
# AI/ML Development Task

## Story Context
Original Story: [STORY_ID] - [STORY_TITLE]
Related to: [PARENT_EPIC_IF_EXISTS]

## AI/ML Requirements
- Machine learning model development and training
- AI feature integration and intelligent data processing
- Model serving infrastructure and real-time inference
- Performance monitoring and model lifecycle management

## Technical Specifications
### ML Framework & Tools
- ML Framework: [TensorFlow/PyTorch/Scikit-learn]
- Language: Python 3.9+ with type hints
- Data Processing: Pandas, NumPy, Apache Spark
- MLOps: MLflow, Docker, Kubernetes

### Model Architecture
- Model Type: [Classification/Regression/NLP/Computer Vision/Recommendation]
- Input Features: [Feature specifications and data types]
- Output Format: [Prediction format and confidence scores]
- Performance Requirements: [Accuracy targets and latency limits]

## Data Requirements

### Training Data:
- Dataset size and quality requirements
- Labeling requirements and data annotation
- Data preprocessing and cleaning specifications
- Feature engineering and transformation needs

### Inference Data:
- Real-time data streaming requirements
- Batch processing specifications
- Data validation and quality checks
- Feature store integration

## Model Development Pipeline

### 1. Data Analysis & Preparation
- Exploratory data analysis (EDA)
- Data cleaning and preprocessing
- Feature engineering and selection
- Data splitting (train/validation/test)

### 2. Model Training & Evaluation
- Model architecture design and selection
- Hyperparameter tuning and optimization
- Cross-validation and performance evaluation
- Model comparison and selection

### 3. Model Deployment & Serving
- Model packaging and containerization
- API endpoint development for inference
- Real-time and batch inference optimization
- Model version management and rollback

### 4. Monitoring & Management
- Model performance monitoring
- Data drift and model drift detection
- Automated retraining triggers
- A/B testing and gradual rollout

## Cross-Team Dependencies

### Requires:
- /database-developer - Feature store and data warehouse infrastructure
- /backend-developer - API integration and data preprocessing services
- /devops-engineer - ML infrastructure and deployment pipelines

### Provides:
- /backend-developer - ML model APIs and inference endpoints
- /frontend-developer - AI-powered features and intelligent recommendations
- /qa-engineer - Model testing frameworks and performance validation

### Blocking/Blocked Status:
- BLOCKS: Frontend AI features (model must be deployed)
- BLOCKED BY: Data infrastructure (database) and API integration (backend)

## Performance Requirements
- Model Accuracy: [Target accuracy/precision/recall metrics]
- Inference Latency: [Maximum response time requirements]
- Throughput: [Requests per second capacity]
- Resource Usage: [Memory and CPU constraints]

## Model Specifications
- Input Schema: [Detailed input feature specifications]
- Output Schema: [Prediction format and confidence scores]
- Model Size: [Memory footprint and storage requirements]
- Update Frequency: [Model retraining schedule and triggers]

## Acceptance Criteria
- [ ] Model achieves target performance metrics on test data
- [ ] Inference API endpoints deployed and functional
- [ ] Model monitoring and drift detection implemented
- [ ] Documentation complete (model cards, API docs)
- [ ] Integration tests with backend services passing
- [ ] Performance benchmarks met (latency/throughput)
- [ ] A/B testing framework setup for model evaluation
- [ ] Model explainability and interpretability implemented

## Definition of Done
- [ ] Model training pipeline automated and reproducible
- [ ] Code review completed and approved
- [ ] Model evaluation and validation complete
- [ ] Inference API deployed to staging environment
- [ ] Performance testing and benchmarking complete
- [ ] Model monitoring and alerting configured
- [ ] Documentation and model cards updated
- [ ] Integration with frontend/backend verified
```

### 6. Integration Features

#### Story Integration
- Links to parent story issue created by `/create-story`
- Inherits story context and intelligent feature requirements
- Maintains traceability to original AI/ML narrative

#### Model Documentation
- Generates model cards with performance metrics
- Includes feature specifications and data requirements
- Documents inference API endpoints and usage
- Provides integration guides for backend services

#### MLOps Integration
- Tracks model versions and experiment results
- Monitors model performance and data drift
- Manages model deployment and rollback strategies
- Integrates with CI/CD pipelines for automated testing

## Example Usage

```bash
# After creating story with /create-story
/story-analysis KAN-15
# Activates role-specific commands

/ai-developer KAN-15
✅ Created: "User Dashboard Analytics - AI" (KAN-28)
📝 Dependencies: Data warehouse (KAN-29), Backend APIs (KAN-26)
🔗 Linked to parent story: KAN-15
🤖 Model: Predictive analytics with recommendation engine
```

## Error Handling

- **Missing Story ID**: Prompts for required story parameter
- **Story Not Found**: Searches for similar story IDs
- **Duplicate AI Task**: Shows existing task, prevents duplicates
- **Missing Data Dependencies**: Warns about data infrastructure requirements

## Next Steps

After creating AI/ML tasks:
1. Review model specifications in Jira web interface
2. Coordinate with database developer for data infrastructure
3. Plan backend integration for model serving APIs
4. Set up ML development environment and data pipelines

**Ready to create detailed AI/ML development tasks with comprehensive model specifications and cross-team collaboration!**