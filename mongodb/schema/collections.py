"""
MongoDB Collection Definitions
NoSQL Warehouse Architect: Lucas Kim
"""

from mongodb.config import get_database
import logging

logger = logging.getLogger(__name__)


def create_collections():
    """
    Create MongoDB collections and define schema structure
    
    Schema Design Options:
    1. Embedded: Price history and reviews embedded in product documents
    2. Referenced: Separate collections with references
    3. Hybrid: Frequently accessed data embedded, historical data referenced
    """
    db = get_database()
    
    # Products collection
    # Decision: Use embedded approach for price_history and reviews
    # Rationale: Reduces joins, improves read performance for common queries
    products_collection = db['products']
    
    # Create indexes
    products_collection.create_index('asin', unique=True)
    products_collection.create_index('brand')
    products_collection.create_index('category')
    products_collection.create_index('updated_at')
    
    # Indexes for embedded arrays
    products_collection.create_index('price_history.date')
    products_collection.create_index('reviews.date')
    
    logger.info("MongoDB collections and indexes created")
    
    # Alternative: Separate collections approach
    # Uncomment if using referenced approach
    # price_history_collection = db['price_history']
    # price_history_collection.create_index([('asin', 1), ('date', 1)], unique=True)
    # price_history_collection.create_index('date')
    # 
    # reviews_collection = db['reviews']
    # reviews_collection.create_index([('asin', 1), ('date', 1)], unique=True)
    # reviews_collection.create_index('sales_rank')


def get_product_schema_example():
    """
    Example product document structure (embedded approach)
    
    Returns:
        Example document structure
    """
    return {
        "asin": "B08N5WRWNW",
        "title": "Example Product Title",
        "brand": "Example Brand",
        "category": "Electronics",
        "features": ["Feature 1", "Feature 2"],
        "description": "Product description text",
        "price_history": [
            {
                "date": "2024-01-01",
                "price": 99.99,
                "offer_count": 5
            },
            {
                "date": "2024-01-02",
                "price": 89.99,
                "offer_count": 6
            }
        ],
        "reviews": [
            {
                "date": "2024-01-01",
                "sales_rank": 1234,
                "review_count": 150,
                "average_rating": 4.5
            }
        ],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    create_collections()

