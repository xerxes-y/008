#!/usr/bin/env python3
"""
Order Service - REST API for order management with Kafka integration
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional
import psycopg2
from kafka import KafkaProducer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Order Service",
    description="REST API for order management",
    version="1.0.0"
)

# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://qa_user:qa_password@postgres:5432/qa_testing'))
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Kafka producer
def get_kafka_producer():
    """Get Kafka producer"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=os.getenv('KAFKA_BROKERS', 'kafka:29092'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        return producer
    except Exception as e:
        logger.error(f"Kafka producer creation failed: {e}")
        return None

# Pydantic models
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]
    total_amount: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total_amount: float
    status: str
    created_at: str

class OrderUpdate(BaseModel):
    status: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        conn = get_db_connection()
        conn.close()
        
        # Check Kafka connection
        producer = get_kafka_producer()
        if producer:
            producer.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected",
                "kafka": "connected" if producer else "disconnected"
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

# Order endpoints
@app.post("/api/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate):
    """Create a new order"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert order
        cursor.execute(
            "INSERT INTO orders (user_id, total_amount, status, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
            (order.user_id, order.total_amount, 'pending', datetime.now())
        )
        order_id = cursor.fetchone()[0]
        
        # Insert order items
        for item in order.items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, item.product_id, item.quantity, item.price)
            )
        
        conn.commit()
        
        # Send order created event to Kafka
        producer = get_kafka_producer()
        if producer:
            event = {
                'event_type': 'order_created',
                'order_id': order_id,
                'user_id': order.user_id,
                'total_amount': order.total_amount,
                'timestamp': datetime.now().isoformat()
            }
            producer.send('order_events', event)
            producer.flush()
        
        cursor.close()
        conn.close()
        
        return OrderResponse(
            id=order_id,
            user_id=order.user_id,
            items=order.items,
            total_amount=order.total_amount,
            status='pending',
            created_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    """Get order by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get order
        cursor.execute(
            "SELECT id, user_id, total_amount, status, created_at FROM orders WHERE id = %s",
            (order_id,)
        )
        order_data = cursor.fetchone()
        
        if not order_data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get order items
        cursor.execute(
            "SELECT product_id, quantity, price FROM order_items WHERE order_id = %s",
            (order_id,)
        )
        items_data = cursor.fetchall()
        
        items = [OrderItem(product_id=item[0], quantity=item[1], price=item[2]) for item in items_data]
        
        order = OrderResponse(
            id=order_data[0],
            user_id=order_data[1],
            items=items,
            total_amount=order_data[2],
            status=order_data[3],
            created_at=order_data[4].isoformat()
        )
        
        cursor.close()
        conn.close()
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get order: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order")

@app.get("/api/orders")
async def list_orders(limit: int = 10, offset: int = 0, user_id: Optional[int] = None):
    """List orders with pagination"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute(
                "SELECT id, user_id, total_amount, status, created_at FROM orders WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (user_id, limit, offset)
            )
        else:
            cursor.execute(
                "SELECT id, user_id, total_amount, status, created_at FROM orders ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (limit, offset)
            )
        
        orders_data = cursor.fetchall()
        
        orders = []
        for order_data in orders_data:
            # Get items for each order
            cursor.execute(
                "SELECT product_id, quantity, price FROM order_items WHERE order_id = %s",
                (order_data[0],)
            )
            items_data = cursor.fetchall()
            items = [OrderItem(product_id=item[0], quantity=item[1], price=item[2]) for item in items_data]
            
            orders.append(OrderResponse(
                id=order_data[0],
                user_id=order_data[1],
                items=items,
                total_amount=order_data[2],
                status=order_data[3],
                created_at=order_data[4].isoformat()
            ))
        
        cursor.close()
        conn.close()
        
        return {
            "data": orders,
            "total": len(orders),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to list orders")

@app.put("/api/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, order_update: OrderUpdate):
    """Update order status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if order exists
        cursor.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update order status
        cursor.execute(
            "UPDATE orders SET status = %s WHERE id = %s RETURNING id, user_id, total_amount, status, created_at",
            (order_update.status, order_id)
        )
        order_data = cursor.fetchone()
        conn.commit()
        
        # Get order items
        cursor.execute(
            "SELECT product_id, quantity, price FROM order_items WHERE order_id = %s",
            (order_id,)
        )
        items_data = cursor.fetchall()
        items = [OrderItem(product_id=item[0], quantity=item[1], price=item[2]) for item in items_data]
        
        order = OrderResponse(
            id=order_data[0],
            user_id=order_data[1],
            items=items,
            total_amount=order_data[2],
            status=order_data[3],
            created_at=order_data[4].isoformat()
        )
        
        # Send order updated event to Kafka
        producer = get_kafka_producer()
        if producer:
            event = {
                'event_type': 'order_updated',
                'order_id': order_id,
                'status': order_update.status,
                'timestamp': datetime.now().isoformat()
            }
            producer.send('order_events', event)
            producer.flush()
        
        cursor.close()
        conn.close()
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update order: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order")

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int):
    """Delete order"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete order items first
        cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        
        # Delete order
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Send order deleted event to Kafka
        producer = get_kafka_producer()
        if producer:
            event = {
                'event_type': 'order_deleted',
                'order_id': order_id,
                'timestamp': datetime.now().isoformat()
            }
            producer.send('order_events', event)
            producer.flush()
        
        return {"message": "Order deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete order: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete order")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
