#!/usr/bin/env python3
"""
Test script for Jira Integration
Demonstrates and validates Jira integration functionality
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def create_sample_test_results():
    """Create sample test results for testing"""
    return {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
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
            "parallel_execution": True,
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
            "endpoints_tested": ["/api/users", "/api/orders", "/api/notifications"],
            "kafka_topics_tested": ["user-events", "order-events"],
            "database_tables_tested": ["users", "orders", "notifications"]
        },
        "failures": {
            "total_failures": 5,
            "failure_types": {
                "connection_timeout": 2,
                "validation_error": 2,
                "database_error": 1
            },
            "common_errors": [
                "Connection timeout to user-service",
                "Invalid order data format",
                "Database constraint violation"
            ]
        },
        "performance": {
            "slow_tests": [
                {"test_name": "User API Performance Test", "execution_time": 2.5},
                {"test_name": "Order Processing Test", "execution_time": 1.8}
            ],
            "performance_by_type": {
                "rest_api": {"avg_time": 0.3, "max_time": 2.5},
                "kafka": {"avg_time": 0.1, "max_time": 0.5},
                "database": {"avg_time": 0.2, "max_time": 1.0}
            }
        },
        "recommendations": [
            "Optimize user-service response times",
            "Add retry logic for flaky tests",
            "Consider database connection pooling"
        ],
        "detailed_results": [
            {
                "test_name": "User API Test",
                "status": "PASSED",
                "execution_time": 0.3,
                "test_type": "rest_api",
                "service": "user-service"
            },
            {
                "test_name": "Order Creation Test",
                "status": "FAILED",
                "execution_time": 1.2,
                "test_type": "integration",
                "service": "order-service",
                "error": "Database constraint violation"
            }
        ]
    }

def test_jira_config_loading():
    """Test Jira configuration loading"""
    print("🔧 Testing Jira Configuration Loading...")
    
    # Test environment variable loading
    os.environ['JIRA_BASE_URL'] = 'https://test.atlassian.net'
    os.environ['JIRA_USERNAME'] = 'test@company.com'
    os.environ['JIRA_API_TOKEN'] = 'test-token'
    os.environ['JIRA_PROJECT_KEY'] = 'TEST'
    
    try:
        from jira_integration import load_jira_config_from_env
        config = load_jira_config_from_env()
        
        if config:
            print("   ✅ Environment config loading: PASSED")
            print(f"      Base URL: {config.base_url}")
            print(f"      Project: {config.project_key}")
        else:
            print("   ❌ Environment config loading: FAILED")
            return False
            
    except Exception as e:
        print(f"   ❌ Environment config loading: ERROR - {e}")
        return False
    
    # Test file config loading
    config_data = {
        "base_url": "https://test.atlassian.net",
        "username": "test@company.com",
        "api_token": "test-token",
        "project_key": "TEST",
        "issue_type": "Test Execution"
    }
    
    config_file = "test_jira_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    
    try:
        from jira_integration import load_jira_config_from_file
        config = load_jira_config_from_file(config_file)
        
        if config:
            print("   ✅ File config loading: PASSED")
            print(f"      Issue Type: {config.issue_type}")
        else:
            print("   ❌ File config loading: FAILED")
            return False
            
    except Exception as e:
        print(f"   ❌ File config loading: ERROR - {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(config_file):
            os.remove(config_file)
    
    return True

def test_jira_integration_class():
    """Test JiraIntegration class"""
    print("\n🔧 Testing JiraIntegration Class...")
    
    try:
        from jira_integration import JiraIntegration, JiraConfig
        
        # Create test config
        config = JiraConfig(
            base_url="https://test.atlassian.net",
            username="test@company.com",
            api_token="test-token",
            project_key="TEST"
        )
        
        # Initialize integration
        jira = JiraIntegration(config)
        print("   ✅ JiraIntegration initialization: PASSED")
        
        # Test comment creation
        test_results = create_sample_test_results()
        build_info = {
            "build_number": "123",
            "build_url": "https://jenkins.test.com/job/123",
            "git_branch": "main",
            "git_commit": "abc123",
            "environment": "test"
        }
        
        comment = jira._create_test_results_comment(test_results, build_info)
        if comment and "Test Execution Results" in comment:
            print("   ✅ Comment creation: PASSED")
        else:
            print("   ❌ Comment creation: FAILED")
            return False
            
    except Exception as e:
        print(f"   ❌ JiraIntegration class: ERROR - {e}")
        return False
    
    return True

def test_report_function():
    """Test report_to_jira function"""
    print("\n🔧 Testing report_to_jira Function...")
    
    try:
        from jira_integration import report_to_jira
        
        # Create sample test results file
        test_results = create_sample_test_results()
        test_file = "sample_test_results.json"
        
        with open(test_file, 'w') as f:
            json.dump(test_results, f)
        
        build_info = {
            "build_number": "123",
            "build_url": "https://jenkins.test.com/job/123",
            "git_branch": "main",
            "git_commit": "abc123",
            "environment": "test"
        }
        
        # Test with mock config (will fail but should handle gracefully)
        result = report_to_jira(
            test_results_file=test_file,
            build_info=build_info,
            jira_ticket=None,
            config_source='env'
        )
        
        # Should return None due to invalid credentials, but not crash
        print("   ✅ report_to_jira function: PASSED (handles invalid config gracefully)")
        
    except Exception as e:
        print(f"   ❌ report_to_jira function: ERROR - {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
    
    return True

def test_command_line_interface():
    """Test command line interface"""
    print("\n🔧 Testing Command Line Interface...")
    
    try:
        # Create sample test results file
        test_results = create_sample_test_results()
        test_file = "sample_test_results.json"
        
        with open(test_file, 'w') as f:
            json.dump(test_results, f)
        
        # Test help
        import subprocess
        result = subprocess.run([
            sys.executable, "jira_integration.py", "--help"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "Report test results to Jira" in result.stdout:
            print("   ✅ Command line help: PASSED")
        else:
            print("   ❌ Command line help: FAILED")
            return False
        
        # Test with invalid arguments (should show usage)
        result = subprocess.run([
            sys.executable, "jira_integration.py"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("   ✅ Command line argument validation: PASSED")
        else:
            print("   ❌ Command line argument validation: FAILED")
            return False
            
    except Exception as e:
        print(f"   ❌ Command line interface: ERROR - {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Jira Integration Components")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_jira_config_loading),
        ("JiraIntegration Class", test_jira_integration_class),
        ("Report Function", test_report_function),
        ("Command Line Interface", test_command_line_interface)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Jira integration is ready to use.")
        print("\n📝 Next Steps:")
        print("1. Configure your Jira credentials")
        print("2. Test with a real Jira instance")
        print("3. Integrate with your Jenkins pipeline")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
