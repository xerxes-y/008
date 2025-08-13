# LLM-Powered QA System for Microservices Testing

An intelligent QA system that uses LLM to automatically discover, test, and validate microservices in a Docker environment. The system can test REST APIs, Kafka message flows, and database operations, generating comprehensive test reports with input/output data.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM QA Agent  │    │   Microservices │    │   Infrastructure│
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Discovery   │ │───▶│ │ REST APIs   │ │    │ │   Kafka     │ │
│ │ Engine      │ │    │ │             │ │    │ │   Broker    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Test        │ │───▶│ │ Kafka       │ │    │ │   Database  │ │
│ │ Generator   │ │    │ │ Consumers   │ │    │ │   (PostgreSQL)│
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Result      │ │    │ │ Microservice│ │    │ │   Redis     │ │
│ │ Reporter    │ │    │ │ Containers  │ │    │ │   (Cache)   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Features

- **Automatic Service Discovery**: Discovers REST endpoints, Kafka topics, and database schemas
- **LLM-Powered Test Generation**: Uses LLM to generate intelligent test cases
- **Comprehensive Testing**: Tests REST APIs, Kafka messages, and database operations
- **Integration Testing**: End-to-end workflow testing across multiple services
- **Detailed Reporting**: Generates comprehensive test reports with input/output data
- **Continuous Monitoring**: Runs continuous testing cycles
- **Performance Analysis**: Identifies slow tests and performance bottlenecks

## 📋 Prerequisites

- Docker and Docker Compose
- At least 8GB RAM (for LLM model)
- 20GB free disk space

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd limbo
```

### 2. Start the Infrastructure

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (about 2-3 minutes)
docker-compose logs -f
```

### 3. Verify Services

Check that all services are running:

```bash
docker-compose ps
```

You should see:
- ✅ zookeeper
- ✅ kafka
- ✅ postgres
- ✅ redis
- ✅ llm-runner
- ✅ user-service
- ✅ order-service
- ✅ notification-service
- ✅ qa-agent
- ✅ kafka-ui

### 4. Access Services

- **Kafka UI**: http://localhost:8080
- **User Service**: http://localhost:8001
- **Order Service**: http://localhost:8002
- **Notification Service**: http://localhost:8003
- **LLM API**: http://localhost:11434

### 5. Monitor QA Agent

```bash
# View QA agent logs
docker-compose logs -f qa-agent

# Check test results
ls -la test-results/
```

## 🔧 Configuration

### Environment Variables

The system uses the following environment variables (already configured in docker-compose.yml):

```yaml
# LLM Configuration
LLM_API_URL: http://llm-runner:11434/api

# Kafka Configuration
KAFKA_BROKERS: kafka:29092

# Database Configuration
POSTGRES_URL: postgresql://qa_user:qa_password@postgres:5432/qa_testing

# Redis Configuration
REDIS_URL: redis://redis:6379
```

### Customizing Test Parameters

Edit `qa-agent/main.py` to modify:
- Test execution intervals
- LLM model selection
- Test generation strategies

## 📊 Test Results

The QA agent generates comprehensive test reports in the `test-results/` directory:

### Report Structure

```json
{
  "report_metadata": {
    "generated_at": "2024-01-01T12:00:00Z",
    "total_tests": 150,
    "report_version": "1.0"
  },
  "summary": {
    "total_tests": 150,
    "passed": 142,
    "failed": 5,
    "skipped": 3,
    "success_rate": 94.67,
    "total_execution_time": 45.2
  },
  "statistics": {
    "test_types": {
      "rest_api": {"total": 80, "passed": 75, "failed": 3, "skipped": 2},
      "kafka": {"total": 40, "passed": 38, "failed": 1, "skipped": 1},
      "database": {"total": 20, "passed": 19, "failed": 1, "skipped": 0},
      "integration": {"total": 10, "passed": 10, "failed": 0, "skipped": 0}
    }
  },
  "failures": {
    "total_failures": 5,
    "failure_types": {...},
    "common_errors": [...]
  },
  "coverage": {
    "services_tested": ["user-service", "order-service", "notification-service"],
    "endpoints_tested": [...],
    "kafka_topics_tested": [...],
    "database_tables_tested": [...]
  },
  "performance": {
    "performance_by_type": {...},
    "slow_tests": [...]
  },
  "recommendations": [...],
  "detailed_results": [...]
}
```

## 🔍 Understanding the Workflow

### 1. Discovery Phase
- LLM scans Docker containers for REST endpoints
- Discovers Kafka topics and message schemas
- Analyzes database schemas and relationships

### 2. Test Generation
- LLM generates test cases based on discovered APIs
- Creates test data and expected responses
- Plans test execution strategy

### 3. Test Execution
- Executes REST API calls with various inputs
- Sends messages to Kafka topics
- Validates responses and data consistency

### 4. Result Generation
- Creates detailed test reports with input/output
- Generates coverage analysis
- Identifies potential issues and recommendations

## 🧪 Sample Microservices

The project includes three sample microservices for testing:

### User Service (Port 8001)
- REST API for user management
- PostgreSQL database integration
- Redis caching
- Endpoints: `/api/users/*`, `/health`

### Order Service (Port 8002)
- REST API for order management
- PostgreSQL database integration
- Kafka producer for order events
- Endpoints: `/api/orders/*`, `/health`

### Notification Service (Port 8003)
- REST API for notifications
- Redis storage
- Kafka consumer for order events
- Endpoints: `/api/notifications/*`, `/health`

## 🐛 Troubleshooting

### Common Issues

1. **LLM Model Not Loading**
   ```bash
   # Check LLM logs
   docker-compose logs llm-runner
   
   # Restart LLM service
   docker-compose restart llm-runner
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Verify database is ready
   docker-compose exec postgres psql -U qa_user -d qa_testing -c "SELECT 1;"
   ```

3. **Kafka Connection Issues**
   ```bash
   # Check Kafka logs
   docker-compose logs kafka
   
   # Verify Kafka topics
   docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
   ```

4. **QA Agent Not Starting**
   ```bash
   # Check QA agent logs
   docker-compose logs qa-agent
   
   # Restart QA agent
   docker-compose restart qa-agent
   ```

### Performance Tuning

1. **Increase LLM Memory**
   ```yaml
   # In docker-compose.yml
   llm-runner:
     deploy:
       resources:
         limits:
           memory: 4G
   ```

2. **Adjust Test Intervals**
   ```python
   # In qa-agent/main.py
   await asyncio.sleep(300)  # Change from 5 minutes to desired interval
   ```

## 📈 Monitoring and Metrics

### Available Metrics

- Test execution success rates
- Performance metrics by test type
- Service coverage statistics
- Error patterns and frequencies
- Resource utilization

### Log Analysis

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs qa-agent
docker-compose logs user-service

# Follow logs in real-time
docker-compose logs -f
```

## 🔄 Continuous Integration

The system is designed to run continuously and can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: QA Testing
on: [push, pull_request]

jobs:
  qa-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start QA System
        run: docker-compose up -d
      - name: Wait for Services
        run: sleep 300
      - name: Check Test Results
        run: |
          if [ -f "test-results/test_report_*.json" ]; then
            echo "Tests completed successfully"
          else
            echo "Tests failed"
            exit 1
          fi
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue with detailed information

## 🔮 Future Enhancements

- [ ] Support for GraphQL APIs
- [ ] gRPC service testing
- [ ] Load testing capabilities
- [ ] Security testing integration
- [ ] Custom test templates
- [ ] Webhook testing
- [ ] API contract validation
- [ ] Performance benchmarking
