#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the qa-agent directory to the path
sys.path.append('.')

from discovery import ServiceDiscovery
from test_generator import TestGenerator
from test_executor import TestExecutor

async def test_execution():
    print("=== TEST EXECUTION DEBUG ===")
    
    # Initialize components
    discovery = ServiceDiscovery()
    test_generator = TestGenerator("http://llm-runner:11434/api")
    test_executor = TestExecutor()
    
    # Discover services
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
    
    # Generate only Kafka tests
    print("\n2. Generating Kafka tests...")
    kafka_tests = await test_generator._generate_kafka_tests(kafka_topics)
    
    print(f"   - Generated {len(kafka_tests)} Kafka test cases")
    
    # Execute a few Kafka tests
    print("\n3. Executing Kafka tests...")
    for i, test_case in enumerate(kafka_tests[:3]):
        print(f"   Executing test {i+1}: {test_case.get('name', 'Unknown')}")
        try:
            result = await test_executor.execute_test(test_case)
            print(f"   Result: {result.get('status', 'Unknown')}")
            if result.get('status') == 'PASSED':
                print(f"   Message sent to topic: {result.get('message_sent', {}).get('topic', 'Unknown')}")
                print(f"   Partition: {result.get('message_sent', {}).get('partition', 'Unknown')}")
                print(f"   Offset: {result.get('message_sent', {}).get('offset', 'Unknown')}")
            else:
                print(f"   Error: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   Exception: {e}")
        print()

if __name__ == "__main__":
    asyncio.run(test_execution())
