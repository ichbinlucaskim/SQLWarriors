#!/usr/bin/env python3
"""Simple connection test"""
import os
os.environ.setdefault('POSTGRES_PORT', '5433')
os.environ.setdefault('POSTGRES_PASSWORD', 'postgres')

import psycopg2
from pymongo import MongoClient

print("Testing database connections...")

# PostgreSQL
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='amazon_warehouse',
        user='postgres',
        password='postgres',
        connect_timeout=5
    )
    print("✓ PostgreSQL: CONNECTED")
    conn.close()
except Exception as e:
    print(f"✗ PostgreSQL: {e}")

# MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✓ MongoDB: CONNECTED")
except Exception as e:
    print(f"✗ MongoDB: {e}")

