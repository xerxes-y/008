pipeline {
    agent any
    
    environment {
        // QA Automation Configuration
        QA_CONFIG_FILE = 'qa-config.json'
        TEST_OUTPUT_DIR = 'test_results'
        LOG_LEVEL = 'INFO'
        
        // Service URLs (can be overridden per environment)
        USER_SERVICE_URL = 'http://user-service:8000'
        ORDER_SERVICE_URL = 'http://order-service:8000'
        NOTIFICATION_SERVICE_URL = 'http://notification-service:8000'
        
        // LLM Configuration
        LLM_API_URL = 'http://llm-runner:11434/api'
        LLM_MODEL_NAME = 'llama2:7b'
        
        // Test Configuration
        MAX_REST_TESTS = '20'
        MAX_KAFKA_TESTS = '15'
        MAX_DATABASE_TESTS = '5'
        MAX_INTEGRATION_TESTS = '3'
        
        // CI Configuration
        CI_MODE = 'true'
        FAIL_FAST = 'true'
        PARALLEL_EXECUTION = 'true'
        MAX_WORKERS = '4'
        
        // Jira Integration Configuration
        JIRA_BASE_URL = 'https://your-company.atlassian.net'
        JIRA_USERNAME = 'your-email@company.com'
        JIRA_API_TOKEN = 'your-jira-api-token'
        JIRA_PROJECT_KEY = 'QA'
        JIRA_ISSUE_TYPE = 'Test Execution'
        JIRA_REPORTING_ENABLED = 'true'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    // Create test configuration file
                    def config = [
                        test: [
                            max_rest_tests: env.MAX_REST_TESTS.toInteger(),
                            max_kafka_tests: env.MAX_KAFKA_TESTS.toInteger(),
                            max_database_tests: env.MAX_DATABASE_TESTS.toInteger(),
                            max_integration_tests: env.MAX_INTEGRATION_TESTS.toInteger(),
                            run_rest_tests: true,
                            run_kafka_tests: true,
                            run_database_tests: true,
                            run_integration_tests: true,
                            include_negative_tests: true,
                            include_performance_tests: false
                        ],
                        llm: [
                            api_url: env.LLM_API_URL,
                            model_name: env.LLM_MODEL_NAME,
                            max_tokens: 2048,
                            temperature: 0.7,
                            timeout: 60
                        ],
                        services: [
                            user_service_url: env.USER_SERVICE_URL,
                            order_service_url: env.ORDER_SERVICE_URL,
                            notification_service_url: env.NOTIFICATION_SERVICE_URL,
                            kafka_brokers: 'kafka:29092',
                            database_url: 'postgresql://qa_user:qa_password@postgres:5432/qa_testing',
                            redis_url: 'redis://redis:6379'
                        ],
                        reporting: [
                            output_dir: env.TEST_OUTPUT_DIR,
                            report_format: 'json',
                            ci_mode: env.CI_MODE.toBoolean(),
                            fail_fast: env.FAIL_FAST.toBoolean(),
                            parallel_execution: env.PARALLEL_EXECUTION.toBoolean(),
                            max_workers: env.MAX_WORKERS.toInteger()
                        ],
                        ci: [
                            build_number: env.BUILD_NUMBER,
                            build_url: env.BUILD_URL,
                            git_branch: env.GIT_BRANCH,
                            git_commit: env.GIT_COMMIT,
                            workspace: env.WORKSPACE,
                            test_suite: 'regression',
                            environment: 'ci',
                            retry_failed: true,
                            max_retries: 3,
                            notify_on_failure: true,
                            notify_on_success: false
                        ]
                    ]
                    
                    writeJSON file: env.QA_CONFIG_FILE, json: config
                    
                    // Create output directory
                    sh "mkdir -p ${env.TEST_OUTPUT_DIR}"
                }
            }
        }
        
        stage('Start Infrastructure') {
            steps {
                script {
                    // Start Docker services
                    sh 'docker-compose up -d'
                    
                    // Wait for services to be ready
                    sh '''
                        echo "Waiting for services to be ready..."
                        sleep 30
                        
                        # Check if services are responding
                        timeout 60 bash -c 'until curl -f http://user-service:8000/health; do sleep 5; done'
                        timeout 60 bash -c 'until curl -f http://order-service:8000/health; do sleep 5; done'
                        timeout 60 bash -c 'until curl -f http://notification-service:8000/health; do sleep 5; done'
                        
                        echo "All services are ready!"
                    '''
                }
            }
        }
        
        stage('Run Smoke Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    changeRequest()
                }
            }
            steps {
                script {
                    // Run smoke tests first
                    sh '''
                        cd qa-agent
                        python ci_runner.py \
                            --config ../${QA_CONFIG_FILE} \
                            --test-suite smoke \
                            --fail-fast \
                            --log-level ${LOG_LEVEL} \
                            --output-dir ../${TEST_OUTPUT_DIR}
                    '''
                }
            }
            post {
                always {
                    // Archive test results
                    archiveArtifacts artifacts: "${TEST_OUTPUT_DIR}/**/*", allowEmptyArchive: true
                    
                    // Publish test results
                    publishTestResults testResultsPattern: "${TEST_OUTPUT_DIR}/**/*.json"
                }
                failure {
                    script {
                        // Send notification on failure
                        if (env.NOTIFY_ON_FAILURE == 'true') {
                            // Add notification logic here (Slack, email, etc.)
                            echo "Smoke tests failed - sending notification"
                        }
                    }
                }
            }
        }
        
        stage('Run Full Test Suite') {
            when {
                allOf {
                    anyOf {
                        branch 'main'
                        branch 'develop'
                    }
                    not {
                        changeRequest()
                    }
                }
            }
            steps {
                script {
                    // Run full regression test suite
                    sh '''
                        cd qa-agent
                        python ci_runner.py \
                            --config ../${QA_CONFIG_FILE} \
                            --test-suite regression \
                            --parallel \
                            --log-level ${LOG_LEVEL} \
                            --output-dir ../${TEST_OUTPUT_DIR} \
                            --max-workers ${MAX_WORKERS}
                    '''
                }
            }
            post {
                always {
                    // Archive test results
                    archiveArtifacts artifacts: "${TEST_OUTPUT_DIR}/**/*", allowEmptyArchive: true
                    
                    // Publish test results
                    publishTestResults testResultsPattern: "${TEST_OUTPUT_DIR}/**/*.json"
                    
                    // Generate test report
                    script {
                        if (fileExists("${TEST_OUTPUT_DIR}/test_report_*.json")) {
                            def reportFile = sh(
                                script: "ls -t ${TEST_OUTPUT_DIR}/test_report_*.json | head -1",
                                returnStdout: true
                            ).trim()
                            
                            def report = readJSON file: reportFile
                            def summary = report.summary
                            
                            echo """
                            Test Execution Summary:
                            =====================
                            Total Tests: ${summary.total_tests}
                            Passed: ${summary.passed}
                            Failed: ${summary.failed}
                            Success Rate: ${summary.success_rate}%
                            """
                        }
                    }
                }
                success {
                    script {
                        // Send success notification if configured
                        if (env.NOTIFY_ON_SUCCESS == 'true') {
                            echo "All tests passed - sending success notification"
                        }
                    }
                }
                failure {
                    script {
                        // Send failure notification
                        if (env.NOTIFY_ON_FAILURE == 'true') {
                            echo "Tests failed - sending failure notification"
                        }
                    }
                }
            }
        }
        
        stage('Performance Tests') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Run performance tests
                    sh '''
                        cd qa-agent
                        python ci_runner.py \
                            --config ../${QA_CONFIG_FILE} \
                            --test-suite performance \
                            --log-level ${LOG_LEVEL} \
                            --output-dir ../${TEST_OUTPUT_DIR}
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${TEST_OUTPUT_DIR}/**/*", allowEmptyArchive: true
                }
            }
        }
        
        stage('Jira Reporting') {
            when {
                allOf {
                    expression { env.JIRA_REPORTING_ENABLED == 'true' }
                    anyOf {
                        branch 'main'
                        branch 'develop'
                    }
                }
            }
            steps {
                script {
                    // Ask user for Jira ticket if not provided
                    def jiraTicket = input(
                        message: 'Enter Jira ticket key for test results reporting',
                        parameters: [
                            string(
                                name: 'JIRA_TICKET',
                                defaultValue: '',
                                description: 'Jira ticket key (e.g., QA-123) or leave empty to create new ticket'
                            ),
                            choice(
                                name: 'REPORT_ACTION',
                                choices: ['Create New Ticket', 'Update Existing Ticket', 'Skip Reporting'],
                                description: 'Choose reporting action'
                            )
                        ]
                    )
                    
                    // Check if we have test results to report
                    if (fileExists("${TEST_OUTPUT_DIR}/test_report_*.json")) {
                        def reportFile = sh(
                            script: "ls -t ${TEST_OUTPUT_DIR}/test_report_*.json | head -1",
                            returnStdout: true
                        ).trim()
                        
                        // Report to Jira based on user choice
                        if (jiraTicket.REPORT_ACTION == 'Create New Ticket') {
                            echo "Creating new Jira ticket for test results..."
                            sh '''
                                cd qa-agent
                                python jira_integration.py \
                                    --test-results ../${reportFile} \
                                    --build-number ${BUILD_NUMBER} \
                                    --build-url ${BUILD_URL} \
                                    --git-branch ${GIT_BRANCH} \
                                    --git-commit ${GIT_COMMIT} \
                                    --environment ci
                            '''
                        } else if (jiraTicket.REPORT_ACTION == 'Update Existing Ticket' && jiraTicket.JIRA_TICKET) {
                            echo "Updating Jira ticket ${jiraTicket.JIRA_TICKET} with test results..."
                            sh '''
                                cd qa-agent
                                python jira_integration.py \
                                    --test-results ../${reportFile} \
                                    --jira-ticket ${jiraTicket.JIRA_TICKET} \
                                    --build-number ${BUILD_NUMBER} \
                                    --build-url ${BUILD_URL} \
                                    --git-branch ${GIT_BRANCH} \
                                    --git-commit ${GIT_COMMIT} \
                                    --environment ci
                            '''
                        } else {
                            echo "Skipping Jira reporting as requested"
                        }
                    } else {
                        echo "No test results found for Jira reporting"
                    }
                }
            }
            post {
                always {
                    echo "Jira reporting stage completed"
                }
            }
        }
        
        stage('Cleanup') {
            always {
                script {
                    // Stop Docker services
                    sh 'docker-compose down'
                    
                    // Clean up temporary files
                    sh 'rm -f ${QA_CONFIG_FILE}'
                }
            }
        }
    }
    
    post {
        always {
            // Always archive logs
            archiveArtifacts artifacts: 'qa_automation.log', allowEmptyArchive: true
            
            // Clean workspace
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}

