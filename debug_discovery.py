#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the qa-agent directory to the path
sys.path.append('qa-agent')

from discovery import ServiceDiscovery

async def test_discovery():
    discovery = ServiceDiscovery()
    results = await discovery.discover_all()
    
    print("=== DISCOVERY RESULTS ===")
    print(f"REST Services: {len(results.get('rest_services', []))}")
    for service in results.get('rest_services', []):
        print(f"  {service['service_name']}: {len(service.get('endpoints', []))} endpoints")
        for endpoint in service.get('endpoints', []):
            print(f"    {endpoint.get('method', 'GET')} {endpoint.get('path', '')}")
    
    print(f"\nKafka Topics: {len(results.get('kafka_topics', []))}")
    for topic in results.get('kafka_topics', []):
        print(f"  {topic['name']}")
    
    print(f"\nDatabase Tables: {len(results.get('database_schemas', []))}")
    for table in results.get('database_schemas', []):
        print(f"  {table.get('schema', '')}.{table.get('table', '')}")

if __name__ == "__main__":
    asyncio.run(test_discovery())
