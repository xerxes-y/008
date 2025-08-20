#!/usr/bin/env python3
"""
Framework Validation Script
Tests if all components of the QA automation framework work correctly
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from config_manager import ConfigManager
        print("✅ ConfigManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ConfigManager: {e}")
        return False
    
    try:
        from test_orchestrator import TestOrchestrator
        print("✅ TestOrchestrator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TestOrchestrator: {e}")
        return False
    
    try:
        from discovery import ServiceDiscovery
        print("✅ ServiceDiscovery imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ServiceDiscovery: {e}")
        return False
    
    try:
        from test_generator import TestGenerator
        print("✅ TestGenerator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TestGenerator: {e}")
        return False
    
    try:
        from test_executor import TestExecutor
        print("✅ TestExecutor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TestExecutor: {e}")
        return False
    
    try:
        from result_reporter import ResultReporter
        print("✅ ResultReporter imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ResultReporter: {e}")
        return False
    
    return True

def test_config_manager():
    """Test configuration manager functionality"""
    print("\n🔍 Testing configuration manager...")
    
    try:
        from config_manager import ConfigManager
        
        # Test default configuration
        config = ConfigManager()
        print("✅ ConfigManager created with default config")
        
        # Test configuration summary
        summary = config.get_summary()
        if "Configuration Summary" in summary:
            print("✅ Configuration summary generated")
        else:
            print("❌ Configuration summary failed")
            return False
        
        # Test environment variable loading
        os.environ['CI_MODE'] = 'true'
        os.environ['MAX_REST_TESTS'] = '10'
        
        config_with_env = ConfigManager()
        if config_with_env.is_ci_mode():
            print("✅ Environment variables loaded correctly")
        else:
            print("❌ Environment variables not loaded")
            return False
        
        # Test test limits
        limits = config_with_env.get_test_limits()
        if limits['rest_tests'] == 10:
            print("✅ Test limits configured correctly")
        else:
            print("❌ Test limits not configured correctly")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager test failed: {e}")
        return False

def test_ci_runner():
    """Test CI runner functionality"""
    print("\n🔍 Testing CI runner...")
    
    try:
        # Test if ci_runner.py exists and can be imported
        if not os.path.exists('ci_runner.py'):
            print("❌ ci_runner.py not found")
            return False
        
        # Test command line interface
        import subprocess
        result = subprocess.run([sys.executable, 'ci_runner.py', '--help'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ CI runner help command works")
        else:
            print("❌ CI runner help command failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CI runner test failed: {e}")
        return False

def test_configuration_file():
    """Test configuration file creation and loading"""
    print("\n🔍 Testing configuration file...")
    
    try:
        from config_manager import ConfigManager
        
        # Create a test configuration
        test_config = {
            "test": {
                "max_rest_tests": 5,
                "max_kafka_tests": 3,
                "run_rest_tests": True,
                "run_kafka_tests": True,
                "run_database_tests": False,
                "run_integration_tests": False
            },
            "llm": {
                "api_url": "http://test-llm:11434/api",
                "model_name": "test-model"
            },
            "services": {
                "user_service_url": "http://test-user:8000",
                "kafka_brokers": "test-kafka:29092"
            },
            "reporting": {
                "output_dir": "test_results",
                "ci_mode": True,
                "fail_fast": False,
                "parallel_execution": False
            },
            "ci": {
                "test_suite": "smoke",
                "environment": "test",
                "max_retries": 2
            }
        }
        
        # Save test configuration
        test_config_file = "test_config.json"
        with open(test_config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        print("✅ Test configuration file created")
        
        # Load configuration from file
        config = ConfigManager(test_config_file)
        
        # Verify configuration was loaded
        if config.test_config.max_rest_tests == 5:
            print("✅ Configuration loaded from file")
        else:
            print("❌ Configuration not loaded from file")
            return False
        
        # Cleanup
        os.remove(test_config_file)
        print("✅ Test configuration file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration file test failed: {e}")
        return False

def test_mock_orchestrator():
    """Test orchestrator with mock data"""
    print("\n🔍 Testing test orchestrator...")
    
    try:
        from config_manager import ConfigManager
        from test_orchestrator import TestOrchestrator
        
        # Create minimal configuration
        config = ConfigManager()
        config.test_config.max_rest_tests = 1
        config.test_config.max_kafka_tests = 1
        config.test_config.run_database_tests = False
        config.test_config.run_integration_tests = False
        config.reporting_config.ci_mode = True
        config.reporting_config.fail_fast = False
        
        # Create orchestrator
        orchestrator = TestOrchestrator(config)
        print("✅ TestOrchestrator created successfully")
        
        # Test execution summary (before execution)
        summary = orchestrator.get_execution_summary()
        if "No execution started" in summary:
            print("✅ Execution summary works correctly")
        else:
            print("❌ Execution summary not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock orchestrator test failed: {e}")
        return False

def test_jenkinsfile_validation():
    """Test if Jenkinsfile is valid"""
    print("\n🔍 Testing Jenkinsfile...")
    
    try:
        jenkinsfile_path = Path("../Jenkinsfile")
        if not jenkinsfile_path.exists():
            print("❌ Jenkinsfile not found")
            return False
        
        with open(jenkinsfile_path, 'r') as f:
            content = f.read()
        
        # Check for required pipeline elements
        required_elements = [
            "pipeline {",
            "agent any",
            "environment {",
            "stages {",
            "stage(",
            "post {"
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ Found required element: {element}")
            else:
                print(f"❌ Missing required element: {element}")
                return False
        
        # Check for QA automation specific elements
        qa_elements = [
            "QA_CONFIG_FILE",
            "TEST_OUTPUT_DIR",
            "ci_runner.py",
            "test-suite",
            "archiveArtifacts"
        ]
        
        for element in qa_elements:
            if element in content:
                print(f"✅ Found QA element: {element}")
            else:
                print(f"⚠️ Missing QA element: {element}")
        
        print("✅ Jenkinsfile validation completed")
        return True
        
    except Exception as e:
        print(f"❌ Jenkinsfile validation failed: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        'aiohttp',
        'asyncio',
        'psycopg2',
        'redis',
        'kafka',
        'json',
        'logging',
        'datetime'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def generate_validation_report(results):
    """Generate validation report"""
    print("\n" + "="*50)
    print("VALIDATION REPORT")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! Framework is ready for CI/CD integration.")
        return True
    else:
        print(f"\n⚠️ {failed_tests} test(s) failed. Please fix issues before CI/CD integration.")
        return False

async def main():
    """Main validation function"""
    print("🧪 QA Automation Framework Validation")
    print("="*50)
    
    results = {}
    
    # Run all validation tests
    results['Module Imports'] = test_imports()
    results['Dependencies'] = test_dependencies()
    results['Configuration Manager'] = test_config_manager()
    results['Configuration File'] = test_configuration_file()
    results['CI Runner'] = test_ci_runner()
    results['Test Orchestrator'] = test_mock_orchestrator()
    results['Jenkinsfile'] = test_jenkinsfile_validation()
    
    # Generate report
    success = generate_validation_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
