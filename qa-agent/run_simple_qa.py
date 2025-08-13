#!/usr/bin/env python3
import asyncio
import sys
import os
import json
from datetime import datetime

# Add the qa-agent directory to the path
sys.path.append('.')

from discovery import ServiceDiscovery
from test_generator import TestGenerator
from test_executor import TestExecutor
from result_reporter import ResultReporter

async def run_simple_qa():
    print("=== RUNNING SIMPLE QA CYCLE ===")
    
    # Initialize components
    discovery = ServiceDiscovery()
    test_generator = TestGenerator("http://llm-runner:11434/api")
    test_executor = TestExecutor()
    result_reporter = ResultReporter()
    
    try:
        # Step 1: Discover services
        print("1. Discovering services...")
        rest_services = await discovery.discover_rest_services()
        kafka_topics = await discovery.discover_kafka_topics('kafka:29092')
        
        import psycopg2
        db_conn = psycopg2.connect("postgresql://qa_user:qa_password@postgres:5432/qa_testing")
        db_schemas = await discovery.discover_database_schemas(db_conn)
        
        discovery_results = {
            'rest_services': rest_services,
            'kafka_topics': kafka_topics,
            'database_schemas': db_schemas
        }
        
        print(f"   - REST Services: {len(rest_services)}")
        print(f"   - Kafka Topics: {len(kafka_topics)}")
        print(f"   - Database Schemas: {len(db_schemas)}")
        
        # Step 2: Generate limited tests
        print("\n2. Generating limited tests...")
        
        # Generate only Kafka tests for now
        kafka_tests = await test_generator._generate_kafka_tests(kafka_topics)
        print(f"   - Generated {len(kafka_tests)} Kafka tests")
        
        # Generate a few REST tests
        rest_tests = []
        if rest_services:
            # Take only first service and first endpoint
            service = rest_services[0]
            if service.get('endpoints'):
                endpoint = service['endpoints'][0]
                positive_tests = await test_generator._generate_rest_positive_tests(
                    service['service_name'], service['service_url'], endpoint
                )
                rest_tests.extend(positive_tests[:2])  # Only 2 tests
        
        print(f"   - Generated {len(rest_tests)} REST tests")
        
        all_tests = kafka_tests + rest_tests
        print(f"   - Total tests: {len(all_tests)}")
        
        # Step 3: Execute tests
        print("\n3. Executing tests...")
        results = []
        for i, test_case in enumerate(all_tests):
            print(f"   Executing test {i+1}/{len(all_tests)}: {test_case.get('name', 'Unknown')}")
            try:
                result = await test_executor.execute_test(test_case)
                results.append(result)
                print(f"   Result: {result.get('status', 'Unknown')}")
            except Exception as e:
                print(f"   Error: {e}")
                results.append({
                    'test_case': test_case,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Step 4: Generate report
        print("\n4. Generating report...")
        report = await result_reporter.generate_report(results)
        
        # Save report
        report_file = f"test_results/simple_qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('test_results', exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   - Report saved to: {report_file}")
        
        # Print summary
        print("\n=== QA CYCLE COMPLETED ===")
        print(f"Total tests: {len(results)}")
        passed = len([r for r in results if r.get('status') == 'PASSED'])
        failed = len([r for r in results if r.get('status') == 'FAILED'])
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        # Show Kafka test results specifically
        kafka_results = [r for r in results if r.get('test_case', {}).get('type') == 'kafka']
        if kafka_results:
            print(f"\nKafka Tests: {len(kafka_results)}")
            kafka_passed = len([r for r in kafka_results if r.get('status') == 'PASSED'])
            print(f"Kafka Tests Passed: {kafka_passed}")
        
    except Exception as e:
        print(f"Error in QA cycle: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_simple_qa())
