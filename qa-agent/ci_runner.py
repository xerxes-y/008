#!/usr/bin/env python3
"""
CI Runner
Main entry point for CI/CD integration with Jenkins and other CI systems
"""

import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path

from config_manager import ConfigManager
from test_orchestrator import TestOrchestrator

# Configure logging for CI environment
def setup_logging(level: str = "INFO"):
    """Setup logging configuration for CI environment"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if level.upper() == "DEBUG":
        log_level = logging.DEBUG
    elif level.upper() == "INFO":
        log_level = logging.INFO
    elif level.upper() == "WARNING":
        log_level = logging.WARNING
    elif level.upper() == "ERROR":
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('qa_automation.log')
        ]
    )

async def run_ci_tests(config_file: str = None, test_suite: str = "all", 
                      fail_fast: bool = False, parallel: bool = False):
    """Run CI tests with the specified configuration"""
    
    # Initialize configuration
    config = ConfigManager(config_file)
    
    # Override configuration with command line arguments
    if fail_fast:
        config.reporting_config.fail_fast = True
    if parallel:
        config.reporting_config.parallel_execution = True
    
    # Setup logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    # Log configuration summary
    logger.info("Starting CI Test Execution")
    logger.info(config.get_summary())
    
    try:
        # Initialize test orchestrator
        orchestrator = TestOrchestrator(config)
        
        # Run test suite
        logger.info(f"Running test suite: {test_suite}")
        report = await orchestrator.run_test_suite(test_suite)
        
        # Log execution summary
        logger.info(orchestrator.get_execution_summary())
        
        # Check results
        success_rate = report.get('summary', {}).get('success_rate', 0)
        total_tests = report.get('summary', {}).get('total_tests', 0)
        failed_tests = report.get('summary', {}).get('failed', 0)
        
        logger.info(f"Test execution completed:")
        logger.info(f"  - Total Tests: {total_tests}")
        logger.info(f"  - Success Rate: {success_rate:.1f}%")
        logger.info(f"  - Failed Tests: {failed_tests}")
        
        # Exit with appropriate code for CI
        if failed_tests > 0 and config.reporting_config.fail_fast:
            logger.error("Test suite failed - exiting with code 1")
            sys.exit(1)
        else:
            logger.info("Test suite completed successfully")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)

def main():
    """Main entry point for CI runner"""
    parser = argparse.ArgumentParser(description='QA Automation CI Runner')
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file (JSON)'
    )
    
    parser.add_argument(
        '--test-suite', '-t',
        type=str,
        choices=['all', 'smoke', 'regression', 'performance'],
        default='all',
        help='Test suite to run (default: all)'
    )
    
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop execution on first failure'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='test_results',
        help='Output directory for test results (default: test_results)'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of parallel workers (default: 4)'
    )
    
    args = parser.parse_args()
    
    # Set environment variables from arguments
    os.environ['LOG_LEVEL'] = args.log_level
    os.environ['TEST_OUTPUT_DIR'] = args.output_dir
    os.environ['MAX_WORKERS'] = str(args.max_workers)
    
    if args.fail_fast:
        os.environ['FAIL_FAST'] = 'true'
    
    if args.parallel:
        os.environ['PARALLEL_EXECUTION'] = 'true'
    
    # Run the tests
    asyncio.run(run_ci_tests(
        config_file=args.config,
        test_suite=args.test_suite,
        fail_fast=args.fail_fast,
        parallel=args.parallel
    ))

if __name__ == "__main__":
    main()

