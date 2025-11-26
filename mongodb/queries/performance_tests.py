"""
MongoDB Performance Test Queries
NoSQL Warehouse Architect: Lucas Kim
"""

import time
from mongodb.config import get_database
from mongodb.queries.aggregation_pipelines import (
    pricing_trends_by_category,
    top_products_by_price_change,
    monthly_category_statistics,
    brand_performance_analysis
)
import logging

logger = logging.getLogger(__name__)


def measure_query_time(query_func, *args, **kwargs):
    """
    Measure execution time of a query function
    
    Args:
        query_func: Query function to measure
        *args, **kwargs: Arguments to pass to query function
        
    Returns:
        Tuple of (results, execution_time_seconds)
    """
    start_time = time.time()
    results = query_func(*args, **kwargs)
    execution_time = time.time() - start_time
    return results, execution_time


def run_performance_tests():
    """
    Run all performance tests and log results
    """
    db = get_database()
    products = db['products']
    
    logger.info("=== MongoDB Performance Tests ===")
    
    # Test 1: Simple count (baseline)
    logger.info("Test 1: Simple count")
    start = time.time()
    count = products.count_documents({})
    elapsed = time.time() - start
    logger.info(f"Count: {count}, Time: {elapsed:.4f}s")
    
    # Test 2: Simple find with filter
    logger.info("Test 2: Find with category filter")
    start = time.time()
    results = list(products.find({'category': 'Electronics'}).limit(1000))
    elapsed = time.time() - start
    logger.info(f"Results: {len(results)}, Time: {elapsed:.4f}s")
    
    # Test 3: Aggregation - pricing trends
    logger.info("Test 3: Pricing trends aggregation")
    results, elapsed = measure_query_time(pricing_trends_by_category)
    logger.info(f"Results: {len(results)}, Time: {elapsed:.4f}s")
    
    # Test 4: Aggregation - top products by price change
    logger.info("Test 4: Top products by price change")
    results, elapsed = measure_query_time(top_products_by_price_change, limit=100)
    logger.info(f"Results: {len(results)}, Time: {elapsed:.4f}s")
    
    # Test 5: Aggregation - monthly statistics
    logger.info("Test 5: Monthly category statistics")
    results, elapsed = measure_query_time(monthly_category_statistics)
    logger.info(f"Results: {len(results)}, Time: {elapsed:.4f}s")
    
    # Test 6: Aggregation - brand performance
    logger.info("Test 6: Brand performance analysis")
    results, elapsed = measure_query_time(brand_performance_analysis, limit=50)
    logger.info(f"Results: {len(results)}, Time: {elapsed:.4f}s")
    
    # Test 7: Explain plan for complex query
    logger.info("Test 7: Explain plan analysis")
    pipeline = [
        {'$unwind': '$price_history'},
        {'$match': {'price_history.price': {'$gt': 50}}},
        {'$group': {'_id': '$category', 'avg_price': {'$avg': '$price_history.price'}}}
    ]
    explain_result = products.aggregate(pipeline).explain()
    logger.info(f"Execution stats: {explain_result.get('executionStats', {})}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_performance_tests()

