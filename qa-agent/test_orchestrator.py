#!/usr/bin/env python3
"""
Test Orchestrator
Manages test execution for CI/CD environments with parallel execution, retries, and monitoring
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

from config_manager import ConfigManager
from discovery import ServiceDiscovery
from test_generator import TestGenerator
from test_executor import TestExecutor
from result_reporter import ResultReporter

logger = logging.getLogger(__name__)

@dataclass
class TestExecutionResult:
    """Test execution result with metadata"""
    test_case: Dict[str, Any]
    status: str
    execution_time: float
    timestamp: str
    error: Optional[str] = None
    retry_count: int = 0
    worker_id: Optional[str] = None

class TestOrchestrator:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.discovery = ServiceDiscovery()
        self.test_generator = TestGenerator(config.llm_config.api_url)
        self.test_executor = TestExecutor()
        self.result_reporter = ResultReporter()
        
        # Execution state
        self.running_tests = set()
        self.completed_tests = []
        self.failed_tests = []
        self.start_time = None
        self.execution_stats = {
            'total_tests': 0,
            'completed_tests': 0,
            'failed_tests': 0,
            'retried_tests': 0,
            'total_execution_time': 0
        }
        
        # Parallel execution
        self.semaphore = None
        self.executor = None
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
        if self.test_executor.session:
            asyncio.create_task(self.test_executor.session.close())
    
    async def run_test_suite(self, test_suite: str = "all") -> Dict[str, Any]:
        """Run complete test suite based on configuration"""
        logger.info(f"Starting test suite: {test_suite}")
        self.start_time = time.time()
        
        try:
            # Step 1: Discover services
            discovery_results = await self._discover_services()
            
            # Step 2: Generate tests based on suite type
            test_cases = await self._generate_tests_for_suite(discovery_results, test_suite)
            
            # Step 3: Execute tests
            results = await self._execute_tests(test_cases)
            
            # Step 4: Generate report
            report = await self._generate_report(results)
            
            # Step 5: Handle CI/CD specific actions
            await self._handle_ci_actions(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Test suite execution failed: {e}")
            raise
    
    async def _discover_services(self) -> Dict[str, Any]:
        """Discover services with error handling"""
        logger.info("Discovering services...")
        
        discovery_results = {}
        
        try:
            # Discover REST services
            if self.config.test_config.run_rest_tests:
                rest_services = await self.discovery.discover_rest_services()
                discovery_results['rest_services'] = rest_services
                logger.info(f"Discovered {len(rest_services)} REST services")
            
            # Discover Kafka topics
            if self.config.test_config.run_kafka_tests:
                kafka_topics = await self.discovery.discover_kafka_topics(
                    self.config.service_config.kafka_brokers
                )
                discovery_results['kafka_topics'] = kafka_topics
                logger.info(f"Discovered {len(kafka_topics)} Kafka topics")
            
            # Discover database schemas
            if self.config.test_config.run_database_tests:
                import psycopg2
                db_conn = psycopg2.connect(self.config.service_config.database_url)
                db_schemas = await self.discovery.discover_database_schemas(db_conn)
                discovery_results['database_schemas'] = db_schemas
                logger.info(f"Discovered {len(db_schemas)} database schemas")
            
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            if self.config.reporting_config.fail_fast:
                raise
        
        return discovery_results
    
    async def _generate_tests_for_suite(self, discovery_results: Dict[str, Any], 
                                      test_suite: str) -> List[Dict[str, Any]]:
        """Generate tests based on suite type"""
        logger.info(f"Generating tests for suite: {test_suite}")
        
        test_cases = []
        limits = self.config.get_test_limits()
        
        if test_suite == "smoke":
            # Quick smoke tests - minimal coverage
            limits = {k: min(v, 5) for k, v in limits.items()}
        elif test_suite == "regression":
            # Full regression tests
            pass
        elif test_suite == "performance":
            # Performance-focused tests
            self.config.test_config.include_performance_tests = True
        
        # Generate tests based on configuration
        if self.config.test_config.run_rest_tests and 'rest_services' in discovery_results:
            rest_tests = await self.test_generator._generate_rest_tests(
                discovery_results['rest_services']
            )
            test_cases.extend(rest_tests[:limits['rest_tests']])
        
        if self.config.test_config.run_kafka_tests and 'kafka_topics' in discovery_results:
            kafka_tests = await self.test_generator._generate_kafka_tests(
                discovery_results['kafka_topics']
            )
            test_cases.extend(kafka_tests[:limits['kafka_tests']])
        
        if self.config.test_config.run_database_tests and 'database_schemas' in discovery_results:
            db_tests = await self.test_generator._generate_database_tests(
                discovery_results['database_schemas']
            )
            test_cases.extend(db_tests[:limits['database_tests']])
        
        if self.config.test_config.run_integration_tests:
            integration_tests = await self.test_generator._generate_integration_tests(
                discovery_results
            )
            test_cases.extend(integration_tests[:limits['integration_tests']])
        
        logger.info(f"Generated {len(test_cases)} test cases")
        return test_cases
    
    async def _execute_tests(self, test_cases: List[Dict[str, Any]]) -> List[TestExecutionResult]:
        """Execute tests with parallel processing and retries"""
        logger.info(f"Executing {len(test_cases)} tests")
        
        self.execution_stats['total_tests'] = len(test_cases)
        
        if self.config.reporting_config.parallel_execution:
            return await self._execute_tests_parallel(test_cases)
        else:
            return await self._execute_tests_sequential(test_cases)
    
    async def _execute_tests_parallel(self, test_cases: List[Dict[str, Any]]) -> List[TestExecutionResult]:
        """Execute tests in parallel"""
        max_workers = self.config.reporting_config.max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        
        logger.info(f"Executing tests in parallel with {max_workers} workers")
        
        # Create tasks for all test cases
        tasks = []
        for i, test_case in enumerate(test_cases):
            task = asyncio.create_task(
                self._execute_single_test_with_retry(test_case, f"worker-{i % max_workers}")
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to TestExecutionResult
        execution_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task execution failed: {result}")
                # Create failed result
                execution_results.append(TestExecutionResult(
                    test_case={},
                    status='FAILED',
                    execution_time=0,
                    timestamp=datetime.now().isoformat(),
                    error=str(result)
                ))
            else:
                execution_results.append(result)
        
        return execution_results
    
    async def _execute_tests_sequential(self, test_cases: List[Dict[str, Any]]) -> List[TestExecutionResult]:
        """Execute tests sequentially"""
        logger.info("Executing tests sequentially")
        
        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"Executing test {i+1}/{len(test_cases)}: {test_case.get('name', 'Unknown')}")
            
            result = await self._execute_single_test_with_retry(test_case)
            results.append(result)
            
            # Check for fail-fast
            if (self.config.reporting_config.fail_fast and 
                result.status == 'FAILED' and 
                result.retry_count >= self.config.ci_config.max_retries):
                logger.error("Fail-fast enabled, stopping execution due to test failure")
                break
        
        return results
    
    async def _execute_single_test_with_retry(self, test_case: Dict[str, Any], 
                                            worker_id: Optional[str] = None) -> TestExecutionResult:
        """Execute a single test with retry logic"""
        max_retries = self.config.ci_config.max_retries
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                start_time = time.time()
                
                # Execute the test
                result = await self.test_executor.execute_test(test_case)
                
                execution_time = time.time() - start_time
                
                # Convert to TestExecutionResult
                execution_result = TestExecutionResult(
                    test_case=test_case,
                    status=result.get('status', 'UNKNOWN'),
                    execution_time=execution_time,
                    timestamp=datetime.now().isoformat(),
                    error=result.get('error'),
                    retry_count=retry_count,
                    worker_id=worker_id
                )
                
                # Update statistics
                self.execution_stats['completed_tests'] += 1
                self.execution_stats['total_execution_time'] += execution_time
                
                if execution_result.status == 'FAILED':
                    self.execution_stats['failed_tests'] += 1
                
                if retry_count > 0:
                    self.execution_stats['retried_tests'] += 1
                
                return execution_result
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Test execution failed (attempt {retry_count}/{max_retries + 1}): {e}")
                
                if retry_count > max_retries:
                    # Final failure
                    execution_time = time.time() - start_time
                    self.execution_stats['failed_tests'] += 1
                    
                    return TestExecutionResult(
                        test_case=test_case,
                        status='FAILED',
                        execution_time=execution_time,
                        timestamp=datetime.now().isoformat(),
                        error=str(e),
                        retry_count=retry_count,
                        worker_id=worker_id
                    )
                
                # Wait before retry
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
    
    async def _generate_report(self, results: List[TestExecutionResult]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        logger.info("Generating test report")
        
        # Convert TestExecutionResult to dict format expected by ResultReporter
        result_dicts = []
        for result in results:
            result_dict = {
                'test_case': result.test_case,
                'status': result.status,
                'execution_time': result.execution_time,
                'timestamp': result.timestamp,
                'error': result.error
            }
            result_dicts.append(result_dict)
        
        # Generate report
        report = await self.result_reporter.generate_report(result_dicts)
        
        # Add CI/CD specific information
        if self.config.is_ci_mode():
            report['ci_info'] = self.config.get_ci_info()
            report['execution_stats'] = self.execution_stats
        
        return report
    
    async def _handle_ci_actions(self, report: Dict[str, Any]):
        """Handle CI/CD specific actions"""
        if not self.config.is_ci_mode():
            return
        
        # Save report with CI metadata
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        build_info = f"build_{self.config.ci_config.build_number}" if self.config.ci_config.build_number else timestamp
        
        report_filename = f"test_report_{build_info}_{timestamp}.json"
        report_path = f"{self.config.reporting_config.output_dir}/{report_filename}"
        
        import json
        import os
        os.makedirs(self.config.reporting_config.output_dir, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"CI report saved to: {report_path}")
        
        # Check if tests passed for CI exit code
        success_rate = report.get('summary', {}).get('success_rate', 0)
        if success_rate < 100 and self.config.reporting_config.fail_fast:
            logger.error(f"Test suite failed with {100 - success_rate:.1f}% failure rate")
            sys.exit(1)
    
    def get_execution_summary(self) -> str:
        """Get execution summary for logging"""
        if not self.start_time:
            return "No execution started"
        
        total_time = time.time() - self.start_time
        success_rate = (self.execution_stats['completed_tests'] - self.execution_stats['failed_tests']) / self.execution_stats['total_tests'] * 100 if self.execution_stats['total_tests'] > 0 else 0
        
        summary = f"""
Test Execution Summary:
======================
Total Tests: {self.execution_stats['total_tests']}
Completed: {self.execution_stats['completed_tests']}
Failed: {self.execution_stats['failed_tests']}
Retried: {self.execution_stats['retried_tests']}
Success Rate: {success_rate:.1f}%
Total Execution Time: {total_time:.2f}s
Average Test Time: {self.execution_stats['total_execution_time'] / self.execution_stats['completed_tests']:.2f}s
"""
        return summary

