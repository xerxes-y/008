#!/usr/bin/env python3
"""
User Service - REST API for user management
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional
import psycopg2
import redis
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="User Service",
    description="REST API for user management",
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

# Redis connection
def get_redis_connection():
    """Get Redis connection"""
    try:
        r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))
        return r
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: str
    status: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        conn = get_db_connection()
        conn.close()
        
        # Check Redis connection
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected",
                "redis": "connected" if redis_conn else "disconnected"
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

# User endpoints
@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (name, email, password, created_at, status) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (user.name, user.email, user.password, datetime.now(), 'active')
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        # Cache user data
        redis_conn = get_redis_connection()
        if redis_conn:
            user_data = {
                'id': user_id,
                'name': user.name,
                'email': user.email,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            redis_conn.setex(f"user:{user_id}", 3600, json.dumps(user_data))
        
        cursor.close()
        conn.close()
        
        return UserResponse(
            id=user_id,
            name=user.name,
            email=user.email,
            created_at=datetime.now().isoformat(),
            status='active'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    try:
        # Try to get from cache first
        redis_conn = get_redis_connection()
        if redis_conn:
            cached_user = redis_conn.get(f"user:{user_id}")
            if cached_user:
                return UserResponse(**json.loads(cached_user))
        
        # Get from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, created_at, status FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = UserResponse(
            id=user_data[0],
            name=user_data[1],
            email=user_data[2],
            created_at=user_data[3].isoformat(),
            status=user_data[4]
        )
        
        # Cache the result
        if redis_conn:
            redis_conn.setex(f"user:{user_id}", 3600, json.dumps(user.dict()))
        
        cursor.close()
        conn.close()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@app.get("/api/users")
async def list_users(limit: int = 10, offset: int = 0):
    """List users with pagination"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, email, created_at, status FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset)
        )
        users_data = cursor.fetchall()
        
        users = []
        for user_data in users_data:
            users.append(UserResponse(
                id=user_data[0],
                name=user_data[1],
                email=user_data[2],
                created_at=user_data[3].isoformat(),
                status=user_data[4]
            ))
        
        cursor.close()
        conn.close()
        
        return {
            "data": users,
            "total": len(users),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    """Update user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build update query
        update_fields = []
        values = []
        
        if user_update.name is not None:
            update_fields.append("name = %s")
            values.append(user_update.name)
        
        if user_update.email is not None:
            update_fields.append("email = %s")
            values.append(user_update.email)
        
        if user_update.status is not None:
            update_fields.append("status = %s")
            values.append(user_update.status)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Execute update
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s RETURNING id, name, email, created_at, status"
        cursor.execute(query, values)
        
        user_data = cursor.fetchone()
        conn.commit()
        
        user = UserResponse(
            id=user_data[0],
            name=user_data[1],
            email=user_data[2],
            created_at=user_data[3].isoformat(),
            status=user_data[4]
        )
        
        # Update cache
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.setex(f"user:{user_id}", 3600, json.dumps(user.dict()))
        
        cursor.close()
        conn.close()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Remove from cache
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.delete(f"user:{user_id}")
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
