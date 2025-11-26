"""
MongoDB Aggregation Pipelines for Analytical Queries
NoSQL Warehouse Architect: Lucas Kim
"""

from mongodb.config import get_database
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def pricing_trends_by_category(start_date=None, end_date=None):
    """
    Query 1: Pricing trends by category and time
    Equivalent to PostgreSQL analytical query 1
    """
    db = get_database()
    products = db['products']
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=365)
    if not end_date:
        end_date = datetime.now()
    
    pipeline = [
        # Unwind price history array
        {'$unwind': '$price_history'},
        # Filter by date range
        {
            '$match': {
                'price_history.date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
        },
        # Group by category and month
        {
            '$group': {
                '_id': {
                    'category': '$category',
                    'month': {
                        '$dateTrunc': {
                            'date': '$price_history.date',
                            'unit': 'month'
                        }
                    }
                },
                'product_count': {'$addToSet': '$asin'},
                'avg_price': {'$avg': '$price_history.price'},
                'min_price': {'$min': '$price_history.price'},
                'max_price': {'$max': '$price_history.price'},
                'price_stddev': {'$stdDevPop': '$price_history.price'},
                'avg_offer_count': {'$avg': '$price_history.offer_count'}
            }
        },
        # Calculate product count
        {
            '$project': {
                'category': '$_id.category',
                'month': '$_id.month',
                'product_count': {'$size': '$product_count'},
                'avg_price': 1,
                'min_price': 1,
                'max_price': 1,
                'price_stddev': 1,
                'avg_offer_count': 1
            }
        },
        # Sort
        {'$sort': {'month': -1, 'category': 1}}
    ]
    
    return list(products.aggregate(pipeline))


def top_products_by_price_change(limit=100):
    """
    Query 2: Top products by price change
    Equivalent to PostgreSQL analytical query 2
    """
    db = get_database()
    products = db['products']
    
    pipeline = [
        # Unwind price history
        {'$unwind': '$price_history'},
        # Sort by asin and date
        {'$sort': {'asin': 1, 'price_history.date': 1}},
        # Group to calculate price changes
        {
            '$group': {
                '_id': '$asin',
                'product': {'$first': '$$ROOT'},
                'price_history': {'$push': '$price_history'}
            }
        },
        # Calculate price changes
        {
            '$project': {
                'asin': '$_id',
                'title': '$product.title',
                'brand': '$product.brand',
                'category': '$product.category',
                'price_changes': {
                    '$map': {
                        'input': {'$range': [1, {'$size': '$price_history'}]},
                        'as': 'idx',
                        'in': {
                            'date': {'$arrayElemAt': ['$price_history.date', '$$idx']},
                            'price': {'$arrayElemAt': ['$price_history.price', '$$idx']},
                            'previous_price': {'$arrayElemAt': ['$price_history.price', {'$subtract': ['$$idx', 1]}]},
                            'price_change_pct': {
                                '$multiply': [
                                    {
                                        '$divide': [
                                            {
                                                '$subtract': [
                                                    {'$arrayElemAt': ['$price_history.price', '$$idx']},
                                                    {'$arrayElemAt': ['$price_history.price', {'$subtract': ['$$idx', 1]}]}
                                                ]
                                            },
                                            {'$arrayElemAt': ['$price_history.price', {'$subtract': ['$$idx', 1]}]}
                                        ]
                                    },
                                    100
                                ]
                            }
                        }
                    }
                }
            }
        },
        # Unwind price changes
        {'$unwind': '$price_changes'},
        # Filter out null changes
        {'$match': {'price_changes.price_change_pct': {'$ne': None}}},
        # Sort by absolute price change
        {'$sort': {'price_changes.price_change_pct': -1}},
        # Limit results
        {'$limit': limit}
    ]
    
    return list(products.aggregate(pipeline))


def monthly_category_statistics(start_date=None, end_date=None):
    """
    Query 3: Aggregated monthly statistics
    Equivalent to PostgreSQL analytical query 3
    """
    db = get_database()
    products = db['products']
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=180)
    if not end_date:
        end_date = datetime.now()
    
    pipeline = [
        # Unwind both price_history and reviews
        {'$unwind': {'path': '$price_history', 'preserveNullAndEmptyArrays': True}},
        {'$unwind': {'path': '$reviews', 'preserveNullAndEmptyArrays': True}},
        # Match date range
        {
            '$match': {
                '$or': [
                    {'price_history.date': {'$gte': start_date, '$lte': end_date}},
                    {'reviews.date': {'$gte': start_date, '$lte': end_date}}
                ]
            }
        },
        # Group by category, brand, and month
        {
            '$group': {
                '_id': {
                    'category': '$category',
                    'brand': '$brand',
                    'month': {
                        '$dateTrunc': {
                            'date': '$price_history.date',
                            'unit': 'month'
                        }
                    }
                },
                'unique_products': {'$addToSet': '$asin'},
                'price_records': {
                    '$sum': {'$cond': [{'$ne': ['$price_history', None]}, 1, 0]}
                },
                'avg_price': {'$avg': '$price_history.price'},
                'avg_offers': {'$avg': '$price_history.offer_count'},
                'avg_sales_rank': {'$avg': '$reviews.sales_rank'},
                'avg_rating': {'$avg': '$reviews.average_rating'}
            }
        },
        # Calculate product count
        {
            '$project': {
                'category': '$_id.category',
                'brand': '$_id.brand',
                'month': '$_id.month',
                'unique_products': {'$size': '$unique_products'},
                'price_records': 1,
                'avg_price': 1,
                'avg_offers': 1,
                'avg_sales_rank': 1,
                'avg_rating': 1
            }
        },
        # Filter out groups with no price records
        {'$match': {'price_records': {'$gt': 0}}},
        # Sort
        {'$sort': {'month': -1, 'category': 1, 'brand': 1}}
    ]
    
    return list(products.aggregate(pipeline))


def brand_performance_analysis(limit=50):
    """
    Query 4: Brand performance analysis
    Equivalent to PostgreSQL analytical query 4
    """
    db = get_database()
    products = db['products']
    
    pipeline = [
        # Filter out products without brand
        {'$match': {'brand': {'$ne': None}}},
        # Unwind reviews
        {'$unwind': {'path': '$reviews', 'preserveNullAndEmptyArrays': True}},
        # Unwind price history
        {'$unwind': {'path': '$price_history', 'preserveNullAndEmptyArrays': True}},
        # Group by brand
        {
            '$group': {
                '_id': '$brand',
                'product_count': {'$addToSet': '$asin'},
                'avg_sales_rank': {'$avg': '$reviews.sales_rank'},
                'avg_rating': {'$avg': '$reviews.average_rating'},
                'avg_price': {'$avg': '$price_history.price'},
                'top_100_count': {
                    '$sum': {
                        '$cond': [
                            {'$lte': ['$reviews.sales_rank', 100]},
                            1,
                            0
                        ]
                    }
                }
            }
        },
        # Calculate product count
        {
            '$project': {
                'brand': '$_id',
                'product_count': {'$size': '$product_count'},
                'avg_sales_rank': 1,
                'avg_rating': 1,
                'avg_price': 1,
                'top_100_count': 1
            }
        },
        # Filter brands with at least 10 products
        {'$match': {'product_count': {'$gte': 10}}},
        # Sort by sales rank
        {'$sort': {'avg_sales_rank': 1}},
        # Limit results
        {'$limit': limit}
    ]
    
    return list(products.aggregate(pipeline))


if __name__ == "__main__":
    # Test queries
    logging.basicConfig(level=logging.INFO)
    
    logger.info("Testing pricing trends query...")
    results = pricing_trends_by_category()
    logger.info(f"Found {len(results)} results")
    
    logger.info("Testing top products by price change...")
    results = top_products_by_price_change(limit=10)
    logger.info(f"Found {len(results)} results")

