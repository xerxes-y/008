#!/usr/bin/env python3
"""
Quick Kafka LLM Testing Demo
A simple script to demonstrate Kafka testing with LLM
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the qa-agent directory to the path
sys.path.append('qa-agent')

from discovery import ServiceDiscovery
from test_generator import TestGenerator
from test_executor import TestExecutor

async def quick_kafka_test():
    """Quick demonstration of Kafka LLM testing"""
    print("🚀 Quick Kafka LLM Testing Demo")
    print("=" * 40)
    
    try:
        # Initialize components
        discovery = ServiceDiscovery()
        test_generator = TestGenerator("http://llm-runner:11434/api")
        test_executor = TestExecutor()
        
        # Step 1: Discover Kafka topics
        print("1. 🔍 Discovering Kafka topics...")
        kafka_topics = await discovery.discover_kafka_topics('kafka:29092')
        
        if not kafka_topics:
            print("❌ No Kafka topics found. Make sure Kafka is running.")
            return
        
        print(f"✅ Found {len(kafka_topics)} topics:")
        for topic in kafka_topics:
            print(f"   📨 {topic['name']}")
        
        # Step 2: Generate test cases
        print("\n2. 🧠 Generating test cases...")
        kafka_tests = await test_generator._generate_kafka_tests(kafka_topics)
        
        print(f"✅ Generated {len(kafka_tests)} test cases")
        
        # Step 3: Execute a few tests
        print("\n3. 🚀 Executing tests...")
        results = []
        
        for i, test_case in enumerate(kafka_tests[:3]):  # Test first 3
            print(f"   Testing: {test_case['name']}")
            
            try:
                result = await test_executor.execute_test(test_case)
                results.append(result)
                
                if result.get('status') == 'PASSED':
                    print(f"   ✅ PASSED")
                else:
                    print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   💥 ERROR: {e}")
                results.append({
                    'test_case': test_case,
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        # Step 4: Show results
        print("\n4. 📊 Results Summary")
        print("=" * 40)
        
        passed = len([r for r in results if r.get('status') == 'PASSED'])
        failed = len([r for r in results if r.get('status') == 'FAILED'])
        
        print(f"Tests executed: {len(results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
        
        # Show topics tested
        topics_tested = set()
        for result in results:
            if 'test_case' in result:
                topics_tested.add(result['test_case'].get('topic', 'unknown'))
        
        print(f"📨 Topics tested: {', '.join(topics_tested)}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_kafka_test())
