"""
MongoDB CSV Data Loader
Loads data from CSV files into MongoDB with embedded arrays for time-series data.
Designed for large-scale data processing (110K+ products, millions of time-series records).
"""

import logging
import os
import pandas as pd
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm
from mongodb.config import get_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoCSVLoader:
    """Loads CSV data into MongoDB with embedded arrays"""
    
    def __init__(self, data_dir: str = 'data', chunk_size: int = 10000):
        """
        Initialize CSV loader
        
        Args:
            data_dir: Directory containing CSV files
            chunk_size: Number of rows to process at a time for CSV reading
        """
        self.data_dir = data_dir
        self.chunk_size = chunk_size
        self.db = get_database()
        self.collection = self.db['products']
        
        # In-memory dictionaries to aggregate time-series data by ASIN
        # Using defaultdict for efficient aggregation
        self.price_history_dict: Dict[str, List[Dict]] = defaultdict(list)
        self.sales_rank_history_dict: Dict[str, List[Dict]] = defaultdict(list)
    
    def load_price_history(self, file_path: Optional[str] = None) -> None:
        """
        Load price history CSV and aggregate by ASIN
        
        Args:
            file_path: Path to price_history.csv (default: data/price_history.csv)
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'price_history.csv')
        
        logger.info(f"Loading price history from {file_path}")
        
        # Get total number of rows for progress tracking
        total_rows = sum(1 for _ in open(file_path)) - 1  # Exclude header
        logger.info(f"Total price history records: {total_rows:,}")
        
        # Read CSV in chunks to avoid memory issues
        chunk_count = 0
        with tqdm(total=total_rows, desc="Loading price history") as pbar:
            for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
                chunk_count += 1
                
                # Convert each row to dictionary and group by ASIN
                for _, row in chunk.iterrows():
                    asin = str(row['asin']).strip()
                    if pd.isna(asin) or asin == '':
                        continue
                    
                    # Create price history entry
                    price_entry = {
                        'date': str(row['date']),
                        'price_usd': float(row['price_usd']) if pd.notna(row['price_usd']) else None,
                    }
                    
                    # Add optional fields if they exist
                    if 'source_category' in row and pd.notna(row['source_category']):
                        price_entry['source_category'] = str(row['source_category'])
                    if 'brand' in row and pd.notna(row['brand']):
                        price_entry['brand'] = str(row['brand'])
                    if 'price_bucket' in row and pd.notna(row['price_bucket']):
                        price_entry['price_bucket'] = str(row['price_bucket'])
                    
                    self.price_history_dict[asin].append(price_entry)
                    pbar.update(1)
                
                # Clear chunk from memory
                del chunk
                
                # Log progress every 10 chunks
                if chunk_count % 10 == 0:
                    logger.info(f"Processed {chunk_count * self.chunk_size:,} price history records, "
                              f"unique ASINs: {len(self.price_history_dict):,}")
        
        logger.info(f"Price history loading complete. Unique ASINs: {len(self.price_history_dict):,}")
    
    def load_sales_rank_history(self, file_path: Optional[str] = None) -> None:
        """
        Load sales rank history CSV and aggregate by ASIN
        
        Args:
            file_path: Path to sales_rank_history.csv (default: data/sales_rank_history.csv)
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'sales_rank_history.csv')
        
        logger.info(f"Loading sales rank history from {file_path}")
        
        # Get total number of rows for progress tracking
        total_rows = sum(1 for _ in open(file_path)) - 1  # Exclude header
        logger.info(f"Total sales rank history records: {total_rows:,}")
        
        # Read CSV in chunks to avoid memory issues
        chunk_count = 0
        with tqdm(total=total_rows, desc="Loading sales rank history") as pbar:
            for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
                chunk_count += 1
                
                # Convert each row to dictionary and group by ASIN
                for _, row in chunk.iterrows():
                    asin = str(row['asin']).strip()
                    if pd.isna(asin) or asin == '':
                        continue
                    
                    # Create sales rank history entry
                    sales_rank_entry = {
                        'date': str(row['date']),
                        'sales_rank': float(row['sales_rank']) if pd.notna(row['sales_rank']) else None,
                    }
                    
                    # Add optional fields if they exist
                    if 'source_category' in row and pd.notna(row['source_category']):
                        sales_rank_entry['source_category'] = str(row['source_category'])
                    if 'brand' in row and pd.notna(row['brand']):
                        sales_rank_entry['brand'] = str(row['brand'])
                    if 'rank_bucket' in row and pd.notna(row['rank_bucket']):
                        sales_rank_entry['rank_bucket'] = str(row['rank_bucket'])
                    
                    self.sales_rank_history_dict[asin].append(sales_rank_entry)
                    pbar.update(1)
                
                # Clear chunk from memory
                del chunk
                
                # Log progress every 10 chunks
                if chunk_count % 10 == 0:
                    logger.info(f"Processed {chunk_count * self.chunk_size:,} sales rank history records, "
                              f"unique ASINs: {len(self.sales_rank_history_dict):,}")
        
        logger.info(f"Sales rank history loading complete. Unique ASINs: {len(self.sales_rank_history_dict):,}")
    
    def load_products(self, file_path: Optional[str] = None, batch_size: int = 1000) -> None:
        """
        Load products CSV and create MongoDB documents with embedded arrays
        
        Args:
            file_path: Path to products.csv (default: data/products.csv)
            batch_size: Number of documents to insert per batch
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'products.csv')
        
        logger.info(f"Loading products from {file_path}")
        
        # Get total number of rows for progress tracking
        total_rows = sum(1 for _ in open(file_path)) - 1  # Exclude header
        logger.info(f"Total product records: {total_rows:,}")
        
        documents_to_insert: List[Dict] = []
        processed_count = 0
        
        # Read CSV in chunks
        chunk_count = 0
        with tqdm(total=total_rows, desc="Loading products") as pbar:
            for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
                chunk_count += 1
                
                for _, row in chunk.iterrows():
                    asin = str(row['asin']).strip()
                    if pd.isna(asin) or asin == '':
                        continue
                    
                    # Create base product document
                    product_doc = {
                        'asin': asin,
                        'title': str(row['title']) if pd.notna(row['title']) else None,
                    }
                    
                    # Add optional fields
                    if 'brand' in row and pd.notna(row['brand']):
                        product_doc['brand'] = str(row['brand'])
                    if 'source_category' in row and pd.notna(row['source_category']):
                        product_doc['category'] = str(row['source_category'])
                    if 'current_price' in row and pd.notna(row['current_price']):
                        product_doc['current_price'] = float(row['current_price'])
                    if 'current_sales_rank' in row and pd.notna(row['current_sales_rank']):
                        product_doc['current_sales_rank'] = float(row['current_sales_rank'])
                    if 'rating' in row and pd.notna(row['rating']):
                        product_doc['rating'] = float(row['rating'])
                    if 'review_count' in row and pd.notna(row['review_count']):
                        product_doc['review_count'] = float(row['review_count'])
                    
                    # Embed price history array
                    product_doc['price_history'] = self.price_history_dict.get(asin, [])
                    
                    # Embed sales rank history array (rename from reviews to sales_rank_history for clarity)
                    product_doc['sales_rank_history'] = self.sales_rank_history_dict.get(asin, [])
                    
                    # Add timestamps
                    product_doc['created_at'] = datetime.utcnow()
                    product_doc['updated_at'] = datetime.utcnow()
                    
                    documents_to_insert.append(product_doc)
                    processed_count += 1
                    
                    # Insert in batches to avoid memory issues
                    if len(documents_to_insert) >= batch_size:
                        try:
                            self.collection.insert_many(documents_to_insert, ordered=False)
                            logger.info(f"Inserted batch of {len(documents_to_insert)} products (total: {processed_count:,})")
                            documents_to_insert.clear()
                        except Exception as e:
                            logger.error(f"Error inserting batch: {e}")
                            # Continue with next batch even if one fails
                            documents_to_insert.clear()
                    
                    pbar.update(1)
                
                # Clear chunk from memory
                del chunk
        
        # Insert remaining documents
        if documents_to_insert:
            try:
                self.collection.insert_many(documents_to_insert, ordered=False)
                logger.info(f"Inserted final batch of {len(documents_to_insert)} products")
            except Exception as e:
                logger.error(f"Error inserting final batch: {e}")
        
        logger.info(f"Product loading complete. Total products processed: {processed_count:,}")
        
        # Clear dictionaries from memory after loading
        self.price_history_dict.clear()
        self.sales_rank_history_dict.clear()
        logger.info("Cleared time-series data from memory")
    
    def create_indexes(self) -> None:
        """Create indexes on the products collection"""
        logger.info("Creating indexes...")
        
        try:
            # Create unique index on ASIN
            self.collection.create_index('asin', unique=True, background=True)
            logger.info("✓ Created unique index on 'asin'")
        except Exception as e:
            logger.warning(f"Index on 'asin' may already exist: {e}")
        
        try:
            # Create index on price_history.date (embedded array field)
            self.collection.create_index('price_history.date', background=True)
            logger.info("✓ Created index on 'price_history.date'")
        except Exception as e:
            logger.warning(f"Index on 'price_history.date' may have issues: {e}")
        
        try:
            # Create index on sales_rank_history.date (embedded array field)
            self.collection.create_index('sales_rank_history.date', background=True)
            logger.info("✓ Created index on 'sales_rank_history.date'")
        except Exception as e:
            logger.warning(f"Index on 'sales_rank_history.date' may have issues: {e}")
        
        try:
            # Create index on brand (common query field)
            self.collection.create_index('brand', background=True)
            logger.info("✓ Created index on 'brand'")
        except Exception as e:
            logger.warning(f"Index on 'brand' may have issues: {e}")
        
        try:
            # Create index on category (common query field)
            self.collection.create_index('category', background=True)
            logger.info("✓ Created index on 'category'")
        except Exception as e:
            logger.warning(f"Index on 'category' may have issues: {e}")
        
        logger.info("Index creation complete")
    
    def run_full_load(self) -> None:
        """
        Execute full data load process:
        1. Load price history
        2. Load sales rank history
        3. Load products with embedded arrays
        4. Create indexes
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("Starting MongoDB CSV data load process")
        logger.info("=" * 60)
        
        try:
            # Step 1: Load time-series data first
            self.load_price_history()
            self.load_sales_rank_history()
            
            # Step 2: Load products with embedded arrays
            self.load_products()
            
            # Step 3: Create indexes
            self.create_indexes()
            
            # Report statistics
            product_count = self.collection.count_documents({})
            logger.info("=" * 60)
            logger.info("Data load complete!")
            logger.info(f"Total products in database: {product_count:,}")
            
            # Calculate some statistics
            pipeline = [
                {'$project': {
                    'price_history_count': {'$size': {'$ifNull': ['$price_history', []]}},
                    'sales_rank_history_count': {'$size': {'$ifNull': ['$sales_rank_history', []]}}
                }},
                {'$group': {
                    '_id': None,
                    'avg_price_history': {'$avg': '$price_history_count'},
                    'avg_sales_rank_history': {'$avg': '$sales_rank_history_count'},
                    'max_price_history': {'$max': '$price_history_count'},
                    'max_sales_rank_history': {'$max': '$sales_rank_history_count'}
                }}
            ]
            
            stats = list(self.collection.aggregate(pipeline))
            if stats:
                logger.info(f"Average price history records per product: {stats[0].get('avg_price_history', 0):.1f}")
                logger.info(f"Average sales rank history records per product: {stats[0].get('avg_sales_rank_history', 0):.1f}")
                logger.info(f"Max price history records: {stats[0].get('max_price_history', 0)}")
                logger.info(f"Max sales rank history records: {stats[0].get('max_sales_rank_history', 0)}")
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Total elapsed time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error during data load: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    # Example usage
    loader = MongoCSVLoader(data_dir='data', chunk_size=10000)
    loader.run_full_load()

