# Kafka LLM Testing Guide

This guide explains how the 008-Agent project uses Large Language Models (LLMs) to automatically test Kafka topics and message flows.

## 🎯 Overview

The project combines Kafka testing with LLM intelligence to:
- **Discover** Kafka topics automatically
- **Generate** intelligent test cases using LLM
- **Execute** tests against Kafka topics
- **Validate** message formats and flows
- **Report** comprehensive test results

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM QA Agent  │    │   Kafka Topics  │    │   Test Results  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Discovery   │ │───▶│ │ Topic 1     │ │    │ │ Test Report │ │
│ │ Engine      │ │    │ │ Topic 2     │ │    │ │ Coverage    │ │
│ └─────────────┘ │    │ │ Topic 3     │ │    │ │ Performance │ │
│                 │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │                 │    │                 │
│ │ LLM Test    │ │───▶│ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Generator   │ │    │ │ Message     │ │    │ │ Validation  │ │
│ └─────────────┘ │    │ │ Schema      │ │    │ │ Results     │ │
│                 │    │ │ Flow        │ │    │ │ Metrics     │ │
│ ┌─────────────┐ │    │ └─────────────┘ │    │ └─────────────┘ │
│ │ Test        │ │───▶│                 │    │                 │
│ │ Executor    │ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ └─────────────┘ │    │ │ Consumer    │ │    │ │ LLM         │ │
│                 │    │ │ Producer    │ │    │ │ Insights    │ │
│ ┌─────────────┐ │    │ └─────────────┘ │    │ └─────────────┘ │
│ │ Result      │ │    │                 │    │                 │
│ │ Reporter    │ │    │                 │    │                 │
│ └─────────────┘ │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 How It Works

### 1. **Kafka Topic Discovery**

The system automatically discovers Kafka topics using the Kafka Admin Client:

```python
async def discover_kafka_topics(self, kafka_brokers: str) -> List[Dict[str, Any]]:
    """Discover Kafka topics and their configurations"""
    admin_client = KafkaAdminClient(
        bootstrap_servers=kafka_brokers,
        client_id='discovery-admin'
    )
    
    # Get all topics
    metadata = admin_client.list_topics()
    topics_info = []
    
    for topic in metadata:
        if not topic.startswith('__'):  # Skip internal topics
            # Get topic configuration and schema
            topic_info = {
                'name': topic,
                'config': configs,
                'schema': schema_info
            }
            topics_info.append(topic_info)
    
    return topics_info
```

### 2. **Schema Inference**

The system analyzes existing messages to infer JSON schemas:

```python
async def _discover_topic_schema(self, kafka_brokers: str, topic: str):
    """Try to discover message schema for a Kafka topic"""
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
        msg_data = json.loads(message.value.decode('utf-8'))
        messages.append(msg_data)
        
        if len(messages) >= 3:  # Analyze up to 3 messages
            break
    
    return self._infer_schema_from_messages(messages)
```

### 3. **LLM Test Generation**

The LLM generates intelligent test cases based on discovered topics:

```python
async def _generate_kafka_tests(self, kafka_topics: List[Dict[str, Any]]):
    """Generate Kafka test cases using LLM"""
    test_cases = []
    
    for topic in kafka_topics:
        topic_name = topic['name']
        
        # Generate positive tests
        positive_tests = await self._generate_kafka_positive_tests(
            topic_name, topic.get('schema', {})
        )
        test_cases.extend(positive_tests)
        
        # Generate negative tests
        negative_tests = await self._generate_kafka_negative_tests(
            topic_name, topic.get('schema', {})
        )
        test_cases.extend(negative_tests)
    
    return test_cases
```

### 4. **Test Execution**

Tests are executed by sending messages to Kafka topics:

```python
async def _execute_kafka_test(self, test_case: Dict[str, Any]):
    """Execute Kafka test"""
    topic = test_case.get('topic', '')
    message_data = test_case.get('message_data', {})
    
    # Send message to Kafka topic
    future = self.kafka_producer.send(topic, message_data)
    record_metadata = future.get(timeout=10)
    
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
        'validation': validation_result
    }
```

## 🚀 Getting Started

### Prerequisites

1. **Start the infrastructure:**
```bash
docker-compose up -d
```

2. **Wait for services to be ready:**
```bash
# Check service status
docker-compose ps

# Monitor logs
docker-compose logs -f qa-agent
```

### Running Kafka LLM Tests

#### Option 1: Use the Simple QA Runner

```bash
# Run from the project root
cd qa-agent
python run_simple_qa.py
```

This will:
- Discover Kafka topics
- Generate test cases
- Execute tests
- Generate a report

#### Option 2: Use the Demo Script

```bash
# Run the comprehensive demo
python kafka_llm_testing_example.py
```

This demonstrates:
- Topic discovery
- LLM test generation
- Test execution
- Schema inference
- Enhanced LLM testing

#### Option 3: Use the Main QA Agent

```bash
# Start the full QA agent
docker-compose up qa-agent
```

This runs continuous monitoring with full LLM integration.

## 📊 Test Types Generated

### 1. **Positive Tests**
- Valid message format testing
- Successful message delivery
- Correct topic routing
- Message persistence validation

### 2. **Negative Tests**
- Invalid message format
- Malformed JSON
- Missing required fields
- Schema validation failures

### 3. **Edge Cases**
- Large message payloads
- Special characters in messages
- Empty messages
- High-frequency message sending

### 4. **Integration Tests**
- End-to-end message flows
- Producer-consumer interactions
- Cross-topic dependencies
- Error handling scenarios

## 🧠 LLM Integration

### LLM Prompts Used

The system uses various LLM prompts for test generation:

```python
# Basic Kafka test generation
prompt = f"""
Generate Kafka test cases for topic: {topic_name}
Schema: {schema}

Generate:
1. Positive test cases with valid messages
2. Negative test cases with invalid messages
3. Edge cases for message handling

Return as JSON array of test cases.
"""
```

### LLM Configuration

```python
# LLM settings in test_generator.py
self.model_name = "llama2:7b"  # Default model

# LLM query parameters
payload = {
    "model": self.model_name,
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.7,  # Creativity level
        "top_p": 0.9        # Response diversity
    }
}
```

## 📈 Test Results

### Sample Test Report

```json
{
  "report_metadata": {
    "generated_at": "2024-01-01T12:00:00Z",
    "total_tests": 20,
    "report_version": "1.0"
  },
  "summary": {
    "total_tests": 20,
    "passed": 18,
    "failed": 2,
    "success_rate": 90.0
  },
  "statistics": {
    "test_types": {
      "kafka": {
        "total": 20,
        "passed": 18,
        "failed": 2
      }
    }
  },
  "coverage": {
    "kafka_topics_tested": [
      "order_events",
      "notifications",
      "qa-test-results"
    ]
  }
}
```

### Performance Metrics

- **Message Delivery Time**: Average time to send messages
- **Topic Coverage**: Percentage of topics tested
- **Schema Validation**: Success rate of schema compliance
- **Error Patterns**: Common failure modes identified

## 🔍 Advanced Features

### 1. **Custom LLM Prompts**

You can create custom prompts for specific testing scenarios:

```python
custom_prompt = f"""
Generate advanced Kafka test cases for e-commerce system:
Topics: {kafka_topics}

Focus on:
- Order processing workflows
- Payment confirmation flows
- Inventory updates
- Customer notifications

Include edge cases for:
- High load scenarios
- Network failures
- Data corruption
- Race conditions
"""
```

### 2. **Schema Evolution Testing**

Test how your system handles schema changes:

```python
# Test backward compatibility
old_schema = {"user_id": "integer", "amount": "number"}
new_schema = {"user_id": "integer", "amount": "number", "currency": "string"}

# Generate tests for both schemas
tests = await generate_schema_compatibility_tests(old_schema, new_schema)
```

### 3. **Load Testing**

Generate high-volume test scenarios:

```python
# Generate load test cases
load_tests = await generate_kafka_load_tests(
    topics=kafka_topics,
    message_rate=1000,  # messages per second
    duration=60         # seconds
)
```

## 🛠️ Configuration

### Environment Variables

```bash
# Kafka Configuration
KAFKA_BROKERS=kafka:29092

# LLM Configuration
LLM_API_URL=http://llm-runner:11434/api

# Test Configuration
LOG_LEVEL=INFO
TEST_TIMEOUT=30
MAX_TESTS_PER_TOPIC=10
```

### Custom Test Templates

You can customize test templates in `test_generator.py`:

```python
self.test_templates = {
    'kafka': {
        'positive': [
            "Test {topic} with valid message format",
            "Test {topic} with standard payload",
            "Test {topic} message delivery confirmation"
        ],
        'negative': [
            "Test {topic} with malformed JSON",
            "Test {topic} with missing required fields",
            "Test {topic} with invalid data types"
        ]
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **LLM Not Responding**
   ```bash
   # Check LLM service
   docker-compose logs llm-runner
   
   # Restart LLM
   docker-compose restart llm-runner
   ```

2. **Kafka Connection Issues**
   ```bash
   # Check Kafka status
   docker-compose logs kafka
   
   # Verify topics exist
   docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
   ```

3. **Test Generation Failing**
   ```bash
   # Check test generator logs
   docker-compose logs qa-agent
   
   # Run debug script
   python qa-agent/test_generation_debug.py
   ```

### Debug Tools

- `test_generation_debug.py` - Debug test generation
- `test_execution_debug.py` - Debug test execution
- `debug_discovery.py` - Debug service discovery

## 📚 Best Practices

1. **Start Small**: Begin with a few topics and gradually expand
2. **Monitor Performance**: Watch for slow tests and optimize
3. **Customize Prompts**: Tailor LLM prompts for your specific use cases
4. **Validate Results**: Always review generated test cases
5. **Iterate**: Continuously improve based on test results

## 🔮 Future Enhancements

- **Real-time Schema Validation**: Validate messages against schemas in real-time
- **Advanced Load Testing**: Generate complex load scenarios
- **Integration with Schema Registry**: Use Apache Kafka Schema Registry
- **Custom Test Frameworks**: Support for custom test frameworks
- **Machine Learning**: Use ML to predict test failures

This guide covers the essential aspects of Kafka LLM testing in the 008-Agent project. The system provides a powerful foundation for automated Kafka testing with intelligent test generation capabilities.
