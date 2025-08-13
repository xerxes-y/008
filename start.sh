#!/bin/bash

# LLM-Powered QA System Startup Script

echo "🚀 Starting LLM-Powered QA System for Microservices Testing"
echo "=========================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create test-results directory if it doesn't exist
mkdir -p test-results

echo "📁 Created test-results directory"

# Start all services
echo "🔧 Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready (this may take 2-3 minutes)..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Wait a bit more for LLM model to load
echo "🧠 Waiting for LLM model to load..."
sleep 60

# Show service URLs
echo ""
echo "🌐 Service URLs:"
echo "   Kafka UI:        http://localhost:8080"
echo "   User Service:    http://localhost:8001"
echo "   Order Service:   http://localhost:8002"
echo "   Notification:    http://localhost:8003"
echo "   LLM API:         http://localhost:11434"
echo ""

# Show how to monitor logs
echo "📊 To monitor the QA agent:"
echo "   docker-compose logs -f qa-agent"
echo ""
echo "📊 To view all logs:"
echo "   docker-compose logs -f"
echo ""
echo "📁 Test results will be saved to:"
echo "   ./test-results/"
echo ""

# Check if QA agent is running
echo "🔍 Checking QA agent status..."
if docker-compose ps qa-agent | grep -q "Up"; then
    echo "✅ QA agent is running successfully!"
    echo ""
    echo "🎉 System is ready! The QA agent will start discovering and testing microservices."
    echo "   Check the logs to see the testing progress."
else
    echo "⚠️  QA agent may still be starting up. Check logs with:"
    echo "   docker-compose logs qa-agent"
fi

echo ""
echo "🛑 To stop the system:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart:"
echo "   docker-compose restart"
