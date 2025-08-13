#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the qa-agent directory to the path
sys.path.append('.')

from discovery import ServiceDiscovery

async def test_discovery():
    discovery = ServiceDiscovery()
    
    print("=== DISCOVERY RESULTS ===")
    
    # Discover REST services
    rest_services = await discovery.discover_rest_services()
    print(f"REST Services: {len(rest_services)}")
    for service in rest_services:
        print(f"  {service['service_name']}: {len(service.get('endpoints', []))} endpoints")
        for endpoint in service.get('endpoints', []):
            print(f"    {endpoint.get('method', 'GET')} {endpoint.get('path', '')}")
    
    # Discover Kafka topics
    kafka_topics = await discovery.discover_kafka_topics('kafka:29092')
    print(f"\nKafka Topics: {len(kafka_topics)}")
    for topic in kafka_topics:
        print(f"  {topic['name']}")
    
    # Discover database schemas
    import psycopg2
    db_conn = psycopg2.connect("postgresql://qa_user:qa_password@postgres:5432/qa_testing")
    db_schemas = await discovery.discover_database_schemas(db_conn)
    print(f"\nDatabase Schemas: {len(db_schemas)}")
    for schema_name, schema_info in db_schemas.items():
        print(f"  Schema: {schema_name}")
        for table_name, table_info in schema_info.get('tables', {}).items():
            print(f"    Table: {table_name} ({len(table_info.get('columns', []))} columns)")

if __name__ == "__main__":
    asyncio.run(test_discovery())
