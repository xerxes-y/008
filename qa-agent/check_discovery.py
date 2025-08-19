#!/usr/bin/env python3

import asyncio
import psycopg2
from discovery import ServiceDiscovery

async def main():
    sd = ServiceDiscovery()
    
    print("=== SERVICE DISCOVERY CHECK ===")
    
    # Check REST services
    print("\n1. REST Services:")
    try:
        rest_services = await sd.discover_rest_services()
        print(f"   Found {len(rest_services)} REST services:")
        for service in rest_services:
            print(f"   - {service.get('service_name', 'Unknown')}: {service.get('service_url', 'Unknown')}")
            if service.get('endpoints'):
                print(f"     Endpoints: {len(service['endpoints'])}")
                for endpoint in service['endpoints'][:3]:  # Show first 3 endpoints
                    print(f"       - {endpoint.get('path', 'Unknown')} ({endpoint.get('method', 'Unknown')})")
    except Exception as e:
        print(f"   Error discovering REST services: {e}")
    
    # Check Kafka topics
    print("\n2. Kafka Topics:")
    try:
        kafka_topics = await sd.discover_kafka_topics('kafka:29092')
        print(f"   Found {len(kafka_topics)} Kafka topics:")
        for topic in kafka_topics:
            print(f"   - {topic}")
    except Exception as e:
        print(f"   Error discovering Kafka topics: {e}")
    
    # Check database schemas
    print("\n3. Database Schemas:")
    try:
        db_conn = psycopg2.connect("postgresql://qa_user:qa_password@postgres:5432/qa_testing")
        db_schemas = await sd.discover_database_schemas(db_conn)
        print(f"   Found {len(db_schemas)} database schemas:")
        for schema in db_schemas:
            print(f"   - {schema}")
        db_conn.close()
    except Exception as e:
        print(f"   Error discovering database schemas: {e}")

if __name__ == "__main__":
    asyncio.run(main())
