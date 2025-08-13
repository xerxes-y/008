#!/usr/bin/env python3
"""
LLM QA Agent for Microservices Testing
Automatically discovers and tests microservices using LLM
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import aiohttp
import psycopg2
import redis
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from discovery import ServiceDiscovery
from test_generator import TestGenerator
from test_executor import TestExecutor
from result_reporter import ResultReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMQAAgent:
    def __init__(self):
        self.llm_api_url = os.getenv('LLM_API_URL', 'http://llm-runner:11434/api')
        self.kafka_brokers = os.getenv('KAFKA_BROKERS', 'kafka:29092')
        self.postgres_url = os.getenv('POSTGRES_URL', 'postgresql://qa_user:qa_password@postgres:5432/qa_testing')
        self.redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
        
        # Initialize components
        self.discovery = ServiceDiscovery()
        self.test_generator = TestGenerator(self.llm_api_url)
        self.test_executor = TestExecutor()
        self.result_reporter = ResultReporter()
        
        # Initialize connections
        self.kafka_producer = None
        self.kafka_consumer = None
        self.redis_client = None
        self.db_connection = None
        
        # Test results storage
        self.test_results_dir = Path("/app/test-results")
        self.test_results_dir.mkdir(exist_ok=True)

    async def initialize(self):
        """Initialize all connections and components"""
        logger.info("Initializing LLM QA Agent...")
        
        # Initialize Kafka
        await self._init_kafka()
        
        # Initialize Redis
        await self._init_redis()
        
        # Initialize Database
        await self._init_database()
        
        # Initialize LLM
        await self._init_llm()
        
        logger.info("LLM QA Agent initialized successfully")

    async def _init_kafka(self):
        """Initialize Kafka connections"""
        try:
            # Create topics if they don't exist
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.kafka_brokers,
                client_id='qa-agent-admin'
            )
            
            topics = [
                NewTopic(name='qa-discovery', num_partitions=1, replication_factor=1),
                NewTopic(name='qa-test-results', num_partitions=1, replication_factor=1),
                NewTopic(name='qa-reports', num_partitions=1, replication_factor=1)
            ]
            
            try:
                admin_client.create_topics(topics, validate_only=False)
            except TopicAlreadyExistsError:
                logger.info("Kafka topics already exist, continuing...")
            except Exception as e:
                logger.warning(f"Could not create topics: {e}")
            admin_client.close()
            
            # Initialize producer and consumer
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.kafka_brokers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            
            self.kafka_consumer = KafkaConsumer(
                'qa-discovery',
                bootstrap_servers=self.kafka_brokers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='qa-agent-group'
            )
            
            logger.info("Kafka connections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka: {e}")
            raise

    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("Redis connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def _init_database(self):
        """Initialize database connection"""
        try:
            self.db_connection = psycopg2.connect(self.postgres_url)
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def _init_llm(self):
        """Initialize LLM connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.llm_api_url}/tags") as response:
                    if response.status == 200:
                        logger.info("LLM connection verified")
                    else:
                        raise Exception(f"LLM API returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

    async def discover_services(self) -> Dict[str, Any]:
        """Discover all microservices and their endpoints"""
        logger.info("Starting service discovery...")
        
        # Discover REST endpoints
        rest_services = await self.discovery.discover_rest_services()
        
        # Discover Kafka topics
        kafka_topics = await self.discovery.discover_kafka_topics(self.kafka_brokers)
        
        # Discover database schemas
        db_schemas = await self.discovery.discover_database_schemas(self.db_connection)
        
        discovery_results = {
            'rest_services': rest_services,
            'kafka_topics': kafka_topics,
            'database_schemas': db_schemas,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache discovery results
        self.redis_client.setex(
            'discovery_results',
            3600,  # 1 hour cache
            json.dumps(discovery_results)
        )
        
        logger.info(f"Discovered {len(rest_services)} REST services, {len(kafka_topics)} Kafka topics")
        return discovery_results

    async def generate_tests(self, discovery_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases using LLM"""
        logger.info("Generating test cases...")
        
        test_cases = await self.test_generator.generate_tests(discovery_results)
        
        logger.info(f"Generated {len(test_cases)} test cases")
        return test_cases

    async def execute_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute all test cases"""
        logger.info("Executing test cases...")
        
        results = []
        for test_case in test_cases:
            try:
                result = await self.test_executor.execute_test(test_case)
                results.append(result)
                
                # Publish result to Kafka
                self.kafka_producer.send('qa-test-results', result)
                
            except Exception as e:
                logger.error(f"Test execution failed for {test_case.get('name', 'unknown')}: {e}")
                results.append({
                    'test_case': test_case,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.info(f"Executed {len(results)} test cases")
        return results

    async def generate_report(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        logger.info("Generating test report...")
        
        report = await self.result_reporter.generate_report(test_results)
        
        # Save report to file
        report_file = self.test_results_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Publish report to Kafka
        self.kafka_producer.send('qa-reports', report)
        
        logger.info(f"Test report generated and saved to {report_file}")
        return report

    async def run_qa_cycle(self):
        """Run complete QA cycle"""
        logger.info("Starting QA cycle...")
        
        try:
            # Step 1: Discover services
            discovery_results = await self.discover_services()
            
            # Step 2: Generate tests
            test_cases = await self.generate_tests(discovery_results)
            
            # Step 3: Execute tests
            test_results = await self.execute_tests(test_cases)
            
            # Step 4: Generate report
            report = await self.generate_report(test_results)
            
            logger.info("QA cycle completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"QA cycle failed: {e}")
            raise

    async def run_continuous_monitoring(self):
        """Run continuous monitoring mode"""
        logger.info("Starting continuous monitoring...")
        
        while True:
            try:
                await self.run_qa_cycle()
                
                # Wait for next cycle (configurable interval)
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Monitoring cycle failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        
        if self.kafka_producer:
            self.kafka_producer.close()
        
        if self.kafka_consumer:
            self.kafka_consumer.close()
        
        if self.redis_client:
            self.redis_client.close()
        
        if self.db_connection:
            self.db_connection.close()

async def main():
    """Main entry point"""
    agent = LLMQAAgent()
    
    try:
        await agent.initialize()
        
        # Run initial QA cycle
        await agent.run_qa_cycle()
        
        # Start continuous monitoring
        await agent.run_continuous_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
