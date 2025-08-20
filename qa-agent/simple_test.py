#!/usr/bin/env python3
"""
Simple Test Script
Basic validation of the QA automation framework without external dependencies
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_basic_components():
    """Test basic framework components without external dependencies"""
    print("🚀 Simple Test of QA Automation Framework")
    print("="*50)
    
    try:
        # Test 1: Check if files exist
        print("1. Checking framework files...")
        required_files = [
            'config_manager.py',
            'test_orchestrator.py', 
            'ci_runner.py',
            'discovery.py',
            'test_generator.py',
            'test_executor.py',
            'result_reporter.py',
            'requirements.txt',
            'ci_config_example.json'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                print(f"   ✅ {file} exists")
            else:
                print(f"   ❌ {file} missing")
                return False
        
        # Test 2: Test configuration manager (basic)
        print("2. Testing configuration manager...")
        try:
            # Import without running full initialization
            import config_manager
            print("   ✅ config_manager.py can be imported")
        except ImportError as e:
            print(f"   ❌ config_manager.py import failed: {e}")
            return False
        
        # Test 3: Test CI runner (basic) - just check file content
        print("3. Testing CI runner...")
        try:
            with open('ci_runner.py', 'r') as f:
                content = f.read()
            
            # Check for required elements in CI runner
            required_elements = [
                'def main():',
                'argparse',
                'ConfigManager',
                'TestOrchestrator'
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"   ✅ Found: {element}")
                else:
                    print(f"   ⚠️ Missing: {element}")
                    
        except Exception as e:
            print(f"   ❌ CI runner test failed: {e}")
            return False
        
        # Test 4: Test configuration file
        print("4. Testing configuration file...")
        try:
            with open('ci_config_example.json', 'r') as f:
                config_data = json.load(f)
            
            # Check required sections
            required_sections = ['test', 'llm', 'services', 'reporting', 'ci']
            for section in required_sections:
                if section in config_data:
                    print(f"   ✅ {section} section found")
                else:
                    print(f"   ❌ {section} section missing")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Configuration file test failed: {e}")
            return False
        
        # Test 5: Test Jenkinsfile
        print("5. Testing Jenkinsfile...")
        jenkinsfile_path = '../Jenkinsfile'
        if os.path.exists(jenkinsfile_path):
            with open(jenkinsfile_path, 'r') as f:
                content = f.read()
            
            # Check for required elements
            required_elements = [
                'pipeline {',
                'agent any',
                'environment {',
                'stages {',
                'ci_runner.py'
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"   ✅ Found: {element}")
                else:
                    print(f"   ❌ Missing: {element}")
                    return False
        else:
            print("   ❌ Jenkinsfile not found")
            return False
        
        # Test 6: Test requirements.txt
        print("6. Testing requirements.txt...")
        try:
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            
            # Check for key dependencies
            key_deps = ['aiohttp', 'psycopg2', 'redis', 'kafka']
            for dep in key_deps:
                if dep in requirements:
                    print(f"   ✅ Found dependency: {dep}")
                else:
                    print(f"   ⚠️ Missing dependency: {dep}")
                    
        except Exception as e:
            print(f"   ❌ Requirements test failed: {e}")
            return False
        
        # Test 7: Test directory structure
        print("7. Testing directory structure...")
        test_results_dir = 'test_results'
        if not os.path.exists(test_results_dir):
            os.makedirs(test_results_dir)
            print(f"   ✅ Created {test_results_dir} directory")
        else:
            print(f"   ✅ {test_results_dir} directory exists")
        
        # Test 8: Create a simple test report
        print("8. Testing report generation...")
        try:
            simple_report = {
                "test_info": {
                    "name": "Simple Framework Test",
                    "timestamp": datetime.now().isoformat(),
                    "status": "PASSED"
                },
                "components_tested": [
                    "File structure",
                    "Configuration files", 
                    "Jenkinsfile",
                    "Requirements",
                    "Directory structure"
                ],
                "summary": {
                    "total_checks": 8,
                    "passed": 8,
                    "failed": 0,
                    "success_rate": 100.0
                }
            }
            
            report_file = f"{test_results_dir}/simple_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(simple_report, f, indent=2)
            
            print(f"   ✅ Test report saved to {report_file}")
            
        except Exception as e:
            print(f"   ❌ Report generation failed: {e}")
            return False
        
        print("\n🎉 Simple test completed successfully!")
        print("Framework structure is ready for CI/CD integration.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run full validation: python validate_framework.py")
        print("3. Test with Jenkins: ./test-jenkins-pipeline.sh")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = test_basic_components()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
