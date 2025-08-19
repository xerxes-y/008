# Spring Boot Service

A Spring Boot microservice for product management that integrates with the 008-Agent QA testing system.

## 🏗️ Architecture

This service provides:
- **REST API** for product management
- **JPA/Hibernate** for database persistence
- **Redis** for caching
- **Kafka** integration for event-driven communication
- **OpenAPI/Swagger** documentation
- **Actuator** for monitoring and health checks

## 🚀 Features

### REST API Endpoints

- `POST /api/products` - Create a new product
- `GET /api/products/{id}` - Get product by ID
- `GET /api/products` - Get all products (with pagination)
- `GET /api/products/list` - Get all products (without pagination)
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `GET /api/products/search?name={name}` - Search products by name
- `GET /api/products/price-range?minPrice={min}&maxPrice={max}` - Get products by price range
- `GET /api/products/in-stock?minStock={min}` - Get products in stock
- `GET /api/products/low-stock?maxStock={max}` - Get products with low stock
- `PATCH /api/products/{id}/stock?quantity={qty}` - Update product stock
- `GET /api/products/{id}/exists` - Check if product exists
- `GET /api/products/check-name?name={name}` - Check if product exists by name

### Kafka Integration

The service publishes events to Kafka topics:
- `product_events` - Product lifecycle events (created, deleted)
- `product_updates` - Product update events
- `low_stock_alerts` - Low stock notifications

### Database Schema

The service uses the existing `products` table in the PostgreSQL database.

## 🛠️ Technology Stack

- **Spring Boot 3.2.0** - Main framework
- **Spring Data JPA** - Database access
- **Spring Data Redis** - Caching
- **Spring Kafka** - Message broker integration
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **OpenAPI 3** - API documentation
- **Spring Actuator** - Monitoring and health checks

## 📋 Prerequisites

- Java 17 or higher
- Maven 3.6+
- Docker and Docker Compose
- PostgreSQL database
- Redis cache
- Kafka message broker

## 🚀 Getting Started

### Option 1: Using Docker Compose (Recommended)

The service is already configured in the main `docker-compose.yml`:

```bash
# Start all services including Spring Boot service
docker-compose up -d

# Check service status
docker-compose ps spring-boot-service

# View logs
docker-compose logs -f spring-boot-service
```

### Option 2: Local Development

1. **Clone and navigate to the service directory:**
```bash
cd microservices/spring-boot-service
```

2. **Build the project:**
```bash
./mvnw clean compile
```

3. **Run the application:**
```bash
./mvnw spring-boot:run
```

The service will start on port 8004.

## 📊 API Documentation

Once the service is running, you can access:

- **Swagger UI**: http://localhost:8004/swagger-ui.html
- **OpenAPI JSON**: http://localhost:8004/api-docs
- **Health Check**: http://localhost:8004/actuator/health

## 🔧 Configuration

### Environment Variables

The service can be configured using environment variables:

```bash
# Database
SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/qa_testing
SPRING_DATASOURCE_USERNAME=qa_user
SPRING_DATASOURCE_PASSWORD=qa_password

# Kafka
SPRING_KAFKA_BOOTSTRAP_SERVERS=kafka:29092
SPRING_KAFKA_CONSUMER_GROUP_ID=spring-boot-service-group

# Redis
SPRING_REDIS_HOST=redis
SPRING_REDIS_PORT=6379

# Server
SERVER_PORT=8004
```

### Application Properties

Key configuration in `application.yml`:

```yaml
server:
  port: 8004

spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/qa_testing
    username: qa_user
    password: qa_password
  
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false
  
  kafka:
    bootstrap-servers: kafka:29092
    consumer:
      group-id: spring-boot-service-group
  
  data:
    redis:
      host: redis
      port: 6379
```

## 🧪 Testing with QA Agent

The Spring Boot service is automatically discovered and tested by the QA Agent:

1. **Service Discovery**: The QA Agent discovers the REST endpoints
2. **Test Generation**: LLM generates test cases for the API
3. **Test Execution**: Tests are executed against the service
4. **Kafka Testing**: Kafka topics and message flows are tested
5. **Database Testing**: Database operations are validated

### Test Coverage

The QA Agent will test:
- ✅ All REST API endpoints
- ✅ Request/response validation
- ✅ Error handling
- ✅ Kafka message publishing
- ✅ Database CRUD operations
- ✅ Redis caching
- ✅ Health check endpoints

## 📈 Monitoring

### Health Checks

- **Application Health**: `/actuator/health`
- **Database Health**: `/actuator/health/db`
- **Redis Health**: `/actuator/health/redis`
- **Kafka Health**: `/actuator/health/kafka`

### Metrics

- **Prometheus Metrics**: `/actuator/prometheus`
- **Application Metrics**: `/actuator/metrics`

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Check database logs
   docker-compose logs postgres
   ```

2. **Kafka Connection Failed**
   ```bash
   # Check if Kafka is running
   docker-compose ps kafka
   
   # Check Kafka logs
   docker-compose logs kafka
   ```

3. **Redis Connection Failed**
   ```bash
   # Check if Redis is running
   docker-compose ps redis
   
   # Check Redis logs
   docker-compose logs redis
   ```

4. **Service Not Starting**
   ```bash
   # Check service logs
   docker-compose logs spring-boot-service
   
   # Check if port 8004 is available
   netstat -tulpn | grep 8004
   ```

### Debug Mode

To run in debug mode:

```bash
# Set debug logging
export LOGGING_LEVEL_COM_EXAMPLE_SPRINGBOOTSERVICE=DEBUG

# Run with debug
./mvnw spring-boot:run -Dspring-boot.run.jvmArguments="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005"
```

## 🔄 Development Workflow

1. **Make changes** to the code
2. **Build** the project: `./mvnw clean compile`
3. **Test** locally: `./mvnw test`
4. **Run** the service: `./mvnw spring-boot:run`
5. **Verify** with QA Agent tests
6. **Commit** and push changes

## 📚 API Examples

### Create a Product

```bash
curl -X POST http://localhost:8004/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "A test product",
    "price": 29.99,
    "stockQuantity": 100
  }'
```

### Get All Products

```bash
curl http://localhost:8004/api/products
```

### Search Products

```bash
curl "http://localhost:8004/api/products/search?name=test"
```

### Update Stock

```bash
curl -X PATCH "http://localhost:8004/api/products/1/stock?quantity=50"
```

## 🤝 Integration

This service integrates seamlessly with:
- **User Service** - User management
- **Order Service** - Order processing
- **Notification Service** - Event notifications
- **QA Agent** - Automated testing
- **Kafka** - Event streaming
- **PostgreSQL** - Data persistence
- **Redis** - Caching

The service follows the same patterns and conventions as the other microservices in the 008-Agent project.
