#!/usr/bin/env python3
"""
Notification Service - REST API for notifications with Kafka consumer
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from typing import List, Optional
from kafka import KafkaConsumer
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Notification Service",
    description="REST API for notification management",
    version="1.0.0"
)

# Redis connection
def get_redis_connection():
    """Get Redis connection"""
    try:
        r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))
        return r
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

# Kafka consumer
def get_kafka_consumer():
    """Get Kafka consumer"""
    try:
        consumer = KafkaConsumer(
            'order_events',
            bootstrap_servers=os.getenv('KAFKA_BROKERS', 'kafka:29092'),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='notification-service'
        )
        return consumer
    except Exception as e:
        logger.error(f"Kafka consumer creation failed: {e}")
        return None

# Pydantic models
class NotificationCreate(BaseModel):
    user_id: int
    message: str
    type: str = 'info'

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    type: str
    status: str
    created_at: str

# Global variables for storing notifications
notifications = []
notification_counter = 1

# Kafka consumer thread
def kafka_consumer_thread():
    """Background thread to consume Kafka messages"""
    global notifications, notification_counter
    
    consumer = get_kafka_consumer()
    if not consumer:
        logger.error("Failed to create Kafka consumer")
        return
    
    logger.info("Starting Kafka consumer thread")
    
    try:
        for message in consumer:
            try:
                event = message.value
                logger.info(f"Received event: {event}")
                
                # Process order events
                if event.get('event_type') == 'order_created':
                    notification = {
                        'id': notification_counter,
                        'user_id': event.get('user_id'),
                        'message': f"Order {event.get('order_id')} has been created successfully",
                        'type': 'success',
                        'status': 'unread',
                        'created_at': datetime.now().isoformat()
                    }
                    notifications.append(notification)
                    notification_counter += 1
                    
                    # Store in Redis
                    redis_conn = get_redis_connection()
                    if redis_conn:
                        redis_conn.setex(
                            f"notification:{notification['id']}",
                            86400,  # 24 hours
                            json.dumps(notification)
                        )
                
                elif event.get('event_type') == 'order_updated':
                    notification = {
                        'id': notification_counter,
                        'user_id': event.get('user_id', 0),
                        'message': f"Order {event.get('order_id')} status updated to {event.get('status')}",
                        'type': 'info',
                        'status': 'unread',
                        'created_at': datetime.now().isoformat()
                    }
                    notifications.append(notification)
                    notification_counter += 1
                    
                    # Store in Redis
                    redis_conn = get_redis_connection()
                    if redis_conn:
                        redis_conn.setex(
                            f"notification:{notification['id']}",
                            86400,  # 24 hours
                            json.dumps(notification)
                        )
                
                elif event.get('event_type') == 'order_deleted':
                    notification = {
                        'id': notification_counter,
                        'user_id': event.get('user_id', 0),
                        'message': f"Order {event.get('order_id')} has been deleted",
                        'type': 'warning',
                        'status': 'unread',
                        'created_at': datetime.now().isoformat()
                    }
                    notifications.append(notification)
                    notification_counter += 1
                    
                    # Store in Redis
                    redis_conn = get_redis_connection()
                    if redis_conn:
                        redis_conn.setex(
                            f"notification:{notification['id']}",
                            86400,  # 24 hours
                            json.dumps(notification)
                        )
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except Exception as e:
        logger.error(f"Kafka consumer error: {e}")
    finally:
        consumer.close()

# Start Kafka consumer thread
kafka_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
kafka_thread.start()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.ping()
        
        # Check Kafka connection
        consumer = get_kafka_consumer()
        if consumer:
            consumer.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "redis": "connected" if redis_conn else "disconnected",
                "kafka": "connected" if consumer else "disconnected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# OpenAPI specification
@app.get("/openapi.json")
async def get_openapi():
    """Get OpenAPI specification"""
    return app.openapi()

# Notification endpoints
@app.post("/api/notifications", response_model=NotificationResponse, status_code=201)
async def create_notification(notification: NotificationCreate):
    """Create a new notification"""
    global notification_counter
    
    try:
        new_notification = {
            'id': notification_counter,
            'user_id': notification.user_id,
            'message': notification.message,
            'type': notification.type,
            'status': 'unread',
            'created_at': datetime.now().isoformat()
        }
        
        notifications.append(new_notification)
        notification_counter += 1
        
        # Store in Redis
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.setex(
                f"notification:{new_notification['id']}",
                86400,  # 24 hours
                json.dumps(new_notification)
            )
        
        return NotificationResponse(**new_notification)
        
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create notification")

@app.get("/api/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: int):
    """Get notification by ID"""
    try:
        # Try to get from Redis first
        redis_conn = get_redis_connection()
        if redis_conn:
            cached_notification = redis_conn.get(f"notification:{notification_id}")
            if cached_notification:
                return NotificationResponse(**json.loads(cached_notification))
        
        # Get from memory
        for notification in notifications:
            if notification['id'] == notification_id:
                return NotificationResponse(**notification)
        
        raise HTTPException(status_code=404, detail="Notification not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification")

@app.get("/api/notifications")
async def list_notifications(user_id: Optional[int] = None, limit: int = 10, offset: int = 0):
    """List notifications with pagination"""
    try:
        filtered_notifications = notifications
        
        if user_id:
            filtered_notifications = [n for n in notifications if n['user_id'] == user_id]
        
        # Apply pagination
        paginated_notifications = filtered_notifications[offset:offset + limit]
        
        return {
            "data": [NotificationResponse(**n) for n in paginated_notifications],
            "total": len(filtered_notifications),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to list notifications")

@app.put("/api/notifications/{notification_id}")
async def mark_notification_read(notification_id: int):
    """Mark notification as read"""
    try:
        # Update in memory
        for notification in notifications:
            if notification['id'] == notification_id:
                notification['status'] = 'read'
                
                # Update in Redis
                redis_conn = get_redis_connection()
                if redis_conn:
                    redis_conn.setex(
                        f"notification:{notification_id}",
                        86400,  # 24 hours
                        json.dumps(notification)
                    )
                
                return NotificationResponse(**notification)
        
        raise HTTPException(status_code=404, detail="Notification not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")

@app.delete("/api/notifications/{notification_id}")
async def delete_notification(notification_id: int):
    """Delete notification"""
    try:
        # Remove from memory
        for i, notification in enumerate(notifications):
            if notification['id'] == notification_id:
                del notifications[i]
                
                # Remove from Redis
                redis_conn = get_redis_connection()
                if redis_conn:
                    redis_conn.delete(f"notification:{notification_id}")
                
                return {"message": "Notification deleted successfully"}
        
        raise HTTPException(status_code=404, detail="Notification not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")

# Kafka topic endpoint for testing
@app.post("/api/kafka/test")
async def send_test_notification():
    """Send a test notification via Kafka"""
    try:
        test_notification = {
            'id': notification_counter,
            'user_id': 1,
            'message': 'This is a test notification',
            'type': 'info',
            'status': 'unread',
            'created_at': datetime.now().isoformat()
        }
        
        notifications.append(test_notification)
        
        # Store in Redis
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.setex(
                f"notification:{test_notification['id']}",
                86400,  # 24 hours
                json.dumps(test_notification)
            )
        
        return {"message": "Test notification created", "notification": test_notification}
        
    except Exception as e:
        logger.error(f"Failed to create test notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create test notification")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
