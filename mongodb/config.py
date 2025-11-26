"""
MongoDB Configuration
Connection and database settings
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_client() -> MongoClient:
    """Get MongoDB client from environment"""
    host = os.getenv('MONGODB_HOST', 'localhost')
    port = int(os.getenv('MONGODB_PORT', 27017))
    username = os.getenv('MONGODB_USER')
    password = os.getenv('MONGODB_PASSWORD')
    
    if username and password:
        uri = f"mongodb://{username}:{password}@{host}:{port}/"
    else:
        uri = f"mongodb://{host}:{port}/"
    
    return MongoClient(uri)


def get_database():
    """Get MongoDB database instance"""
    client = get_client()
    db_name = os.getenv('MONGODB_DB', 'amazon_warehouse')
    return client[db_name]

