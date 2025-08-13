"""
Test Executor Component
Executes test cases against microservices and validates results
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
import psycopg2
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

logger = logging.getLogger(__name__)

class TestExecutor:
    def __init__(self):
        self.session = None
        self.kafka_producer = None
        self.kafka_consumer = None
        self.db_connection = None
        
        # Test execution timeouts
        self.timeouts = {
            'rest_api': 30,
            'kafka': 60,
            'database': 30,
            'integration': 120
        }

    async def execute_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test case"""
        logger.info(f"Executing test: {test_case.get('name', 'Unknown')}")
        
        start_time = time.time()
        test_type = test_case.get('type', 'unknown')
        
        try:
            if test_type == 'rest_api':
                result = await self._execute_rest_test(test_case)
            elif test_type == 'kafka':
                result = await self._execute_kafka_test(test_case)
            elif test_type == 'database':
                result = await self._execute_database_test(test_case)
            elif test_type == 'integration':
                result = await self._execute_integration_test(test_case)
            else:
                result = {
                    'status': 'SKIPPED',
                    'error': f'Unknown test type: {test_type}'
                }
            
            execution_time = time.time() - start_time
            
            result.update({
                'test_case': test_case,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Test execution failed: {e}")
            
            return {
                'test_case': test_case,
                'status': 'FAILED',
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

    async def _execute_rest_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute REST API test"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = test_case.get('url', '')
        method = test_case.get('method', 'GET')
        request_data = test_case.get('request_data', {})
        expected_response = test_case.get('expected_response', {})
        
        try:
            # Prepare request
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Add authentication if specified
            if 'auth' in request_data:
                headers['Authorization'] = request_data['auth']
            
            # Prepare request parameters
            params = request_data.get('query_params', {})
            json_data = request_data.get('body', None)
            
            # Execute request
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeouts['rest_api'])
            ) as response:
                
                response_body = await response.text()
                
                # Try to parse JSON response
                try:
                    response_json = await response.json()
                except:
                    response_json = None
                
                # Validate response
                validation_result = self._validate_rest_response(
                    response, response_json, expected_response
                )
                
                return {
                    'status': 'PASSED' if validation_result['valid'] else 'FAILED',
                    'request': {
                        'method': method,
                        'url': url,
                        'headers': headers,
                        'params': params,
                        'body': json_data
                    },
                    'response': {
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'body': response_json if response_json else response_body
                    },
                    'validation': validation_result,
                    'test_type': 'rest_api'
                }
                
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'test_type': 'rest_api'
            }

    def _validate_rest_response(self, response, response_json: Optional[Dict], expected_response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate REST API response"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check status code
        expected_status = expected_response.get('status_code', 200)
        if response.status != expected_status:
            validation_result['valid'] = False
            validation_result['errors'].append(
                f"Expected status {expected_status}, got {response.status}"
            )
        
        # Check response body structure if expected
        if 'body' in expected_response and response_json:
            expected_body = expected_response['body']
            if isinstance(expected_body, dict):
                for key, expected_value in expected_body.items():
                    if key not in response_json:
                        validation_result['warnings'].append(f"Missing expected field: {key}")
                    elif response_json[key] != expected_value:
                        validation_result['warnings'].append(
                            f"Field {key} value mismatch: expected {expected_value}, got {response_json[key]}"
                        )
        
        return validation_result

    async def _execute_kafka_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Kafka test"""
        topic = test_case.get('topic', '')
        message_data = test_case.get('message_data', {})
        expected_processing = test_case.get('expected_processing', {})
        
        if not self.kafka_producer:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers='kafka:29092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
        
        try:
            # Send message to Kafka topic
            future = self.kafka_producer.send(topic, message_data)
            record_metadata = future.get(timeout=10)
            
            # Wait for message processing
            await asyncio.sleep(2)
            
            # Validate message was sent successfully
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            if record_metadata.topic != topic:
                validation_result['valid'] = False
                validation_result['errors'].append(
                    f"Message sent to wrong topic: {record_metadata.topic}"
                )
            
            return {
                'status': 'PASSED' if validation_result['valid'] else 'FAILED',
                'message_sent': {
                    'topic': record_metadata.topic,
                    'partition': record_metadata.partition,
                    'offset': record_metadata.offset,
                    'data': message_data
                },
                'validation': validation_result,
                'test_type': 'kafka'
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'test_type': 'kafka'
            }

    async def _execute_database_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database test"""
        schema = test_case.get('schema', '')
        table = test_case.get('table', '')
        operation = test_case.get('operation', 'SELECT')
        test_data = test_case.get('test_data', {})
        expected_result = test_case.get('expected_result', {})
        
        if not self.db_connection:
            self.db_connection = psycopg2.connect(
                "postgresql://qa_user:qa_password@postgres:5432/qa_testing"
            )
        
        try:
            cursor = self.db_connection.cursor()
            
            if operation == 'SELECT':
                # Execute SELECT query
                query = f"SELECT * FROM {schema}.{table} LIMIT 1"
                cursor.execute(query)
                result = cursor.fetchall()
                
                validation_result = {
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
                
                if not result and expected_result.get('expect_data', True):
                    validation_result['warnings'].append("No data returned from query")
                
            elif operation == 'INSERT':
                # Execute INSERT query
                columns = list(test_data.keys())
                values = list(test_data.values())
                placeholders = ', '.join(['%s'] * len(values))
                
                query = f"INSERT INTO {schema}.{table} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(query, values)
                self.db_connection.commit()
                
                validation_result = {
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
                
            elif operation == 'UPDATE':
                # Execute UPDATE query
                set_clause = ', '.join([f"{k} = %s" for k in test_data.keys()])
                query = f"UPDATE {schema}.{table} SET {set_clause} WHERE id = %s"
                values = list(test_data.values()) + [test_data.get('id', 1)]
                
                cursor.execute(query, values)
                self.db_connection.commit()
                
                validation_result = {
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
                
            elif operation == 'DELETE':
                # Execute DELETE query
                query = f"DELETE FROM {schema}.{table} WHERE id = %s"
                cursor.execute(query, [test_data.get('id', 1)])
                self.db_connection.commit()
                
                validation_result = {
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
            
            cursor.close()
            
            return {
                'status': 'PASSED' if validation_result['valid'] else 'FAILED',
                'operation': operation,
                'query_executed': True,
                'validation': validation_result,
                'test_type': 'database'
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'test_type': 'database'
            }

    async def _execute_integration_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration test"""
        workflow_steps = test_case.get('workflow_steps', [])
        services_involved = test_case.get('services_involved', [])
        expected_outcome = test_case.get('expected_outcome', {})
        
        try:
            results = []
            overall_status = 'PASSED'
            
            for step in workflow_steps:
                step_result = await self._execute_workflow_step(step)
                results.append(step_result)
                
                if step_result.get('status') == 'FAILED':
                    overall_status = 'FAILED'
            
            # Validate overall outcome
            validation_result = self._validate_integration_outcome(results, expected_outcome)
            
            return {
                'status': overall_status,
                'workflow_steps': results,
                'services_involved': services_involved,
                'validation': validation_result,
                'test_type': 'integration'
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'test_type': 'integration'
            }

    async def _execute_workflow_step(self, step: str) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            if 'user-service' in step.lower():
                # Execute user service step
                return await self._execute_user_service_step(step)
            elif 'order-service' in step.lower():
                # Execute order service step
                return await self._execute_order_service_step(step)
            elif 'notification-service' in step.lower():
                # Execute notification service step
                return await self._execute_notification_service_step(step)
            elif 'database' in step.lower():
                # Execute database step
                return await self._execute_database_step(step)
            else:
                return {
                    'step': step,
                    'status': 'SKIPPED',
                    'reason': 'Unknown step type'
                }
                
        except Exception as e:
            return {
                'step': step,
                'status': 'FAILED',
                'error': str(e)
            }

    async def _execute_user_service_step(self, step: str) -> Dict[str, Any]:
        """Execute user service workflow step"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            if 'create' in step.lower():
                # Create user
                user_data = {
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'password': 'testpass123'
                }
                
                async with self.session.post(
                    'http://user-service:8000/api/users',
                    json=user_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 201:
                        user = await response.json()
                        return {
                            'step': step,
                            'status': 'PASSED',
                            'user_id': user.get('id'),
                            'response': user
                        }
                    else:
                        return {
                            'step': step,
                            'status': 'FAILED',
                            'error': f"Failed to create user: {response.status}"
                        }
            
            elif 'get' in step.lower():
                # Get user
                async with self.session.get(
                    'http://user-service:8000/api/users/1',
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        user = await response.json()
                        return {
                            'step': step,
                            'status': 'PASSED',
                            'user': user
                        }
                    else:
                        return {
                            'step': step,
                            'status': 'FAILED',
                            'error': f"Failed to get user: {response.status}"
                        }
            
            return {
                'step': step,
                'status': 'SKIPPED',
                'reason': 'Unknown user service operation'
            }
            
        except Exception as e:
            return {
                'step': step,
                'status': 'FAILED',
                'error': str(e)
            }

    async def _execute_order_service_step(self, step: str) -> Dict[str, Any]:
        """Execute order service workflow step"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            if 'create' in step.lower():
                # Create order
                order_data = {
                    'user_id': 1,
                    'items': [
                        {'product_id': 1, 'quantity': 2, 'price': 29.99}
                    ],
                    'total_amount': 59.98
                }
                
                async with self.session.post(
                    'http://order-service:8000/api/orders',
                    json=order_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 201:
                        order = await response.json()
                        return {
                            'step': step,
                            'status': 'PASSED',
                            'order_id': order.get('id'),
                            'response': order
                        }
                    else:
                        return {
                            'step': step,
                            'status': 'FAILED',
                            'error': f"Failed to create order: {response.status}"
                        }
            
            return {
                'step': step,
                'status': 'SKIPPED',
                'reason': 'Unknown order service operation'
            }
            
        except Exception as e:
            return {
                'step': step,
                'status': 'FAILED',
                'error': str(e)
            }

    async def _execute_notification_service_step(self, step: str) -> Dict[str, Any]:
        """Execute notification service workflow step"""
        try:
            if 'verify' in step.lower():
                # Verify notification was sent (check Kafka topic)
                if not self.kafka_consumer:
                    self.kafka_consumer = KafkaConsumer(
                        'notifications',
                        bootstrap_servers='kafka:29092',
                        auto_offset_reset='latest',
                        enable_auto_commit=False,
                        group_id='test-consumer'
                    )
                
                # Wait for notification message
                for message in self.kafka_consumer:
                    try:
                        notification = json.loads(message.value.decode('utf-8'))
                        return {
                            'step': step,
                            'status': 'PASSED',
                            'notification': notification
                        }
                    except:
                        continue
                
                return {
                    'step': step,
                    'status': 'FAILED',
                    'error': 'No notification message received'
                }
            
            return {
                'step': step,
                'status': 'SKIPPED',
                'reason': 'Unknown notification service operation'
            }
            
        except Exception as e:
            return {
                'step': step,
                'status': 'FAILED',
                'error': str(e)
            }

    async def _execute_database_step(self, step: str) -> Dict[str, Any]:
        """Execute database workflow step"""
        try:
            if 'verify' in step.lower() and 'consistency' in step.lower():
                # Verify data consistency across services
                if not self.db_connection:
                    self.db_connection = psycopg2.connect(
                        "postgresql://qa_user:qa_password@postgres:5432/qa_testing"
                    )
                
                cursor = self.db_connection.cursor()
                
                # Check if user exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE id = 1")
                user_count = cursor.fetchone()[0]
                
                # Check if order exists
                cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = 1")
                order_count = cursor.fetchone()[0]
                
                cursor.close()
                
                if user_count > 0 and order_count > 0:
                    return {
                        'step': step,
                        'status': 'PASSED',
                        'user_count': user_count,
                        'order_count': order_count
                    }
                else:
                    return {
                        'step': step,
                        'status': 'FAILED',
                        'error': f"Data inconsistency: users={user_count}, orders={order_count}"
                    }
            
            return {
                'step': step,
                'status': 'SKIPPED',
                'reason': 'Unknown database operation'
            }
            
        except Exception as e:
            return {
                'step': step,
                'status': 'FAILED',
                'error': str(e)
            }

    def _validate_integration_outcome(self, results: List[Dict[str, Any]], expected_outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration test outcome"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if all steps passed
        failed_steps = [r for r in results if r.get('status') == 'FAILED']
        if failed_steps:
            validation_result['valid'] = False
            validation_result['errors'].append(f"{len(failed_steps)} workflow steps failed")
        
        # Check expected outcomes
        for key, expected_value in expected_outcome.items():
            if key == 'status' and expected_value == 'success':
                if validation_result['valid']:
                    continue
                else:
                    validation_result['errors'].append("Expected success but test failed")
            
            # Add more specific validations as needed
        
        return validation_result

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        
        if self.kafka_producer:
            self.kafka_producer.close()
        
        if self.kafka_consumer:
            self.kafka_consumer.close()
        
        if self.db_connection:
            self.db_connection.close()
