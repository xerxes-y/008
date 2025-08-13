"""
Test Generator Component
Uses LLM to generate test cases based on discovered services
"""

import asyncio
import json
import logging
import random
import string
from typing import Dict, List, Any, Optional
import aiohttp

logger = logging.getLogger(__name__)

class TestGenerator:
    def __init__(self, llm_api_url: str):
        self.llm_api_url = llm_api_url
        self.model_name = "llama2:7b"  # Default model
        
        # Test case templates
        self.test_templates = {
            'rest_api': {
                'positive': [
                    "Test {endpoint} with valid {method} request",
                    "Test {endpoint} with valid authentication",
                    "Test {endpoint} with valid request body"
                ],
                'negative': [
                    "Test {endpoint} with invalid authentication",
                    "Test {endpoint} with malformed request body",
                    "Test {endpoint} with missing required fields",
                    "Test {endpoint} with invalid data types"
                ],
                'edge': [
                    "Test {endpoint} with empty request body",
                    "Test {endpoint} with very large payload",
                    "Test {endpoint} with special characters in data"
                ]
            },
            'kafka': {
                'positive': [
                    "Test Kafka topic {topic} with valid message",
                    "Test Kafka topic {topic} with different message formats"
                ],
                'negative': [
                    "Test Kafka topic {topic} with malformed message",
                    "Test Kafka topic {topic} with invalid schema"
                ]
            },
            'database': {
                'positive': [
                    "Test database table {table} CRUD operations",
                    "Test database table {table} with valid constraints"
                ],
                'negative': [
                    "Test database table {table} with invalid data",
                    "Test database table {table} constraint violations"
                ]
            }
        }

    async def generate_tests(self, discovery_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive test cases using LLM"""
        logger.info("Generating test cases using LLM...")
        
        all_test_cases = []
        
        # Generate REST API tests (limit to 2 tests per endpoint)
        if 'rest_services' in discovery_results:
            rest_tests = await self._generate_rest_tests(discovery_results['rest_services'])
            # Limit REST tests to prevent overwhelming
            rest_tests = rest_tests[:50]  # Limit to 50 REST tests
            all_test_cases.extend(rest_tests)
        
        # Generate Kafka tests
        if 'kafka_topics' in discovery_results:
            kafka_tests = await self._generate_kafka_tests(discovery_results['kafka_topics'])
            all_test_cases.extend(kafka_tests)
        
        # Generate database tests (limit to 1 test per table)
        if 'database_schemas' in discovery_results:
            db_tests = await self._generate_database_tests(discovery_results['database_schemas'])
            # Limit database tests
            db_tests = db_tests[:10]  # Limit to 10 database tests
            all_test_cases.extend(db_tests)
        
        # Generate integration tests (limit to 5)
        integration_tests = await self._generate_integration_tests(discovery_results)
        integration_tests = integration_tests[:5]  # Limit to 5 integration tests
        all_test_cases.extend(integration_tests)
        
        logger.info(f"Generated {len(all_test_cases)} test cases (limited for performance)")
        return all_test_cases

    async def _generate_rest_tests(self, rest_services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate REST API test cases"""
        test_cases = []
        
        for service in rest_services:
            service_name = service['service_name']
            service_url = service['service_url']
            
            for endpoint in service.get('endpoints', []):
                # Generate positive test cases
                positive_tests = await self._generate_rest_positive_tests(
                    service_name, service_url, endpoint
                )
                test_cases.extend(positive_tests)
                
                # Generate negative test cases
                negative_tests = await self._generate_rest_negative_tests(
                    service_name, service_url, endpoint
                )
                test_cases.extend(negative_tests)
                
                # Generate edge case tests
                edge_tests = await self._generate_rest_edge_tests(
                    service_name, service_url, endpoint
                )
                test_cases.extend(edge_tests)
        
        return test_cases

    async def _generate_rest_positive_tests(self, service_name: str, service_url: str, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate positive REST API test cases"""
        test_cases = []
        
        # Use template-based generation by default since LLM is slow
        logger.info(f"Using template-based generation for {service_name} positive tests")
        test_cases.extend(self._generate_template_rest_tests(service_name, service_url, endpoint, 'positive'))
        
        return test_cases

    async def _generate_rest_negative_tests(self, service_name: str, service_url: str, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate negative REST API test cases"""
        test_cases = []
        
        # Use template-based generation by default since LLM is slow
        logger.info(f"Using template-based generation for {service_name} negative tests")
        test_cases.extend(self._generate_template_rest_tests(service_name, service_url, endpoint, 'negative'))
        
        return test_cases

    async def _generate_rest_edge_tests(self, service_name: str, service_url: str, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge case REST API test cases"""
        test_cases = []
        
        # Use template-based generation by default since LLM is slow
        logger.info(f"Using template-based generation for {service_name} edge tests")
        test_cases.extend(self._generate_template_rest_tests(service_name, service_url, endpoint, 'edge'))
        
        return test_cases

    def _generate_template_rest_tests(self, service_name: str, service_url: str, endpoint: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
        """Generate template-based REST tests as fallback"""
        test_cases = []
        templates = self.test_templates['rest_api'].get(category, [])
        
        for i, template in enumerate(templates):
            test_case = {
                'id': f"{service_name}_{endpoint.get('path', '').replace('/', '_')}_{category}_{i+1}",
                'name': template.format(
                    endpoint=endpoint.get('path', ''),
                    method=endpoint.get('method', 'GET')
                ),
                'type': 'rest_api',
                'category': category,
                'service': service_name,
                'endpoint': endpoint.get('path', ''),
                'method': endpoint.get('method', 'GET'),
                'url': f"{service_url}{endpoint.get('path', '')}",
                'request_data': self._generate_sample_request_data(endpoint),
                'expected_response': self._generate_expected_response(endpoint),
                'generated_by': 'template'
            }
            test_cases.append(test_case)
        
        return test_cases

    async def _generate_kafka_tests(self, kafka_topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate Kafka test cases"""
        test_cases = []
        
        for topic in kafka_topics:
            topic_name = topic['name']
            
            # Generate positive Kafka tests
            positive_tests = await self._generate_kafka_positive_tests(topic_name, topic.get('schema', {}))
            test_cases.extend(positive_tests)
            
            # Generate negative Kafka tests
            negative_tests = await self._generate_kafka_negative_tests(topic_name, topic.get('schema', {}))
            test_cases.extend(negative_tests)
        
        return test_cases

    async def _generate_kafka_positive_tests(self, topic_name: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate positive Kafka test cases"""
        test_cases = []
        
        # Use template-based generation by default since LLM is slow
        logger.info(f"Using template-based generation for Kafka topic {topic_name} positive tests")
        test_cases.extend(self._generate_template_kafka_tests(topic_name, 'positive'))
        
        return test_cases

    async def _generate_kafka_negative_tests(self, topic_name: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate negative Kafka test cases"""
        test_cases = []
        
        # Use template-based generation by default since LLM is slow
        logger.info(f"Using template-based generation for Kafka topic {topic_name} negative tests")
        test_cases.extend(self._generate_template_kafka_tests(topic_name, 'negative'))
        
        return test_cases

    def _generate_template_kafka_tests(self, topic_name: str, category: str) -> List[Dict[str, Any]]:
        """Generate template-based Kafka tests as fallback"""
        test_cases = []
        templates = self.test_templates['kafka'].get(category, [])
        
        for i, template in enumerate(templates):
            test_case = {
                'id': f"kafka_{topic_name}_{category}_{i+1}",
                'name': template.format(topic=topic_name),
                'type': 'kafka',
                'category': category,
                'topic': topic_name,
                'message_data': self._generate_sample_kafka_message(),
                'expected_processing': {'status': 'success'},
                'generated_by': 'template'
            }
            test_cases.append(test_case)
        
        return test_cases

    async def _generate_database_tests(self, database_schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate database test cases"""
        test_cases = []
        
        for schema_name, schema_info in database_schemas.items():
            for table_name, table_info in schema_info.get('tables', {}).items():
                # Generate positive database tests
                positive_tests = await self._generate_database_positive_tests(schema_name, table_name, table_info)
                test_cases.extend(positive_tests)
                
                # Generate negative database tests
                negative_tests = await self._generate_database_negative_tests(schema_name, table_name, table_info)
                test_cases.extend(negative_tests)
        
        return test_cases

    async def _generate_database_positive_tests(self, schema_name: str, table_name: str, table_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate positive database test cases"""
        test_cases = []
        
        # Use template-based generation by default since LLM is slow
        logger.info(f"Using template-based generation for database table {table_name} positive tests")
        test_cases.extend(self._generate_template_database_tests(schema_name, table_name, 'positive'))
        
        return test_cases

    async def _generate_database_negative_tests(self, schema_name: str, table_name: str, table_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate negative database test cases"""
        test_cases = []
        
        # Use template-based generation by default since LLM is slow
        logger.info(f"Using template-based generation for database table {table_name} negative tests")
        test_cases.extend(self._generate_template_database_tests(schema_name, table_name, 'negative'))
        
        return test_cases

    def _generate_template_database_tests(self, schema_name: str, table_name: str, category: str) -> List[Dict[str, Any]]:
        """Generate template-based database tests as fallback"""
        test_cases = []
        templates = self.test_templates['database'].get(category, [])
        
        for i, template in enumerate(templates):
            test_case = {
                'id': f"db_{schema_name}_{table_name}_{category}_{i+1}",
                'name': template.format(table=table_name),
                'type': 'database',
                'category': category,
                'schema': schema_name,
                'table': table_name,
                'operation': 'SELECT' if category == 'positive' else 'INSERT',
                'test_data': self._generate_sample_database_data(),
                'expected_result': {'status': 'success'} if category == 'positive' else {'status': 'error'},
                'generated_by': 'template'
            }
            test_cases.append(test_case)
        
        return test_cases

    async def _generate_integration_tests(self, discovery_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate integration test cases"""
        test_cases = []
        
        prompt = f"""
        Generate integration test cases for the following microservices:
        REST Services: {json.dumps(discovery_results.get('rest_services', []), indent=2)}
        Kafka Topics: {json.dumps(discovery_results.get('kafka_topics', []), indent=2)}
        Database Schemas: {json.dumps(discovery_results.get('database_schemas', {}), indent=2)}
        
        Generate 3 integration test cases that test:
        1. End-to-end workflows
        2. Service interactions
        3. Data flow between components
        
        Return as JSON array with test cases.
        """
        
        try:
            response = await self._query_llm(prompt)
            generated_tests = json.loads(response)
            
            for i, test in enumerate(generated_tests):
                test_case = {
                    'id': f"integration_test_{i+1}",
                    'name': test.get('name', f"Integration test {i+1}"),
                    'type': 'integration',
                    'category': 'workflow',
                    'workflow_steps': test.get('workflow_steps', []),
                    'services_involved': test.get('services_involved', []),
                    'expected_outcome': test.get('expected_outcome', {}),
                    'data_flow': test.get('data_flow', []),
                    'generated_by': 'llm'
                }
                test_cases.append(test_case)
                
        except Exception as e:
            logger.error(f"Failed to generate integration tests: {e}")
            # Fallback to basic integration tests
            test_cases.extend(self._generate_basic_integration_tests(discovery_results))
        
        return test_cases

    def _generate_basic_integration_tests(self, discovery_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic integration tests as fallback"""
        test_cases = []
        
        # Basic user creation workflow
        test_case = {
            'id': 'integration_user_workflow',
            'name': 'User Creation and Order Workflow',
            'type': 'integration',
            'category': 'workflow',
            'workflow_steps': [
                'Create user via user-service',
                'Create order via order-service',
                'Verify notification sent via notification-service',
                'Verify data consistency in database'
            ],
            'services_involved': ['user-service', 'order-service', 'notification-service'],
            'expected_outcome': {'status': 'success', 'user_created': True, 'order_created': True},
            'generated_by': 'template'
        }
        test_cases.append(test_case)
        
        return test_cases

    async def _query_llm(self, prompt: str) -> str:
        """Query the LLM with a prompt"""
        try:
            timeout = aiohttp.ClientTimeout(total=120)  # 2 minute timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                }
                
                async with session.post(f"{self.llm_api_url}/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '')
                    else:
                        raise Exception(f"LLM API returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to query LLM: {e}")
            raise

    def _generate_sample_request_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample request data for an endpoint"""
        method = endpoint.get('method', 'GET')
        
        if method == 'GET':
            return {'query_params': {'limit': 10, 'offset': 0}}
        elif method in ['POST', 'PUT', 'PATCH']:
            return {
                'body': {
                    'id': self._generate_random_id(),
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'created_at': '2024-01-01T00:00:00Z'
                }
            }
        else:
            return {}

    def _generate_expected_response(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate expected response for an endpoint"""
        method = endpoint.get('method', 'GET')
        
        if method == 'GET':
            return {
                'status_code': 200,
                'body': {
                    'data': [],
                    'total': 0,
                    'page': 1
                }
            }
        elif method in ['POST', 'PUT', 'PATCH']:
            return {
                'status_code': 201 if method == 'POST' else 200,
                'body': {
                    'id': self._generate_random_id(),
                    'status': 'success'
                }
            }
        else:
            return {'status_code': 204}

    def _generate_sample_kafka_message(self) -> Dict[str, Any]:
        """Generate sample Kafka message"""
        return {
            'id': self._generate_random_id(),
            'event_type': 'test_event',
            'timestamp': '2024-01-01T00:00:00Z',
            'data': {
                'message': 'Test message',
                'value': 123
            }
        }

    def _generate_sample_database_data(self) -> Dict[str, Any]:
        """Generate sample database data"""
        return {
            'id': self._generate_random_id(),
            'name': 'Test Record',
            'created_at': '2024-01-01T00:00:00Z',
            'status': 'active'
        }

    def _generate_random_id(self) -> str:
        """Generate a random ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
