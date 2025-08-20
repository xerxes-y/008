# Testing Guide for Jenkins Pipeline Integration

This guide provides comprehensive instructions for testing the Jenkins pipeline integration with your QA automation framework.

## 🧪 **Testing Options**

### **1. Quick Framework Validation**
Fastest way to test if the framework components work:

```bash
cd qa-agent
python quick_test.py
```

**What it tests:**
- Module imports
- Configuration management
- Test orchestrator creation
- CI runner functionality
- Report generation
- File operations

**Expected output:**
```
🚀 Quick Test of QA Automation Framework
==================================================
1. Testing module imports...
   ✅ All modules imported successfully
2. Testing configuration...
   ✅ Configuration created
   - CI Mode: False
   - Max REST Tests: 50
   - Max Kafka Tests: 30
...
🎉 Quick test completed successfully!
Framework is ready for CI/CD integration.
```

### **2. Comprehensive Framework Validation**
Detailed validation of all framework components:

```bash
cd qa-agent
python validate_framework.py
```

**What it tests:**
- All module imports
- Dependencies availability
- Configuration manager functionality
- Configuration file operations
- CI runner validation
- Test orchestrator functionality
- Jenkinsfile validation

**Expected output:**
```
🧪 QA Automation Framework Validation
==================================================
🔍 Testing module imports...
✅ ConfigManager imported successfully
✅ TestOrchestrator imported successfully
...

==================================================
VALIDATION REPORT
==================================================
Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100.0%

Detailed Results:
  Module Imports: ✅ PASS
  Dependencies: ✅ PASS
  Configuration Manager: ✅ PASS
  Configuration File: ✅ PASS
  CI Runner: ✅ PASS
  Test Orchestrator: ✅ PASS
  Jenkinsfile: ✅ PASS

🎉 All tests passed! Framework is ready for CI/CD integration.
```

### **3. Local Jenkins Testing**
Test with a real Jenkins instance:

```bash
# Run the Jenkins test script
./test-jenkins-pipeline.sh

# Or run specific parts
./test-jenkins-pipeline.sh test-only    # Test framework only
./test-jenkins-pipeline.sh cleanup      # Cleanup test environment
```

**What it does:**
- Starts a local Jenkins instance using Docker
- Creates test job configuration
- Validates pipeline syntax
- Tests framework integration
- Provides Jenkins access for manual testing

**Expected output:**
```
🧪 Testing Jenkins Pipeline with QA Automation Framework
========================================================
[INFO] Checking Docker...
[SUCCESS] Docker is running
[INFO] Testing QA framework directly...
[SUCCESS] QA framework test passed
[INFO] Setting up Jenkins test environment...
[SUCCESS] Jenkins test environment created
[INFO] Starting Jenkins...
[SUCCESS] Jenkins is running on http://localhost:8080
Jenkins URL: http://localhost:8080
Admin Password: [password]
[SUCCESS] Jenkins pipeline test completed successfully!
```

## 🔧 **Manual Testing Steps**

### **Step 1: Test Framework Components**

```bash
# 1. Test configuration manager
cd qa-agent
python -c "
from config_manager import ConfigManager
config = ConfigManager()
print('Config created:', config.is_ci_mode())
print('Test limits:', config.get_test_limits())
"

# 2. Test CI runner
python ci_runner.py --help

# 3. Test with minimal configuration
python ci_runner.py --test-suite smoke --fail-fast
```

### **Step 2: Test Jenkins Pipeline Syntax**

```bash
# Validate Jenkinsfile syntax
cd ..
groovy -e "
def pipeline = new groovy.lang.Binding()
def shell = new groovy.lang.GroovyShell(pipeline)
try {
    shell.evaluate(new File('Jenkinsfile').text)
    println 'Jenkinsfile syntax is valid'
} catch (Exception e) {
    println 'Jenkinsfile syntax error: ' + e.message
}
"
```

### **Step 3: Test with Mock Services**

```bash
# Start minimal infrastructure for testing
docker-compose up -d postgres redis kafka

# Test framework with mock services
cd qa-agent
python ci_runner.py --test-suite smoke --config ci_config_example.json
```

## 🐳 **Docker-Based Testing**

### **1. Test with Full Infrastructure**

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 60

# Test the framework
cd qa-agent
python ci_runner.py --test-suite smoke --parallel
```

### **2. Test Jenkins Pipeline Locally**

```bash
# Start Jenkins with Docker
docker run -d \
  --name jenkins-test \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts-jdk17

# Wait for Jenkins to start
sleep 30

# Get admin password
docker exec jenkins-test cat /var/jenkins_home/secrets/initialAdminPassword

# Access Jenkins at http://localhost:8080
```

## 🔍 **Testing Checklist**

### **Framework Components**
- [ ] All Python modules can be imported
- [ ] Configuration manager works with defaults
- [ ] Configuration manager loads environment variables
- [ ] Configuration manager loads from JSON files
- [ ] Test orchestrator can be created
- [ ] CI runner accepts command line arguments
- [ ] Report generation works
- [ ] File operations work correctly

### **CI/CD Integration**
- [ ] Jenkinsfile syntax is valid
- [ ] Pipeline stages are defined correctly
- [ ] Environment variables are set
- [ ] Artifact archiving works
- [ ] Exit codes are correct
- [ ] Build metadata is captured

### **Infrastructure**
- [ ] Docker services start correctly
- [ ] Services are accessible
- [ ] Database connections work
- [ ] Kafka connections work
- [ ] LLM service is available

## 🚨 **Troubleshooting**

### **Common Issues**

**1. Import Errors**
```bash
# Solution: Install dependencies
pip install -r requirements.txt

# Or install specific missing packages
pip install aiohttp psycopg2-binary redis kafka-python
```

**2. Configuration Errors**
```bash
# Check if configuration file exists
ls -la ci_config_example.json

# Validate JSON syntax
python -m json.tool ci_config_example.json
```

**3. Jenkins Connection Issues**
```bash
# Check if Jenkins is running
curl http://localhost:8080

# Check Docker containers
docker ps | grep jenkins

# Restart Jenkins if needed
docker restart jenkins-test
```

**4. Service Connection Issues**
```bash
# Check if services are running
docker-compose ps

# Check service logs
docker-compose logs user-service
docker-compose logs order-service
docker-compose logs llm-runner

# Test service health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### **Debug Mode**

```bash
# Run with debug logging
cd qa-agent
python ci_runner.py --log-level DEBUG --test-suite smoke

# Check detailed logs
tail -f qa_automation.log
```

## 📊 **Test Results Validation**

### **Expected Test Results**

After running tests, you should see:

1. **Test Reports**: JSON files in `test_results/` directory
2. **Log Files**: `qa_automation.log` with execution details
3. **Exit Codes**: 
   - `0` for success
   - `1` for failure (when fail-fast is enabled)

### **Sample Test Report Structure**

```json
{
  "report_metadata": {
    "generated_at": "2024-01-01T12:00:00Z",
    "total_tests": 10,
    "report_version": "1.0"
  },
  "summary": {
    "total_tests": 10,
    "passed": 9,
    "failed": 1,
    "skipped": 0,
    "success_rate": 90.0,
    "total_execution_time": 15.2
  },
  "ci_info": {
    "build_number": "123",
    "build_url": "https://jenkins.example.com/job/123",
    "git_branch": "main",
    "environment": "ci"
  }
}
```

## 🎯 **Performance Testing**

### **Test Execution Times**

Expected execution times for different test suites:

- **Smoke Tests**: 2-5 minutes
- **Regression Tests**: 10-30 minutes
- **Performance Tests**: 15-45 minutes

### **Resource Usage**

Monitor resource usage during testing:

```bash
# Monitor CPU and memory
docker stats

# Monitor disk usage
df -h

# Monitor network
docker network ls
```

## 🔄 **Continuous Testing**

### **Automated Testing Script**

Create a script for regular testing:

```bash
#!/bin/bash
# daily-test.sh

echo "Running daily framework tests..."

# Test framework components
cd qa-agent
python validate_framework.py

# Test with minimal configuration
python ci_runner.py --test-suite smoke --fail-fast

# Test Jenkins pipeline syntax
cd ..
groovy -e "new groovy.lang.GroovyShell().evaluate(new File('Jenkinsfile').text)"

echo "Daily tests completed"
```

### **GitHub Actions for Testing**

Create `.github/workflows/test-framework.yml`:

```yaml
name: Test Framework

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd qa-agent
        pip install -r requirements.txt
    
    - name: Test framework
      run: |
        cd qa-agent
        python validate_framework.py
    
    - name: Quick test
      run: |
        cd qa-agent
        python quick_test.py
```

## 📈 **Monitoring and Metrics**

### **Test Metrics to Track**

1. **Success Rate**: Percentage of tests passing
2. **Execution Time**: Time per test suite
3. **Resource Usage**: CPU, memory, disk usage
4. **Failure Patterns**: Common failure types
5. **Framework Performance**: Component load times

### **Log Analysis**

```bash
# Analyze test logs
grep "ERROR" qa_automation.log
grep "WARNING" qa_automation.log
grep "PASSED\|FAILED" qa_automation.log | wc -l
```

## 🎉 **Success Criteria**

Your framework is ready for CI/CD integration when:

1. ✅ All validation tests pass
2. ✅ Quick test completes successfully
3. ✅ Jenkins pipeline syntax is valid
4. ✅ Test reports are generated correctly
5. ✅ Exit codes work as expected
6. ✅ Artifacts are archived properly
7. ✅ Logging provides sufficient detail
8. ✅ Error handling works correctly

## 📚 **Additional Resources**

- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [QA Automation Best Practices](https://www.selenium.dev/documentation/)

## 🤝 **Getting Help**

If you encounter issues:

1. Check the troubleshooting section
2. Review the logs in `qa_automation.log`
3. Run the validation script to identify specific issues
4. Check Docker container status and logs
5. Verify all dependencies are installed correctly

The testing framework provides comprehensive validation to ensure your QA automation framework is ready for production CI/CD integration!
