#!/usr/bin/env python3
"""
Kafka LLM Testing Example
Demonstrates how to test Kafka topics using LLM in the 008-Agent project
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
from result_reporter import ResultReporter

class KafkaLLMTester:
    def __init__(self):
        self.discovery = ServiceDiscovery()
        self.test_generator = TestGenerator("http://llm-runner:11434/api")
        self.test_executor = TestExecutor()
        self.result_reporter = ResultReporter()
        
    async def demonstrate_kafka_discovery(self):
        """Demonstrate Kafka topic discovery"""
        print("🔍 STEP 1: Kafka Topic Discovery")
        print("=" * 50)
        
        # Discover Kafka topics
        kafka_topics = await self.discovery.discover_kafka_topics('kafka:29092')
        
        print(f"Discovered {len(kafka_topics)} Kafka topics:")
        for topic in kafka_topics:
            print(f"  📨 Topic: {topic['name']}")
            if 'schema' in topic:
                print(f"     Schema: {json.dumps(topic['schema'], indent=6)}")
            if 'config' in topic:
                print(f"     Config: {len(topic['config'])} configuration items")
        
        return kafka_topics
    
    async def demonstrate_llm_test_generation(self, kafka_topics):
        """Demonstrate LLM-powered test generation for Kafka"""
        print("\n🧠 STEP 2: LLM Test Generation")
        print("=" * 50)
        
        # Generate Kafka tests using LLM
        kafka_tests = await self.test_generator._generate_kafka_tests(kafka_topics)
        
        print(f"Generated {len(kafka_tests)} Kafka test cases:")
        
        # Categorize tests
        positive_tests = [t for t in kafka_tests if t.get('category') == 'positive']
        negative_tests = [t for t in kafka_tests if t.get('category') == 'negative']
        
        print(f"  ✅ Positive tests: {len(positive_tests)}")
        print(f"  ❌ Negative tests: {len(negative_tests)}")
        
        # Show sample test cases
        print("\nSample test cases:")
        for i, test in enumerate(kafka_tests[:3]):
            print(f"  {i+1}. {test['name']}")
            print(f"     Topic: {test['topic']}")
            print(f"     Category: {test['category']}")
            print(f"     Message: {json.dumps(test['message_data'], indent=8)}")
            print()
        
        return kafka_tests
    
    async def demonstrate_test_execution(self, kafka_tests):
        """Demonstrate Kafka test execution"""
        print("🚀 STEP 3: Kafka Test Execution")
        print("=" * 50)
        
        results = []
        
        for i, test_case in enumerate(kafka_tests[:5]):  # Execute first 5 tests
            print(f"Executing test {i+1}/{min(5, len(kafka_tests))}: {test_case['name']}")
            
            try:
                result = await self.test_executor.execute_test(test_case)
                results.append(result)
                
                status = result.get('status', 'UNKNOWN')
                if status == 'PASSED':
                    print(f"  ✅ PASSED - Message sent to {result['message_sent']['topic']}")
                    print(f"     Partition: {result['message_sent']['partition']}")
                    print(f"     Offset: {result['message_sent']['offset']}")
                else:
                    print(f"  ❌ FAILED - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  💥 ERROR - {e}")
                results.append({
                    'test_case': test_case,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    async def demonstrate_llm_enhanced_testing(self, kafka_topics):
        """Demonstrate LLM-enhanced Kafka testing with custom prompts"""
        print("\n🤖 STEP 4: LLM-Enhanced Kafka Testing")
        print("=" * 50)
        
        # Create custom LLM prompt for Kafka testing
        custom_prompt = f"""
        Generate advanced Kafka test cases for the following topics:
        {json.dumps(kafka_topics, indent=2)}
        
        For each topic, generate:
        1. A test case that validates message format
        2. A test case that tests message ordering
        3. A test case that validates message persistence
        4. A test case that tests consumer behavior
        
        Return the test cases as a JSON array with the following structure:
        {{
            "name": "Test description",
            "topic": "topic_name",
            "message_data": {{...}},
            "expected_behavior": "description",
            "validation_criteria": ["criteria1", "criteria2"]
        }}
        """
        
        try:
            # Query LLM for enhanced test cases
            print("Querying LLM for enhanced test cases...")
            llm_response = await self.test_generator._query_llm(custom_prompt)
            
            print("LLM Response:")
            print(llm_response[:500] + "..." if len(llm_response) > 500 else llm_response)
            
            # Try to parse LLM response as JSON
            try:
                enhanced_tests = json.loads(llm_response)
                print(f"\nGenerated {len(enhanced_tests)} enhanced test cases from LLM")
                
                # Convert to test format
                for i, test in enumerate(enhanced_tests[:3]):
                    test_case = {
                        'id': f"llm_enhanced_{i+1}",
                        'name': test.get('name', f'LLM Enhanced Test {i+1}'),
                        'type': 'kafka',
                        'category': 'llm_enhanced',
                        'topic': test.get('topic', 'test_topic'),
                        'message_data': test.get('message_data', {}),
                        'expected_behavior': test.get('expected_behavior', ''),
                        'validation_criteria': test.get('validation_criteria', []),
                        'generated_by': 'llm_enhanced'
                    }
                    
                    print(f"  {i+1}. {test_case['name']}")
                    print(f"     Topic: {test_case['topic']}")
                    print(f"     Expected: {test_case['expected_behavior']}")
                    
            except json.JSONDecodeError:
                print("LLM response was not valid JSON, using fallback generation")
                
        except Exception as e:
            print(f"LLM query failed: {e}")
    
    async def demonstrate_schema_inference(self, kafka_topics):
        """Demonstrate Kafka message schema inference"""
        print("\n📋 STEP 5: Kafka Schema Inference")
        print("=" * 50)
        
        for topic in kafka_topics:
            topic_name = topic['name']
            print(f"Analyzing schema for topic: {topic_name}")
            
            if 'schema' in topic:
                schema = topic['schema']
                print(f"  Inferred schema:")
                print(f"    Type: {schema.get('type', 'unknown')}")
                print(f"    Properties: {list(schema.get('properties', {}).keys())}")
                
                # Show sample message based on schema
                sample_message = self._generate_message_from_schema(schema)
                print(f"  Sample message: {json.dumps(sample_message, indent=6)}")
            else:
                print(f"  No schema information available")
            
            print()
    
    def _generate_message_from_schema(self, schema):
        """Generate a sample message based on inferred schema"""
        if not schema or 'properties' not in schema:
            return {'message': 'Sample message'}
        
        sample = {}
        for field, field_schema in schema['properties'].items():
            field_type = field_schema.get('type', 'string')
            
            if field_type == 'string':
                sample[field] = f"sample_{field}"
            elif field_type == 'integer':
                sample[field] = 123
            elif field_type == 'number':
                sample[field] = 123.45
            elif field_type == 'boolean':
                sample[field] = True
            elif field_type == 'object':
                sample[field] = {'nested': 'value'}
            elif field_type == 'array':
                sample[field] = ['item1', 'item2']
            else:
                sample[field] = 'default_value'
        
        return sample
    
    async def run_complete_demo(self):
        """Run complete Kafka LLM testing demonstration"""
        print("🎯 Kafka LLM Testing Demonstration")
        print("=" * 60)
        print("This demo shows how the 008-Agent project tests Kafka topics using LLM")
        print()
        
        try:
            # Step 1: Discover Kafka topics
            kafka_topics = await self.demonstrate_kafka_discovery()
            
            if not kafka_topics:
                print("❌ No Kafka topics discovered. Make sure Kafka is running.")
                return
            
            # Step 2: Generate tests with LLM
            kafka_tests = await self.demonstrate_llm_test_generation(kafka_topics)
            
            # Step 3: Execute tests
            test_results = await self.demonstrate_test_execution(kafka_tests)
            
            # Step 4: LLM-enhanced testing
            await self.demonstrate_llm_enhanced_testing(kafka_topics)
            
            # Step 5: Schema inference
            await self.demonstrate_schema_inference(kafka_topics)
            
            # Generate summary report
            print("\n📊 STEP 6: Test Summary")
            print("=" * 50)
            
            passed = len([r for r in test_results if r.get('status') == 'PASSED'])
            failed = len([r for r in test_results if r.get('status') == 'FAILED'])
            
            print(f"Test Results:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            print(f"  📊 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
            
            # Show topics tested
            topics_tested = set()
            for result in test_results:
                if 'test_case' in result:
                    topics_tested.add(result['test_case'].get('topic', 'unknown'))
            
            print(f"  📨 Topics Tested: {', '.join(topics_tested)}")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Main entry point"""
    tester = KafkaLLMTester()
    await tester.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())
