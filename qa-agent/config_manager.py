#!/usr/bin/env python3
"""
Configuration Manager
Manages configuration for CI/CD environments and different testing scenarios
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Test execution configuration"""
    # Test limits
    max_rest_tests: int = 50
    max_kafka_tests: int = 30
    max_database_tests: int = 10
    max_integration_tests: int = 5
    
    # Timeouts
    rest_timeout: int = 30
    kafka_timeout: int = 60
    database_timeout: int = 30
    integration_timeout: int = 120
    
    # Test categories to run
    run_rest_tests: bool = True
    run_kafka_tests: bool = True
    run_database_tests: bool = True
    run_integration_tests: bool = True
    
    # Test data
    test_data_size: str = "small"  # small, medium, large
    include_negative_tests: bool = True
    include_performance_tests: bool = False

@dataclass
class LLMConfig:
    """LLM configuration"""
    api_url: str = "http://llm-runner:11434/api"
    model_name: str = "llama2:7b"
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 60

@dataclass
class ServiceConfig:
    """Service endpoints configuration"""
    user_service_url: str = "http://user-service:8000"
    order_service_url: str = "http://order-service:8000"
    notification_service_url: str = "http://notification-service:8000"
    spring_boot_service_url: str = "http://spring-boot-service:8004"
    
    kafka_brokers: str = "kafka:29092"
    database_url: str = "postgresql://qa_user:qa_password@postgres:5432/qa_testing"
    redis_url: str = "redis://redis:6379"

@dataclass
class ReportingConfig:
    """Reporting configuration"""
    output_dir: str = "test_results"
    report_format: str = "json"  # json, html, xml
    include_screenshots: bool = False
    include_logs: bool = True
    detailed_reporting: bool = True
    
    # CI/CD specific
    ci_mode: bool = False
    fail_fast: bool = False
    parallel_execution: bool = False
    max_workers: int = 4

@dataclass
class CIConfig:
    """CI/CD specific configuration"""
    # Jenkins/Build environment
    build_number: Optional[str] = None
    build_url: Optional[str] = None
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    workspace: Optional[str] = None
    
    # Test execution
    test_suite: str = "all"  # all, smoke, regression, performance
    environment: str = "ci"  # ci, staging, production
    retry_failed: bool = True
    max_retries: int = 3
    
    # Notifications
    notify_on_failure: bool = True
    notify_on_success: bool = False
    slack_webhook: Optional[str] = None
    email_recipients: Optional[str] = None

class ConfigManager:
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.test_config = TestConfig()
        self.llm_config = LLMConfig()
        self.service_config = ServiceConfig()
        self.reporting_config = ReportingConfig()
        self.ci_config = CIConfig()
        
        self._load_config()
        self._load_environment_variables()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update configurations from file
                if 'test' in config_data:
                    self._update_dataclass(self.test_config, config_data['test'])
                if 'llm' in config_data:
                    self._update_dataclass(self.llm_config, config_data['llm'])
                if 'services' in config_data:
                    self._update_dataclass(self.service_config, config_data['services'])
                if 'reporting' in config_data:
                    self._update_dataclass(self.reporting_config, config_data['reporting'])
                if 'ci' in config_data:
                    self._update_dataclass(self.ci_config, config_data['ci'])
                    
                logger.info(f"Loaded configuration from {self.config_file}")
                
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        # Test configuration
        self.test_config.max_rest_tests = int(os.getenv('MAX_REST_TESTS', self.test_config.max_rest_tests))
        self.test_config.max_kafka_tests = int(os.getenv('MAX_KAFKA_TESTS', self.test_config.max_kafka_tests))
        self.test_config.max_database_tests = int(os.getenv('MAX_DATABASE_TESTS', self.test_config.max_database_tests))
        self.test_config.max_integration_tests = int(os.getenv('MAX_INTEGRATION_TESTS', self.test_config.max_integration_tests))
        
        self.test_config.run_rest_tests = os.getenv('RUN_REST_TESTS', 'true').lower() == 'true'
        self.test_config.run_kafka_tests = os.getenv('RUN_KAFKA_TESTS', 'true').lower() == 'true'
        self.test_config.run_database_tests = os.getenv('RUN_DATABASE_TESTS', 'true').lower() == 'true'
        self.test_config.run_integration_tests = os.getenv('RUN_INTEGRATION_TESTS', 'true').lower() == 'true'
        
        # LLM configuration
        self.llm_config.api_url = os.getenv('LLM_API_URL', self.llm_config.api_url)
        self.llm_config.model_name = os.getenv('LLM_MODEL_NAME', self.llm_config.model_name)
        
        # Service configuration
        self.service_config.user_service_url = os.getenv('USER_SERVICE_URL', self.service_config.user_service_url)
        self.service_config.order_service_url = os.getenv('ORDER_SERVICE_URL', self.service_config.order_service_url)
        self.service_config.notification_service_url = os.getenv('NOTIFICATION_SERVICE_URL', self.service_config.notification_service_url)
        self.service_config.kafka_brokers = os.getenv('KAFKA_BROKERS', self.service_config.kafka_brokers)
        self.service_config.database_url = os.getenv('DATABASE_URL', self.service_config.database_url)
        
        # Reporting configuration
        self.reporting_config.output_dir = os.getenv('TEST_OUTPUT_DIR', self.reporting_config.output_dir)
        self.reporting_config.ci_mode = os.getenv('CI_MODE', 'false').lower() == 'true'
        self.reporting_config.fail_fast = os.getenv('FAIL_FAST', 'false').lower() == 'true'
        self.reporting_config.parallel_execution = os.getenv('PARALLEL_EXECUTION', 'false').lower() == 'true'
        
        # CI configuration
        self.ci_config.build_number = os.getenv('BUILD_NUMBER')
        self.ci_config.build_url = os.getenv('BUILD_URL')
        self.ci_config.git_branch = os.getenv('GIT_BRANCH') or os.getenv('BRANCH_NAME')
        self.ci_config.git_commit = os.getenv('GIT_COMMIT') or os.getenv('COMMIT_SHA')
        self.ci_config.workspace = os.getenv('WORKSPACE')
        self.ci_config.test_suite = os.getenv('TEST_SUITE', 'all')
        self.ci_config.environment = os.getenv('ENVIRONMENT', 'ci')
        
        # Auto-detect CI environment
        if any(env_var in os.environ for env_var in ['JENKINS_URL', 'BUILD_NUMBER', 'CI', 'TRAVIS']):
            self.reporting_config.ci_mode = True
            self.ci_config.environment = 'ci'
    
    def _update_dataclass(self, dataclass_instance, data_dict: Dict[str, Any]):
        """Update dataclass instance with dictionary data"""
        for key, value in data_dict.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)
    
    def get_test_limits(self) -> Dict[str, int]:
        """Get test execution limits"""
        return {
            'rest_tests': self.test_config.max_rest_tests,
            'kafka_tests': self.test_config.max_kafka_tests,
            'database_tests': self.test_config.max_database_tests,
            'integration_tests': self.test_config.max_integration_tests
        }
    
    def get_timeouts(self) -> Dict[str, int]:
        """Get timeout configurations"""
        return {
            'rest_api': self.test_config.rest_timeout,
            'kafka': self.test_config.kafka_timeout,
            'database': self.test_config.database_timeout,
            'integration': self.test_config.integration_timeout
        }
    
    def get_enabled_test_types(self) -> Dict[str, bool]:
        """Get enabled test types"""
        return {
            'rest_api': self.test_config.run_rest_tests,
            'kafka': self.test_config.run_kafka_tests,
            'database': self.test_config.run_database_tests,
            'integration': self.test_config.run_integration_tests
        }
    
    def is_ci_mode(self) -> bool:
        """Check if running in CI mode"""
        return self.reporting_config.ci_mode
    
    def get_ci_info(self) -> Dict[str, Any]:
        """Get CI environment information"""
        return asdict(self.ci_config)
    
    def save_config(self, output_file: str):
        """Save current configuration to file"""
        config_data = {
            'test': asdict(self.test_config),
            'llm': asdict(self.llm_config),
            'services': asdict(self.service_config),
            'reporting': asdict(self.reporting_config),
            'ci': asdict(self.ci_config)
        }
        
        with open(output_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Configuration saved to {output_file}")
    
    def get_summary(self) -> str:
        """Get configuration summary"""
        summary = f"""
Configuration Summary:
====================
Test Configuration:
- Max REST Tests: {self.test_config.max_rest_tests}
- Max Kafka Tests: {self.test_config.max_kafka_tests}
- Max Database Tests: {self.test_config.max_database_tests}
- Max Integration Tests: {self.test_config.max_integration_tests}
- Enabled Test Types: {', '.join([k for k, v in self.get_enabled_test_types().items() if v])}

LLM Configuration:
- API URL: {self.llm_config.api_url}
- Model: {self.llm_config.model_name}

Reporting Configuration:
- Output Directory: {self.reporting_config.output_dir}
- CI Mode: {self.reporting_config.ci_mode}
- Fail Fast: {self.reporting_config.fail_fast}
- Parallel Execution: {self.reporting_config.parallel_execution}

CI Configuration:
- Environment: {self.ci_config.environment}
- Test Suite: {self.ci_config.test_suite}
- Build Number: {self.ci_config.build_number or 'N/A'}
- Git Branch: {self.ci_config.git_branch or 'N/A'}
"""
        return summary

