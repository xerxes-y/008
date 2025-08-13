# LLM-Powered QA System for Microservices Testing

## Project Overview

This project creates an intelligent QA system that uses LLM to automatically test microservices in a Docker environment. The LLM discovers REST endpoints, Kafka message structures, and generates comprehensive test cases with results.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM QA Agent  │    │   Microservices │    │   Infrastructure│
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Discovery   │ │───▶│ │ REST APIs   │ │    │ │   Kafka     │ │
│ │ Engine      │ │    │ │             │ │    │ │   Broker    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Test        │ │───▶│ │ Kafka       │ │    │ │   Database  │ │
│ │ Generator   │ │    │ │ Consumers   │ │    │ │   (PostgreSQL)│
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Result      │ │    │ │ Microservice│ │    │ │   Redis     │ │
│ │ Reporter    │ │    │ │ Containers  │ │    │ │   (Cache)   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

1. **LLM QA Agent**: 
   - Discovers REST endpoints and Kafka topics
   - Generates test cases based on API schemas
   - Executes tests and validates responses
   - Generates detailed test reports

2. **Microservices Infrastructure**:
   - REST API endpoints for testing
   - Kafka consumers/producers
   - Database connections
   - Container orchestration

3. **Supporting Infrastructure**:
   - Kafka broker for message handling
   - PostgreSQL for data persistence
   - Redis for caching
   - Docker Model Runner for LLM

## Workflow

1. **Discovery Phase**:
   - LLM scans Docker containers for REST endpoints
   - Discovers Kafka topics and message schemas
   - Analyzes database schemas and relationships

2. **Test Generation**:
   - LLM generates test cases based on discovered APIs
   - Creates test data and expected responses
   - Plans test execution strategy

3. **Test Execution**:
   - Executes REST API calls with various inputs
   - Sends messages to Kafka topics
   - Validates responses and data consistency

4. **Result Generation**:
   - Creates detailed test reports with input/output
   - Generates coverage analysis
   - Identifies potential issues and recommendations

## Setup Instructions

1. Configure environment variables
2. Start infrastructure with `docker-compose up -d`
3. Load test datasets into database
4. Run LLM QA agent to begin testing

## Configuration

See individual component documentation for detailed setup instructions.
