"""
Service Discovery Component
Discovers REST endpoints, Kafka topics, and database schemas
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Any, Optional
import aiohttp
import psycopg2
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, ConfigResource, ConfigResourceType

logger = logging.getLogger(__name__)

class ServiceDiscovery:
    def __init__(self):
        self.known_services = {
            'user-service': 'http://user-service:8000',
            'order-service': 'http://order-service:8000',
            'notification-service': 'http://notification-service:8000'
        }
        
        # Common REST API patterns
        self.api_patterns = [
            '/api/v1',
            '/api',
            '/rest',
            '/swagger',
            '/openapi',
            '/health',
            '/metrics'
        ]

    async def discover_rest_services(self) -> List[Dict[str, Any]]:
        """Discover REST API endpoints from all microservices"""
        logger.info("Discovering REST services...")
        
        discovered_services = []
        
        for service_name, service_url in self.known_services.items():
            try:
                service_info = await self._discover_service_endpoints(service_name, service_url)
                if service_info:
                    discovered_services.append(service_info)
                    
            except Exception as e:
                logger.error(f"Failed to discover {service_name}: {e}")
        
        return discovered_services

    async def _discover_service_endpoints(self, service_name: str, service_url: str) -> Optional[Dict[str, Any]]:
        """Discover endpoints for a specific service"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Try to get OpenAPI/Swagger documentation
                openapi_spec = await self._get_openapi_spec(session, service_url)
                
                if openapi_spec:
                    return self._parse_openapi_spec(service_name, service_url, openapi_spec)
                
                # Fallback: try common endpoints
                endpoints = await self._discover_common_endpoints(session, service_url)
                
                return {
                    'service_name': service_name,
                    'service_url': service_url,
                    'endpoints': endpoints,
                    'discovery_method': 'common_patterns'
                }
                
        except Exception as e:
            logger.error(f"Error discovering {service_name}: {e}")
            return None

    async def _get_openapi_spec(self, session: aiohttp.ClientSession, service_url: str) -> Optional[Dict[str, Any]]:
        """Try to get OpenAPI specification from service"""
        openapi_paths = [
            '/openapi.json',
            '/swagger.json',
            '/api-docs',
            '/swagger/v1/swagger.json'
        ]
        
        for path in openapi_paths:
            try:
                url = f"{service_url}{path}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception:
                continue
        
        return None

    def _parse_openapi_spec(self, service_name: str, service_url: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAPI specification to extract endpoints"""
        endpoints = []
        
        if 'paths' in spec:
            for path, methods in spec['paths'].items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        endpoint = {
                            'path': path,
                            'method': method.upper(),
                            'summary': details.get('summary', ''),
                            'description': details.get('description', ''),
                            'parameters': details.get('parameters', []),
                            'request_body': details.get('requestBody', {}),
                            'responses': details.get('responses', {})
                        }
                        endpoints.append(endpoint)
        
        return {
            'service_name': service_name,
            'service_url': service_url,
            'endpoints': endpoints,
            'discovery_method': 'openapi_spec',
            'openapi_version': spec.get('openapi', ''),
            'info': spec.get('info', {})
        }

    async def _discover_common_endpoints(self, session: aiohttp.ClientSession, service_url: str) -> List[Dict[str, Any]]:
        """Discover endpoints using common patterns"""
        endpoints = []
        
        # Test common API patterns
        for pattern in self.api_patterns:
            try:
                url = f"{service_url}{pattern}"
                async with session.get(url) as response:
                    if response.status in [200, 401, 403]:  # Valid responses
                        endpoints.append({
                            'path': pattern,
                            'method': 'GET',
                            'status_code': response.status,
                            'discovered': True
                        })
            except Exception:
                continue
        
        # Try health check endpoint
        try:
            async with session.get(f"{service_url}/health") as response:
                if response.status == 200:
                    endpoints.append({
                        'path': '/health',
                        'method': 'GET',
                        'status_code': 200,
                        'discovered': True
                    })
        except Exception:
            pass
        
        return endpoints

    async def discover_kafka_topics(self, kafka_brokers: str) -> List[Dict[str, Any]]:
        """Discover Kafka topics and their configurations"""
        logger.info("Discovering Kafka topics...")
        
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=kafka_brokers,
                client_id='discovery-admin'
            )
            
            # Get all topics
            metadata = admin_client.list_topics()
            topics_info = []
            
            for topic in metadata:
                if not topic.startswith('__'):  # Skip internal topics
                    try:
                        # Get topic configuration
                        config_resource = ConfigResource(ConfigResourceType.TOPIC, topic)
                        configs = admin_client.describe_configs([config_resource])
                        
                        topic_info = {
                            'name': topic,
                            'config': configs[config_resource].config,
                            'discovered': True
                        }
                        
                        # Try to get message schema (if available)
                        schema_info = await self._discover_topic_schema(kafka_brokers, topic)
                        if schema_info:
                            topic_info['schema'] = schema_info
                        
                        topics_info.append(topic_info)
                        
                    except Exception as e:
                        logger.warning(f"Could not get config for topic {topic}: {e}")
                        topics_info.append({
                            'name': topic,
                            'discovered': True
                        })
            
            admin_client.close()
            return topics_info
            
        except Exception as e:
            logger.error(f"Failed to discover Kafka topics: {e}")
            return []

    async def _discover_topic_schema(self, kafka_brokers: str, topic: str) -> Optional[Dict[str, Any]]:
        """Try to discover message schema for a Kafka topic"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=kafka_brokers,
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                group_id='schema-discovery'
            )
            
            # Get a few messages to analyze schema
            messages = []
            for message in consumer:
                try:
                    msg_data = json.loads(message.value.decode('utf-8'))
                    messages.append(msg_data)
                    
                    if len(messages) >= 3:  # Analyze up to 3 messages
                        break
                        
                except Exception:
                    continue
            
            consumer.close()
            
            if messages:
                return self._infer_schema_from_messages(messages)
            
        except Exception as e:
            logger.debug(f"Could not discover schema for topic {topic}: {e}")
        
        return None

    def _infer_schema_from_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Infer JSON schema from message samples"""
        if not messages:
            return {}
        
        # Simple schema inference
        schema = {
            'type': 'object',
            'properties': {},
            'required': []
        }
        
        # Analyze all messages to find common fields
        all_fields = set()
        field_types = {}
        
        for msg in messages:
            if isinstance(msg, dict):
                all_fields.update(msg.keys())
                
                for field, value in msg.items():
                    if field not in field_types:
                        field_types[field] = set()
                    field_types[field].add(type(value).__name__)
        
        # Build schema properties
        for field in all_fields:
            types = field_types.get(field, set())
            
            if 'string' in types:
                schema['properties'][field] = {'type': 'string'}
            elif 'integer' in types:
                schema['properties'][field] = {'type': 'integer'}
            elif 'number' in types:
                schema['properties'][field] = {'type': 'number'}
            elif 'boolean' in types:
                schema['properties'][field] = {'type': 'boolean'}
            elif 'object' in types:
                schema['properties'][field] = {'type': 'object'}
            elif 'array' in types:
                schema['properties'][field] = {'type': 'array'}
            else:
                schema['properties'][field] = {'type': 'string'}
        
        return schema

    async def discover_database_schemas(self, db_connection) -> Dict[str, Any]:
        """Discover database schemas and table structures"""
        logger.info("Discovering database schemas...")
        
        try:
            cursor = db_connection.cursor()
            
            # Get all schemas
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            """)
            
            schemas = [row[0] for row in cursor.fetchall()]
            
            schema_info = {}
            
            for schema in schemas:
                # Get tables in schema
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_type = 'BASE TABLE'
                """, (schema,))
                
                tables = [row[0] for row in cursor.fetchall()]
                schema_info[schema] = {
                    'tables': {},
                    'discovered': True
                }
                
                for table in tables:
                    # Get table columns
                    cursor.execute("""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            character_maximum_length
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = %s
                        ORDER BY ordinal_position
                    """, (schema, table))
                    
                    columns = []
                    for row in cursor.fetchall():
                        columns.append({
                            'name': row[0],
                            'type': row[1],
                            'nullable': row[2] == 'YES',
                            'default': row[3],
                            'max_length': row[4]
                        })
                    
                    # Get primary keys
                    cursor.execute("""
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.constraint_type = 'PRIMARY KEY' 
                            AND tc.table_schema = %s 
                            AND tc.table_name = %s
                    """, (schema, table))
                    
                    primary_keys = [row[0] for row in cursor.fetchall()]
                    
                    # Get foreign keys
                    cursor.execute("""
                        SELECT 
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage ccu 
                            ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY' 
                            AND tc.table_schema = %s 
                            AND tc.table_name = %s
                    """, (schema, table))
                    
                    foreign_keys = []
                    for row in cursor.fetchall():
                        foreign_keys.append({
                            'column': row[0],
                            'foreign_table': row[1],
                            'foreign_column': row[2]
                        })
                    
                    schema_info[schema]['tables'][table] = {
                        'columns': columns,
                        'primary_keys': primary_keys,
                        'foreign_keys': foreign_keys,
                        'discovered': True
                    }
            
            cursor.close()
            return schema_info
            
        except Exception as e:
            logger.error(f"Failed to discover database schemas: {e}")
            return {}

    async def discover_service_health(self) -> Dict[str, Any]:
        """Discover health status of all services"""
        logger.info("Checking service health...")
        
        health_status = {}
        
        for service_name, service_url in self.known_services.items():
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    async with session.get(f"{service_url}/health") as response:
                        health_status[service_name] = {
                            'status': 'healthy' if response.status == 200 else 'unhealthy',
                            'status_code': response.status,
                            'response_time': response.headers.get('X-Response-Time', 'unknown')
                        }
            except Exception as e:
                health_status[service_name] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
        
        return health_status
