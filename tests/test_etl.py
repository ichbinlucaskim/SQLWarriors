"""
ETL Pipeline Tests
"""

import pytest
from etl.keepa_client import KeepaClient
from etl.transformer import DataTransformer


def test_keepa_client_initialization():
    """Test KeepaClient initialization"""
    client = KeepaClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.BASE_URL == "https://keepa.com/1.0"


def test_data_transformer_deduplication():
    """Test data deduplication"""
    transformer = DataTransformer()
    data = [
        {'asin': 'B001', 'title': 'Product 1'},
        {'asin': 'B002', 'title': 'Product 2'},
        {'asin': 'B001', 'title': 'Product 1 Duplicate'},
    ]
    unique = transformer.deduplicate(data, key_field='asin')
    assert len(unique) == 2
    assert unique[0]['asin'] == 'B001'
    assert unique[1]['asin'] == 'B002'


# TODO: Add more ETL tests

