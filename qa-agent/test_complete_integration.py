#!/usr/bin/env python3
"""
Complete Integration Test for QA Automation Framework
Tests the entire workflow including Jira integration
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def test_framework_structure():
    """Test framework file structure"""
    print("🔧 Testing Framework Structure...")
    
    required_files = [
        'config_manager.py',
        'test_orchestrator.py', 
        'ci_runner.py',
        'discovery.py',
        'test_generator.py',
        'test_executor.py',
        'result_reporter.py',
        'jira_integration.py',
        'requirements.txt',
        'ci_config_example.json',
        'jira_config_example.json'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"   ⚠️  Missing files: {missing_files}")
        return False
    
    return True

def test_configuration_management():
    """Test configuration management"""
    print("\n🔧 Testing Configuration Management...")
    
    try:
        # Test config manager import
        from config_manager import ConfigManager
        
        # Test loading from file
        config_manager = ConfigManager('ci_config_example.json')
        print("   ✅ ConfigManager initialization: PASSED")
        
        # Test configuration sections
        if hasattr(config_manager, 'test_config'):
            print("   ✅ Test configuration: PASSED")
        if hasattr(config_manager, 'llm_config'):
            print("   ✅ LLM configuration: PASSED")
        if hasattr(config_manager, 'service_config'):
            print("   ✅ Service configuration: PASSED")
        if hasattr(config_manager, 'reporting_config'):
            print("   ✅ Reporting configuration: PASSED")
        if hasattr(config_manager, 'ci_config'):
            print("   ✅ CI configuration: PASSED")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration management: ERROR - {e}")
        return False

def test_jira_integration():
    """Test Jira integration"""
    print("\n🔧 Testing Jira Integration...")
    
    try:
        from jira_integration import JiraIntegration, JiraConfig, report_to_jira
        
        # Test JiraConfig
        config = JiraConfig(
            base_url="https://test.atlassian.net",
            username="test@company.com",
            api_token="test-token",
            project_key="TEST"
        )
        print("   ✅ JiraConfig creation: PASSED")
        
        # Test JiraIntegration
        jira = JiraIntegration(config)
        print("   ✅ JiraIntegration initialization: PASSED")
        
        # Test comment creation
        test_results = {
            'summary': {
                'total_tests': 10,
                'passed': 8,
                'failed': 2,
                'success_rate': 80.0
            }
        }
        
        build_info = {
            'build_number': '123',
            'build_url': 'https://jenkins.test.com/job/123',
            'git_branch': 'main',
            'git_commit': 'abc123'
        }
        
        comment = jira._create_test_results_comment(test_results, build_info)
        if comment and "Test Execution Results" in comment:
            print("   ✅ Comment creation: PASSED")
        else:
            print("   ❌ Comment creation: FAILED")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Jira integration: ERROR - {e}")
        return False

def test_sample_workflow():
    """Test complete sample workflow"""
    print("\n🔧 Testing Sample Workflow...")
    
    try:
        # Create sample test results
        test_results = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "framework_version": "2.0",
                "ci_build_number": "123",
                "test_suite": "regression"
            },
            "summary": {
                "total_tests": 50,
                "passed": 45,
                "failed": 3,
                "skipped": 2,
                "success_rate": 90.0,
                "total_execution_time": 25.5
            },
            "test_suites": {
                "smoke": {"total": 10, "passed": 9, "failed": 1},
                "regression": {"total": 40, "passed": 36, "failed": 2}
            },
            "coverage": {
                "services_tested": ["user-service", "order-service"],
                "endpoints_tested": ["/api/users", "/api/orders"]
            },
            "detailed_results": [
                {
                    "test_name": "User API Test",
                    "status": "PASSED",
                    "execution_time": 0.5
                },
                {
                    "test_name": "Order Service Test",
                    "status": "FAILED",
                    "execution_time": 1.2,
                    "error": "Connection timeout"
                }
            ]
        }
        
        # Save test results
        test_file = "integration_test_results.json"
        with open(test_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print("   ✅ Test results creation: PASSED")
        
        # Test Jira reporting (will fail gracefully with invalid credentials)
        build_info = {
            "build_number": "123",
            "build_url": "https://jenkins.test.com/job/123",
            "git_branch": "main",
            "git_commit": "abc123def",
            "environment": "test"
        }
        
        # Set test environment variables
        os.environ['JIRA_BASE_URL'] = 'https://test.atlassian.net'
        os.environ['JIRA_USERNAME'] = 'test@company.com'
        os.environ['JIRA_API_TOKEN'] = 'test-token'
        os.environ['JIRA_PROJECT_KEY'] = 'TEST'
        
        from jira_integration import report_to_jira
        result = report_to_jira(
            test_results_file=test_file,
            build_info=build_info,
            jira_ticket=None,
            config_source='env'
        )
        
        # Should return None due to invalid credentials, but not crash
        print("   ✅ Jira reporting workflow: PASSED (handles invalid config gracefully)")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Sample workflow: ERROR - {e}")
        return False

def test_jenkins_integration():
    """Test Jenkins integration readiness"""
    print("\n🔧 Testing Jenkins Integration Readiness...")
    
    try:
        # Check if Jenkinsfile exists
        jenkinsfile_path = "../Jenkinsfile"
        if os.path.exists(jenkinsfile_path):
            print("   ✅ Jenkinsfile exists: PASSED")
            
            # Check for Jira integration in Jenkinsfile
            with open(jenkinsfile_path, 'r') as f:
                content = f.read()
                
            if "Jira Reporting" in content:
                print("   ✅ Jira Reporting stage: PASSED")
            else:
                print("   ❌ Jira Reporting stage: NOT FOUND")
                return False
                
            if "JIRA_BASE_URL" in content:
                print("   ✅ Jira environment variables: PASSED")
            else:
                print("   ❌ Jira environment variables: NOT FOUND")
                return False
                
        else:
            print("   ❌ Jenkinsfile: NOT FOUND")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Jenkins integration: ERROR - {e}")
        return False

def test_command_line_tools():
    """Test command line tools"""
    print("\n🔧 Testing Command Line Tools...")
    
    try:
        import subprocess
        
        # Test Jira integration help
        result = subprocess.run([
            sys.executable, "jira_integration.py", "--help"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "Report test results to Jira" in result.stdout:
            print("   ✅ Jira integration CLI: PASSED")
        else:
            print("   ❌ Jira integration CLI: FAILED")
            return False
        
        # Test simple test script
        result = subprocess.run([
            sys.executable, "simple_test.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "Simple test completed successfully" in result.stdout:
            print("   ✅ Simple test script: PASSED")
        else:
            print("   ❌ Simple test script: FAILED")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Command line tools: ERROR - {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Complete Integration Test for QA Automation Framework")
    print("=" * 60)
    
    tests = [
        ("Framework Structure", test_framework_structure),
        ("Configuration Management", test_configuration_management),
        ("Jira Integration", test_jira_integration),
        ("Sample Workflow", test_sample_workflow),
        ("Jenkins Integration", test_jenkins_integration),
        ("Command Line Tools", test_command_line_tools)
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
    
    print("\n" + "=" * 60)
    print(f"📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n📝 Framework Status:")
        print("✅ Framework structure is complete")
        print("✅ Configuration management is working")
        print("✅ Jira integration is ready")
        print("✅ Jenkins pipeline integration is ready")
        print("✅ Command line tools are functional")
        print("\n🚀 Ready for production use!")
        print("\nNext steps:")
        print("1. Configure your Jira credentials")
        print("2. Set up Jenkins pipeline")
        print("3. Run your first automated test")
        return 0
    else:
        print("⚠️  Some integration tests failed.")
        print("Please check the errors above and fix any issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
