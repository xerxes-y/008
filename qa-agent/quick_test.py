#!/usr/bin/env python3
"""
Quick Test Script
Quick validation of the QA automation framework without running actual tests
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

async def quick_test():
    """Run a quick test of the framework"""
    print("🚀 Quick Test of QA Automation Framework")
    print("="*50)
    
    try:
        # Test 1: Import modules
        print("1. Testing module imports...")
        from config_manager import ConfigManager
        from test_orchestrator import TestOrchestrator
        print("   ✅ All modules imported successfully")
        
        # Test 2: Create configuration
        print("2. Testing configuration...")
        config = ConfigManager()
        print(f"   ✅ Configuration created")
        print(f"   - CI Mode: {config.is_ci_mode()}")
        print(f" - Max REST Tests: {config.test_config.max_rest_tests}")
        print(f" - Max Kafka Tests: {config.test_config.max_kafka_tests}")
        
        # Test 3: Create orchestrator
        print("3. Testing orchestrator...")
        orchestrator = TestOrchestrator(config)
        print("   ✅ Orchestrator created successfully")
        
        # Test 4: Test configuration file
        print("4. Testing configuration file...")
        test_config = {
            "test": {
                "max_rest_tests": 3,
                "max_kafka_tests": 2,
                "run_rest_tests": True,
                "run_kafka_tests": True,
                "run_database_tests": False,
                "run_integration_tests": False
            },
            "reporting": {
                "ci_mode": True,
                "fail_fast": False,
                "parallel_execution": False
            }
        }
        
        with open("quick_test_config.json", "w") as f:
            json.dump(test_config, f, indent=2)
        
        config_from_file = ConfigManager("quick_test_config.json")
        print("   ✅ Configuration loaded from file")
        
        # Test 5: Test CI runner
        print("5. Testing CI runner...")
        import subprocess
        result = subprocess.run([sys.executable, "ci_runner.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ CI runner works")
        else:
            print("   ⚠️ CI runner help failed")
        
        # Test 6: Generate mock report
        print("6. Testing report generation...")
        mock_results = [
            {
                "test_case": {"name": "Test 1", "type": "rest_api"},
                "status": "PASSED",
                "execution_time": 1.5,
                "timestamp": datetime.now().isoformat()
            },
            {
                "test_case": {"name": "Test 2", "type": "kafka"},
                "status": "PASSED", 
                "execution_time": 2.1,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        from result_reporter import ResultReporter
        reporter = ResultReporter()
        report = await reporter.generate_report(mock_results)
        
        print(f"   ✅ Report generated with {len(mock_results)} test results")
        print(f"   - Success Rate: {report['summary']['success_rate']}%")
        
        # Test 7: Save test report
        print("7. Testing report saving...")
        os.makedirs("test_results", exist_ok=True)
        report_file = f"test_results/quick_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"   ✅ Report saved to {report_file}")
        
        # Cleanup
        if os.path.exists("quick_test_config.json"):
            os.remove("quick_test_config.json")
        
        print("\n🎉 Quick test completed successfully!")
        print("Framework is ready for CI/CD integration.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
