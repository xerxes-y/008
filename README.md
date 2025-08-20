# 008-Agent: LLM-Powered QA Automation Framework for Microservices

An intelligent, production-ready QA automation framework that uses LLM to automatically discover, test, and validate microservices in CI/CD environments. The system provides comprehensive testing for REST APIs, Kafka message flows, and database operations, with advanced features for continuous integration and deployment pipelines, including **full Jira integration** for test result reporting.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM QA Automation Framework                  │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   CI Runner     │  │  Test Orchestrator │  │ Config Manager │  │
│  │   (ci_runner.py)│  │  (test_orchestrator)│  │ (config_manager)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │          │
│           └─────────────────────┼─────────────────────┘          │
│                                 │                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Discovery     │  │ Test Generator  │  │ Test Executor   │  │
│  │   Engine        │  │ (LLM-powered)   │  │ (Parallel/Retry)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │          │
│           └─────────────────────┼─────────────────────┘          │
│                                 │                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Result Reporter │  │ Jira Integration│  │ Jenkins Pipeline│  │
│  │ (Multi-format)  │  │ (jira_integration)│  │ (Jenkinsfile)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Kafka     │  │ PostgreSQL  │  │   Redis     │  │ Ollama  │ │
│  │   Broker    │  │   Database  │  │   Cache     │  │ (LLM)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ User Service│  │Order Service│  │Notification │              │
│  │ (REST API)  │  │ (REST API)  │  │ Service     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Key Features

### **Core QA Capabilities**
- **🔍 Automatic Service Discovery**: Discovers REST endpoints, Kafka topics, and database schemas
- **🧠 LLM-Powered Test Generation**: Uses Ollama (local LLM) to generate intelligent test cases
- **⚡ Comprehensive Testing**: Tests REST APIs, Kafka messages, and database operations
- **🔄 Integration Testing**: End-to-end workflow testing across multiple services
- **📊 Detailed Reporting**: Generates comprehensive test reports in multiple formats (JSON, HTML, XML)

### **CI/CD Integration**
- **🏗️ Jenkins Pipeline**: Complete Jenkinsfile with multi-stage testing
- **⚙️ Configuration Management**: Centralized config with environment variable support
- **🔄 Parallel Execution**: Multi-worker test execution for faster CI/CD runs
- **🛡️ Retry Logic**: Intelligent retry with exponential backoff
- **🚨 Fail-Fast Mode**: Configurable fail-fast for CI/CD optimization
- **📈 Test Suites**: Smoke, regression, and performance test suites
- **🎯 Exit Codes**: Proper exit codes for CI/CD pipeline integration

### **🎯 Jira Integration (NEW!)**
- **📋 Interactive Ticket Selection**: Choose to create new tickets or update existing ones
- **📊 Comprehensive Reporting**: Detailed test results with build information
- **📎 File Attachments**: Automatic test report attachments to Jira tickets
- **🔄 Real-time Updates**: Live test result updates with formatted comments
- **⚙️ Flexible Configuration**: Environment variables or JSON configuration files
- **🛡️ Error Handling**: Graceful handling of connection and authentication issues

### **Advanced Features**
- **📊 Performance Analysis**: Identifies slow tests and performance bottlenecks
- **🔧 Test Orchestration**: Centralized test execution management
- **📝 Multi-format Reports**: JSON, HTML, and XML report formats
- **🌍 Environment Support**: Development, staging, and production configurations
- **📱 Notification Support**: Email and webhook notifications for test results

## 📋 Prerequisites

- **Docker and Docker Compose**
- **At least 8GB RAM** (for LLM model)
- **20GB free disk space**
- **Python 3.8+** (for local development)
- **Jenkins** (for CI/CD pipeline integration)
- **Jira instance** (for test result reporting)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd 008
```

### 2. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (about 2-3 minutes)
docker-compose logs -f
```

### 3. Run QA Framework

#### **Option A: CI/CD Mode (Recommended)**
```bash
# Run smoke tests
cd qa-agent
python3 ci_runner.py --test-suite smoke --fail-fast

# Run full regression tests
python3 ci_runner.py --test-suite regression --parallel --max-workers 4

# Run with custom config
python3 ci_runner.py --config ../ci_config_example.json --test-suite regression
```

#### **Option B: Simple QA Mode**
```bash
# Run simple QA cycle
cd qa-agent
python3 run_simple_qa.py
```

#### **Option C: Continuous Monitoring**
```bash
# Run continuous monitoring (development mode)
cd qa-agent
python3 main.py
```

### 4. Test Framework Integration

```bash
# Run comprehensive integration test
cd qa-agent
python3 test_complete_integration.py

# Test Jira integration specifically
python3 test_jira_integration.py

# Validate framework structure
python3 simple_test.py
```

### 5. Verify Services

```bash
docker-compose ps
```

You should see:
- ✅ zookeeper
- ✅ kafka
- ✅ postgres
- ✅ redis
- ✅ llm-runner (Ollama)
- ✅ user-service
- ✅ order-service
- ✅ notification-service
- ✅ kafka-ui

### 6. Access Services

- **Kafka UI**: http://localhost:8080
- **User Service**: http://localhost:8001
- **Order Service**: http://localhost:8002
- **Notification Service**: http://localhost:8003
- **LLM API (Ollama)**: http://localhost:11434

## 🎯 Jira Integration Setup

### **1. Configure Jira Credentials**

#### **Option A: Environment Variables (Recommended for Jenkins)**
```bash
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_USERNAME="your-email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"
export JIRA_PROJECT_KEY="QA"
export JIRA_ISSUE_TYPE="Test Execution"
```

#### **Option B: Configuration File**
```json
{
  "base_url": "https://your-company.atlassian.net",
  "username": "your-email@company.com",
  "api_token": "your-jira-api-token",
  "project_key": "QA",
  "issue_type": "Test Execution"
}
```

### **2. Test Jira Integration**

```bash
# Test with existing ticket
python3 qa-agent/jira_integration.py \
    --test-results test_results/test_report.json \
    --jira-ticket QA-123 \
    --build-number 456 \
    --build-url "https://jenkins.company.com/job/456/" \
    --git-branch main \
    --git-commit abc123def

# Create new ticket
python3 qa-agent/jira_integration.py \
    --test-results test_results/test_report.json \
    --build-number 456 \
    --build-url "https://jenkins.company.com/job/456/" \
    --git-branch main \
    --git-commit abc123def
```

### **3. Jenkins Pipeline Integration**

The Jenkinsfile includes automatic Jira integration. When you run the pipeline:

1. **Test execution completes** ✅
2. **Jira Reporting stage starts** 🔄
3. **Interactive prompt appears** asking for:
   - Jira ticket key (e.g., QA-123) or leave empty for new ticket
   - Reporting action: Create New / Update Existing / Skip
4. **Results are reported** to Jira with full details 📊

## 🔧 Configuration

### **Configuration Management**

The framework uses a centralized `ConfigManager` that supports both JSON files and environment variables:

#### **JSON Configuration Example**
```json
{
  "test": {
    "max_rest_tests": 20,
    "max_kafka_tests": 15,
    "max_database_tests": 5,
    "run_rest_tests": true,
    "run_kafka_tests": true,
    "include_negative_tests": true,
    "include_performance_tests": false
  },
  "llm": {
    "api_url": "http://llm-runner:11434/api",
    "model_name": "llama2:7b",
    "max_tokens": 2048,
    "temperature": 0.7,
    "timeout": 60
  },
  "services": {
    "user_service_url": "http://user-service:8000",
    "order_service_url": "http://order-service:8000",
    "kafka_brokers": "kafka:29092",
    "database_url": "postgresql://qa_user:qa_password@postgres:5432/qa_testing"
  },
  "reporting": {
    "output_dir": "test_results",
    "report_format": "json",
    "ci_mode": true,
    "fail_fast": true,
    "parallel_execution": true,
    "max_workers": 4
  },
  "ci": {
    "build_number": "123",
    "test_suite": "regression",
    "environment": "ci",
    "retry_failed": true,
    "max_retries": 3
  }
}
```

#### **Environment Variables**
```bash
# Test Configuration
MAX_REST_TESTS=20
MAX_KAFKA_TESTS=15
INCLUDE_PERFORMANCE_TESTS=false

# LLM Configuration
LLM_API_URL=http://llm-runner:11434/api
LLM_MODEL_NAME=llama2:7b

# Service URLs
USER_SERVICE_URL=http://user-service:8000
ORDER_SERVICE_URL=http://order-service:8000

# CI Configuration
CI_MODE=true
FAIL_FAST=true
PARALLEL_EXECUTION=true
MAX_WORKERS=4

# Jira Configuration
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=QA
JIRA_ISSUE_TYPE=Test Execution
```

## 🚀 CI/CD Integration

### **Jenkins Pipeline**

The framework includes a complete Jenkins pipeline (`Jenkinsfile`) with:

- **Multi-stage testing** (smoke, regression, performance)
- **Parallel execution** with configurable workers
- **Artifact archiving** and test result publishing
- **Environment-specific configurations**
- **Failure notifications**
- **🎯 Interactive Jira reporting** with ticket selection

#### **Jenkins Setup**
```bash
# Test Jenkins pipeline locally
./test-jenkins-pipeline.sh
```

#### **Jenkins Pipeline Stages**
1. **Checkout**: Git repository checkout
2. **Setup Environment**: Configuration and environment setup
3. **Start Infrastructure**: Docker services startup
4. **Run Smoke Tests**: Quick validation tests
5. **Run Full Test Suite**: Complete regression testing
6. **Performance Tests**: Load and performance testing
7. **🎯 Jira Reporting**: Interactive test result reporting
8. **Cleanup**: Resource cleanup and artifact archiving

### **GitHub Actions Example**
```yaml
name: QA Testing
on: [push, pull_request]

jobs:
  qa-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd qa-agent
          pip install -r requirements.txt
      - name: Start infrastructure
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 120
      - name: Run QA tests
        run: |
          cd qa-agent
          python3 ci_runner.py --test-suite smoke --fail-fast
      - name: Archive results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test-results/
```

## 📊 Test Results and Reporting

### **Report Structure**

The framework generates comprehensive test reports:

```json
{
  "report_metadata": {
    "generated_at": "2024-01-01T12:00:00Z",
    "framework_version": "2.0",
    "ci_build_number": "123",
    "test_suite": "regression"
  },
  "summary": {
    "total_tests": 150,
    "passed": 142,
    "failed": 5,
    "skipped": 3,
    "success_rate": 94.67,
    "total_execution_time": 45.2,
    "parallel_execution": true,
    "workers_used": 4
  },
  "execution_stats": {
    "completed_tests": 150,
    "failed_tests": 5,
    "retried_tests": 2,
    "total_execution_time": 45.2,
    "average_test_time": 0.3
  },
  "test_suites": {
    "smoke": {"total": 20, "passed": 19, "failed": 1},
    "regression": {"total": 130, "passed": 123, "failed": 4}
  },
  "coverage": {
    "services_tested": ["user-service", "order-service", "notification-service"],
    "endpoints_tested": [...],
    "kafka_topics_tested": [...],
    "database_tables_tested": [...]
  },
  "performance": {
    "slow_tests": [...],
    "performance_by_type": {...}
  },
  "recommendations": [...],
  "detailed_results": [...]
}
```

### **Report Formats**

- **JSON**: Machine-readable format for CI/CD integration
- **HTML**: Human-readable reports with charts and graphs
- **XML**: JUnit-compatible format for CI tools

### **🎯 Jira Integration Reports**

#### **New Ticket Creation**
- **Summary**: "QA Test Execution - X/Y passed"
- **Description**: Build information and test summary
- **Test Statistics**: Total tests, passed, failed, success rate
- **Build Details**: Build number, URL, git branch, commit
- **Attachment**: Complete test report JSON

#### **Existing Ticket Update**
- **Comment**: Detailed test results with formatting
- **Test Suite Breakdown**: Results by test suite
- **Failure Details**: First 5 failed tests with errors
- **Build Information**: Current build details
- **Attachment**: Updated test report

#### **Example Jira Comment**
```
h3. Test Execution Results - 2024-12-01 12:00:00

h4. Summary
* Total Tests: 150
* Passed: 142
* Failed: 5
* Skipped: 3
* Success Rate: 94.67%

h4. Build Information
* Build Number: 456
* Build URL: https://jenkins.company.com/job/456/
* Git Branch: main
* Git Commit: abc123def
* Environment: ci

h4. Test Suite Breakdown
* smoke: 19/20 passed
* regression: 123/130 passed

h4. Failures (5)
* User API Test: Connection timeout
* Order Service Test: Database constraint violation
```

## 🧪 Sample Microservices

The project includes three sample microservices for testing:

### **User Service (Port 8001)**
- REST API for user management
- PostgreSQL database integration
- Redis caching
- Endpoints: `/api/users/*`, `/health`

### **Order Service (Port 8002)**
- REST API for order management
- PostgreSQL database integration
- Kafka producer for order events
- Endpoints: `/api/orders/*`, `/health`

### **Notification Service (Port 8003)**
- REST API for notifications
- Redis storage
- Kafka consumer for order events
- Endpoints: `/api/notifications/*`, `/health`

## 🔍 Framework Components

### **Core Components**

1. **`ci_runner.py`**: Main entry point for CI/CD environments
2. **`test_orchestrator.py`**: Manages test execution flow and parallel processing
3. **`config_manager.py`**: Centralized configuration management
4. **`discovery.py`**: Service discovery engine
5. **`test_generator.py`**: LLM-powered test generation
6. **`test_executor.py`**: Test execution with retry logic
7. **`result_reporter.py`**: Multi-format report generation
8. **`jira_integration.py`**: 🎯 Jira integration for test result reporting

### **Supporting Files**

- **`Jenkinsfile`**: Complete Jenkins pipeline definition with Jira integration
- **`ci_config_example.json`**: Example configuration file
- **`jira_config_example.json`**: 🎯 Example Jira configuration
- **`test-jenkins-pipeline.sh`**: Local Jenkins testing script
- **`simple_test.py`**: Basic framework validation
- **`test_jira_integration.py`**: 🎯 Jira integration validation
- **`test_complete_integration.py`**: 🎯 Complete end-to-end integration test
- **`validate_framework.py`**: Comprehensive framework validation

## 🧪 Testing and Validation

### **Framework Testing**

```bash
# Run comprehensive integration test
python3 qa-agent/test_complete_integration.py

# Test Jira integration specifically
python3 qa-agent/test_jira_integration.py

# Validate framework structure
python3 qa-agent/simple_test.py

# Test complete framework validation
python3 qa-agent/validate_framework.py
```

### **Test Results**

✅ **All Integration Tests Passed (6/6)**
- ✅ Framework Structure - All required files present
- ✅ Configuration Management - ConfigManager working correctly
- ✅ Jira Integration - All Jira components functional
- ✅ Sample Workflow - Complete end-to-end workflow tested
- ✅ Jenkins Integration - Pipeline integration ready
- ✅ Command Line Tools - All CLI tools working

## 🐛 Troubleshooting

### **Common Issues**

1. **LLM Model Not Loading**
   ```bash
   # Check Ollama logs
   docker-compose logs llm-runner
   
   # Restart LLM service
   docker-compose restart llm-runner
   ```

2. **Framework Import Errors**
   ```bash
   # Validate framework
   cd qa-agent
   python3 simple_test.py
   
   # Check dependencies
   pip install -r requirements.txt
   ```

3. **CI Runner Issues**
   ```bash
   # Test CI runner
   python3 ci_runner.py --help
   
   # Run with debug logging
   python3 ci_runner.py --test-suite smoke --log-level DEBUG
   ```

4. **Jenkins Pipeline Issues**
   ```bash
   # Test Jenkins pipeline locally
   ./test-jenkins-pipeline.sh
   
   # Check Jenkins logs
   docker-compose logs jenkins
   ```

5. **🎯 Jira Integration Issues**
   ```bash
   # Test Jira integration
   python3 qa-agent/test_jira_integration.py
   
   # Check Jira credentials
   curl -u "your-email@company.com:your-api-token" \
        "https://your-company.atlassian.net/rest/api/2/myself"
   ```

### **Performance Tuning**

1. **Increase LLM Memory**
   ```yaml
   # In docker-compose.yml
   llm-runner:
     deploy:
       resources:
         limits:
           memory: 4G
   ```

2. **Adjust Parallel Workers**
   ```bash
   # Use more workers for faster execution
   python3 ci_runner.py --parallel --max-workers 8
   ```

3. **Optimize Test Limits**
   ```json
   {
     "test": {
       "max_rest_tests": 50,
       "max_kafka_tests": 30,
       "include_performance_tests": true
     }
   }
   ```

## 📈 Monitoring and Metrics

### **Available Metrics**

- Test execution success rates by suite
- Performance metrics by test type
- Service coverage statistics
- Error patterns and frequencies
- Parallel execution efficiency
- Retry success rates
- 🎯 Jira integration success rates

### **Log Analysis**

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs qa-agent
docker-compose logs user-service

# Follow logs in real-time
docker-compose logs -f

# Monitor Jira integration
grep "Jira issue" qa_automation.log
```

## 🔄 Advanced Usage

### **Custom Test Suites**

```bash
# Run specific test types only
python3 ci_runner.py --test-suite smoke --rest-only

# Run with custom configuration
python3 ci_runner.py --config custom_config.json --test-suite regression
```

### **Environment-Specific Testing**

```bash
# Development environment
python3 ci_runner.py --environment dev --test-suite smoke

# Production environment
python3 ci_runner.py --environment prod --test-suite regression --fail-fast
```

### **Integration with External Tools**

```bash
# Generate JUnit XML for CI tools
python3 ci_runner.py --report-format xml --output-dir junit-results

# Generate HTML reports
python3 ci_runner.py --report-format html --output-dir html-reports
```

### **🎯 Advanced Jira Integration**

```bash
# Report to specific Jira project
export JIRA_PROJECT_KEY="PERF"
python3 qa-agent/jira_integration.py --test-results report.json --build-number 123

# Use custom issue type
export JIRA_ISSUE_TYPE="Performance Test"
python3 qa-agent/jira_integration.py --test-results report.json --build-number 123

# Update existing ticket with custom config
python3 qa-agent/jira_integration.py \
    --test-results report.json \
    --jira-ticket QA-789 \
    --config-file custom_jira_config.json \
    --build-number 123
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Run framework validation: `python3 validate_framework.py`
4. Test Jira integration: `python3 test_jira_integration.py`
5. Create an issue with detailed information

## 🔮 Future Enhancements

- [ ] **GraphQL API Testing**: Support for GraphQL service testing
- [ ] **gRPC Service Testing**: Protocol buffer and gRPC testing
- [ ] **Load Testing**: Integrated load testing capabilities
- [ ] **Security Testing**: Security vulnerability scanning
- [ ] **Custom Test Templates**: User-defined test templates
- [ ] **Webhook Testing**: Webhook endpoint validation
- [ ] **API Contract Validation**: OpenAPI/Swagger validation
- [ ] **Performance Benchmarking**: Automated performance regression testing
- [ ] **Multi-LLM Support**: Support for different LLM providers
- [ ] **Test Data Management**: Advanced test data generation and management
- [ ] **Real-time Monitoring**: Live test execution monitoring
- [ ] **Test Result Analytics**: Advanced analytics and insights
- [ ] **🎯 Enhanced Jira Integration**: Bulk reporting, custom templates, webhooks

## 📚 Documentation

- **[CI/CD Integration Guide](CI_CD_GUIDE.md)**: Detailed CI/CD setup and configuration
- **[🎯 Jira Integration Guide](JIRA_INTEGRATION_GUIDE.md)**: Complete Jira integration guide
- **[Kafka LLM Testing Guide](KAFKA_LLM_TESTING_GUIDE.md)**: Kafka-specific testing examples
- **[Docker LLM Guide](framework/DOCKER_LLM_GUIDE.md)**: Docker and LLM setup guide
- **[Jenkins Testing Summary](JENKINS_TESTING_SUMMARY.md)**: Jenkins pipeline testing guide
