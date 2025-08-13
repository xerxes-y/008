#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the qa-agent directory to the path
sys.path.append('.')

from discovery import ServiceDiscovery
from test_generator import TestGenerator

async def test_generation():
    print("=== TEST GENERATION DEBUG ===")
    
    # Initialize discovery and test generator
    discovery = ServiceDiscovery()
    test_generator = TestGenerator("http://llm-runner:11434/api")
    
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
    
    print(f"   - REST Services: {len(rest_services)}")
    print(f"   - Kafka Topics: {len(kafka_topics)}")
    print(f"   - Database Schemas: {len(db_schemas)}")
    
    # Generate tests
    print("\n2. Generating tests...")
    test_cases = await test_generator.generate_tests(discovery_results)
    
    print(f"   - Total test cases generated: {len(test_cases)}")
    
    # Analyze test cases
    rest_tests = [t for t in test_cases if t.get('type') == 'rest_api']
    kafka_tests = [t for t in test_cases if t.get('type') == 'kafka']
    db_tests = [t for t in test_cases if t.get('type') == 'database']
    
    print(f"   - REST API tests: {len(rest_tests)}")
    print(f"   - Kafka tests: {len(kafka_tests)}")
    print(f"   - Database tests: {len(db_tests)}")
    
    # Show some sample test cases
    print("\n3. Sample test cases:")
    for i, test_case in enumerate(test_cases[:5]):
        print(f"   {i+1}. {test_case.get('name', 'Unknown')} ({test_case.get('type', 'unknown')})")
    
    if kafka_tests:
        print("\n4. Kafka test cases:")
        for i, test_case in enumerate(kafka_tests[:3]):
            print(f"   {i+1}. {test_case.get('name', 'Unknown')}")
            print(f"      Topic: {test_case.get('topic', 'Unknown')}")
            print(f"      Category: {test_case.get('category', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(test_generation())
