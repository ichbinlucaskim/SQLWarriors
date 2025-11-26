"""
MongoDB Tests
"""

import pytest
from mongodb.config import get_client, get_database


def test_mongodb_client_initialization():
    """Test MongoDB client initialization"""
    client = get_client()
    assert client is not None


def test_mongodb_database_access():
    """Test MongoDB database access"""
    db = get_database()
    assert db is not None


# TODO: Add MongoDB schema and query tests

