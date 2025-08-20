# Jira Integration Guide for QA Automation Framework

This guide explains how to integrate your QA automation framework with Jira for test result reporting in Jenkins pipelines.

## 🎯 Overview

The Jira integration allows you to:
- **Create new Jira tickets** for test execution results
- **Update existing tickets** with test results
- **Add test reports as attachments**
- **Include build information** and test statistics
- **Interactive ticket selection** in Jenkins pipelines

## 🚀 Quick Start

### 1. Setup Jira Configuration

#### **Option A: Environment Variables (Recommended for Jenkins)**
```bash
# Set these in Jenkins credentials or environment
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
  "issue_type": "Test Execution",
  "custom_fields": {
    "customfield_10001": "Automated Test",
    "customfield_10002": "High"
  }
}
```

### 2. Get Jira API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name (e.g., "QA Automation")
4. Copy the token and save it securely

### 3. Test Jira Integration

```bash
# Test with existing ticket
python3 qa-agent/jira_integration.py \
    --test-results test_results/test_report_20241201_120000.json \
    --jira-ticket QA-123 \
    --build-number 456 \
    --build-url "https://jenkins.company.com/job/qa-testing/456/" \
    --git-branch main \
    --git-commit abc123def

# Create new ticket
python3 qa-agent/jira_integration.py \
    --test-results test_results/test_report_20241201_120000.json \
    --build-number 456 \
    --build-url "https://jenkins.company.com/job/qa-testing/456/" \
    --git-branch main \
    --git-commit abc123def
```

## 🔧 Jenkins Pipeline Integration

### **Automatic Integration**

The Jenkinsfile already includes Jira integration. When you run the pipeline:

1. **Test execution completes**
2. **Jira Reporting stage starts**
3. **Interactive prompt appears** asking for:
   - Jira ticket key (optional)
   - Reporting action (Create New/Update Existing/Skip)

### **Pipeline Configuration**

```groovy
environment {
    // Jira Integration Configuration
    JIRA_BASE_URL = 'https://your-company.atlassian.net'
    JIRA_USERNAME = 'your-email@company.com'
    JIRA_API_TOKEN = 'your-jira-api-token'
    JIRA_PROJECT_KEY = 'QA'
    JIRA_ISSUE_TYPE = 'Test Execution'
    JIRA_REPORTING_ENABLED = 'true'
}
```

### **Jenkins Credentials Setup**

1. **Go to Jenkins > Manage Jenkins > Credentials**
2. **Add new credentials**:
   - Kind: Secret text
   - ID: `jira-api-token`
   - Secret: Your Jira API token
3. **Update Jenkinsfile**:
   ```groovy
   environment {
       JIRA_API_TOKEN = credentials('jira-api-token')
   }
   ```

## 📊 What Gets Reported to Jira

### **New Ticket Creation**
- **Summary**: "QA Test Execution - X/Y passed"
- **Description**: Build information and test summary
- **Test Statistics**: Total tests, passed, failed, success rate
- **Build Details**: Build number, URL, git branch, commit
- **Attachment**: Complete test report JSON

### **Existing Ticket Update**
- **Comment**: Detailed test results with formatting
- **Test Suite Breakdown**: Results by test suite
- **Failure Details**: First 5 failed tests with errors
- **Build Information**: Current build details
- **Attachment**: Updated test report

### **Example Jira Comment**
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
* Build URL: https://jenkins.company.com/job/qa-testing/456/
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

## 🎛️ Advanced Configuration

### **Custom Fields**

You can map test results to Jira custom fields:

```json
{
  "custom_fields": {
    "customfield_10001": "Automated Test",
    "customfield_10002": "High",
    "customfield_10003": "QA Team",
    "customfield_10004": "Microservices"
  }
}
```

### **Issue Types**

Configure different issue types for different test scenarios:

```bash
# For smoke tests
export JIRA_ISSUE_TYPE="Smoke Test"

# For regression tests
export JIRA_ISSUE_TYPE="Regression Test"

# For performance tests
export JIRA_ISSUE_TYPE="Performance Test"
```

### **Project Mapping**

Map different test suites to different Jira projects:

```bash
# For QA tests
export JIRA_PROJECT_KEY="QA"

# For performance tests
export JIRA_PROJECT_KEY="PERF"

# For security tests
export JIRA_PROJECT_KEY="SEC"
```

## 🔄 Workflow Examples

### **Scenario 1: Daily Regression Testing**
```bash
# Run regression tests
python3 qa-agent/ci_runner.py --test-suite regression

# Report to existing ticket
python3 qa-agent/jira_integration.py \
    --test-results test_results/test_report.json \
    --jira-ticket QA-789 \
    --build-number 123 \
    --git-branch develop
```

### **Scenario 2: Feature Testing**
```bash
# Run feature-specific tests
python3 qa-agent/ci_runner.py --test-suite smoke

# Create new ticket for feature
python3 qa-agent/jira_integration.py \
    --test-results test_results/test_report.json \
    --build-number 124 \
    --git-branch feature/new-payment \
    --config jira_config_feature.json
```

### **Scenario 3: Jenkins Pipeline**
```groovy
stage('Jira Reporting') {
    steps {
        script {
            def jiraTicket = input(
                message: 'Enter Jira ticket for test results',
                parameters: [
                    string(name: 'JIRA_TICKET', defaultValue: ''),
                    choice(name: 'ACTION', choices: ['Create New', 'Update Existing', 'Skip'])
                ]
            )
            
            if (jiraTicket.ACTION != 'Skip') {
                sh '''
                    python qa-agent/jira_integration.py \
                        --test-results test_results/test_report.json \
                        --jira-ticket ${jiraTicket.JIRA_TICKET} \
                        --build-number ${BUILD_NUMBER}
                '''
            }
        }
    }
}
```

## 🛠️ Troubleshooting

### **Common Issues**

1. **Authentication Failed**
   ```bash
   # Check credentials
   curl -u "your-email@company.com:your-api-token" \
        "https://your-company.atlassian.net/rest/api/2/myself"
   ```

2. **Project Not Found**
   ```bash
   # Verify project key
   curl -u "your-email@company.com:your-api-token" \
        "https://your-company.atlassian.net/rest/api/2/project/QA"
   ```

3. **Issue Type Not Found**
   ```bash
   # List available issue types
   curl -u "your-email@company.com:your-api-token" \
        "https://your-company.atlassian.net/rest/api/2/issuetype"
   ```

### **Debug Mode**

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python3 qa-agent/jira_integration.py --test-results report.json --build-number 123
```

### **Test Jira Connection**

```bash
# Test basic connectivity
python3 -c "
import requests
response = requests.get(
    'https://your-company.atlassian.net/rest/api/2/myself',
    auth=('your-email@company.com', 'your-api-token')
)
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

## 🔒 Security Best Practices

### **Credential Management**
- ✅ Use Jenkins credentials for API tokens
- ✅ Never commit API tokens to version control
- ✅ Rotate API tokens regularly
- ✅ Use least-privilege access

### **Network Security**
- ✅ Use HTTPS for Jira API calls
- ✅ Configure firewall rules appropriately
- ✅ Use VPN if required by company policy

### **Access Control**
- ✅ Limit API token permissions
- ✅ Use service accounts for automation
- ✅ Monitor API usage and audit logs

## 📈 Monitoring and Analytics

### **Track Integration Usage**
```bash
# Monitor Jira API calls
grep "Jira issue" qa_automation.log

# Check success rates
grep "Created Jira issue\|Updated Jira issue" qa_automation.log | wc -l
```

### **Metrics to Monitor**
- Number of tickets created/updated
- Success/failure rates
- Response times
- Error patterns

## 🔮 Future Enhancements

- [ ] **Bulk Reporting**: Report multiple test runs to single ticket
- [ ] **Custom Templates**: User-defined Jira comment templates
- [ ] **Webhook Integration**: Real-time notifications
- [ ] **Dashboard Integration**: Embed test results in Jira dashboards
- [ ] **Test Case Linking**: Link individual tests to Jira test cases
- [ ] **Trend Analysis**: Historical test result trends in Jira

## 📞 Support

For issues with Jira integration:

1. **Check the troubleshooting section**
2. **Verify Jira credentials and permissions**
3. **Review Jenkins pipeline logs**
4. **Test with curl commands**
5. **Create an issue with detailed information**

## 📚 Related Documentation

- **[CI/CD Integration Guide](CI_CD_GUIDE.md)**: Complete CI/CD setup
- **[Jenkins Testing Summary](JENKINS_TESTING_SUMMARY.md)**: Jenkins pipeline guide
- **[README.md](README.md)**: Main framework documentation
