"""
PostgreSQL Configuration
Connection and database settings
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_connection_string() -> str:
    """Get PostgreSQL connection string from environment"""
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5433')  # Default to 5433 for Docker
    db = os.getenv('POSTGRES_DB', 'amazon_warehouse')
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'your_password_here')
    
    # Always include password in connection string
    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"
    else:
        return f"postgresql://{user}@{host}:{port}/{db}"

