"""
PostgreSQL Configuration
Connection and database settings
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_connection_string() -> str:
    """Get PostgreSQL connection string from environment"""
    return (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )

