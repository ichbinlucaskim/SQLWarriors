"""
PostgreSQL Tests
"""

import pytest
from postgres.config import get_connection_string


def test_postgres_connection_string():
    """Test PostgreSQL connection string generation"""
    conn_str = get_connection_string()
    assert 'postgresql://' in conn_str


# TODO: Add PostgreSQL schema and query tests

