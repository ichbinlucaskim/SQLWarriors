"""
MongoDB Index Creation
NoSQL Warehouse Architect: Lucas Kim
"""

from mongodb.config import get_database
import logging

logger = logging.getLogger(__name__)


def create_indexes():
    """
    Create all indexes for MongoDB collections
    Optimize for common query patterns
    """
    db = get_database()
    
    # Products collection indexes
    products = db['products']
    
    # Single field indexes
    products.create_index('asin', unique=True)
    products.create_index('brand')
    products.create_index('category')
    products.create_index('updated_at')
    
    # Compound indexes for common queries
    products.create_index([('category', 1), ('brand', 1)])
    products.create_index([('category', 1), ('updated_at', -1)])
    
    # Indexes for embedded arrays
    products.create_index('price_history.date')
    products.create_index('price_history.price')
    products.create_index('reviews.date')
    products.create_index('reviews.sales_rank')
    
    # Text index for search
    products.create_index([('title', 'text'), ('description', 'text')])
    
    logger.info("MongoDB indexes created successfully")


if __name__ == "__main__":
    create_indexes()

