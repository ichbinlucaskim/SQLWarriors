"""
PostgreSQL CSV Data Loader
Loads data from CSV files into PostgreSQL using COPY command for high-speed bulk loading.
Designed for large-scale data processing (110K+ products, millions of time-series records).
"""

import logging
import os
import io
import tempfile
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
from datetime import datetime
from typing import Optional
from postgres.config import get_connection_string

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PostgresCSVLoader:
    """Loads CSV data into PostgreSQL using COPY command for maximum performance"""
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize PostgreSQL CSV loader
        
        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = data_dir
        self.conn = None
        self.conn_string = get_connection_string()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.conn_string)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def load_products(self, file_path: Optional[str] = None) -> int:
        """
        Load products CSV using COPY command
        
        Args:
            file_path: Path to products.csv (default: data/products.csv)
            
        Returns:
            Number of rows loaded
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'products.csv')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Products file not found: {file_path}")
        
        logger.info(f"Loading products from {file_path}")
        start_time = datetime.now()
        
        # Preprocess CSV to convert review_count from float to int
        logger.info("Preprocessing products CSV (converting review_count to integer)...")
        df = pd.read_csv(file_path)
        # Convert review_count from float to int (handling NaN values)
        df['review_count'] = df['review_count'].fillna(0).astype(int)
        
        # Write to temporary file for COPY command
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp_file:
            df.to_csv(tmp_file.name, index=False, lineterminator='\n')
            tmp_path = tmp_file.name
        
        try:
            with self.conn.cursor() as cursor:
                # Open preprocessed CSV file
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    # Skip header row
                    next(f)
                    
                    # Use COPY FROM for high-speed bulk loading
                    cursor.copy_expert(
                        """
                        COPY products (
                            asin, title, brand, source_category, 
                            current_price, current_sales_rank, rating, review_count
                        )
                        FROM STDIN
                        WITH (FORMAT csv, DELIMITER ',', QUOTE '"', ESCAPE '"')
                        """,
                        f
                    )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            rows_inserted = cursor.rowcount
            self.conn.commit()
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✓ Loaded {rows_inserted:,} products in {elapsed_time:.2f} seconds "
                       f"({rows_inserted/elapsed_time:.0f} rows/sec)")
            
            return rows_inserted
    
    def load_price_history(self, file_path: Optional[str] = None) -> int:
        """
        Load price history CSV using COPY command
        
        Args:
            file_path: Path to price_history.csv (default: data/price_history.csv)
            
        Returns:
            Number of rows loaded
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'price_history.csv')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Price history file not found: {file_path}")
        
        logger.info(f"Loading price history from {file_path}")
        start_time = datetime.now()
        
        with self.conn.cursor() as cursor:
            # Open CSV file and read it into memory for COPY
            with open(file_path, 'r', encoding='utf-8') as f:
                # Skip header row
                next(f)
                
                # Use COPY FROM for high-speed bulk loading
                cursor.copy_expert(
                    """
                    COPY price_history (
                        asin, date, price_usd, source_category, brand, price_bucket
                    )
                    FROM STDIN
                    WITH (FORMAT csv, DELIMITER ',', QUOTE '"', ESCAPE '"')
                    """,
                    f
                )
            
            rows_inserted = cursor.rowcount
            self.conn.commit()
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✓ Loaded {rows_inserted:,} price history records in {elapsed_time:.2f} seconds "
                       f"({rows_inserted/elapsed_time:.0f} rows/sec)")
            
            return rows_inserted
    
    def load_sales_rank_history(self, file_path: Optional[str] = None) -> int:
        """
        Load sales rank history CSV using COPY command
        
        Args:
            file_path: Path to sales_rank_history.csv (default: data/sales_rank_history.csv)
            
        Returns:
            Number of rows loaded
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'sales_rank_history.csv')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Sales rank history file not found: {file_path}")
        
        logger.info(f"Loading sales rank history from {file_path}")
        start_time = datetime.now()
        
        with self.conn.cursor() as cursor:
            # Open CSV file and read it into memory for COPY
            with open(file_path, 'r', encoding='utf-8') as f:
                # Skip header row
                next(f)
                
                # Use COPY FROM for high-speed bulk loading
                cursor.copy_expert(
                    """
                    COPY sales_rank_history (
                        asin, date, sales_rank, source_category, brand, rank_bucket
                    )
                    FROM STDIN
                    WITH (FORMAT csv, DELIMITER ',', QUOTE '"', ESCAPE '"')
                    """,
                    f
                )
            
            rows_inserted = cursor.rowcount
            self.conn.commit()
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✓ Loaded {rows_inserted:,} sales rank history records in {elapsed_time:.2f} seconds "
                       f"({rows_inserted/elapsed_time:.0f} rows/sec)")
            
            return rows_inserted
    
    def load_product_metrics(self, file_path: Optional[str] = None) -> int:
        """
        Load product metrics CSV using COPY command
        
        Args:
            file_path: Path to product_metrics.csv (default: data/product_metrics.csv)
            
        Returns:
            Number of rows loaded
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'product_metrics.csv')
        
        if not os.path.exists(file_path):
            logger.warning(f"Product metrics file not found: {file_path}, skipping...")
            return 0
        
        logger.info(f"Loading product metrics from {file_path}")
        start_time = datetime.now()
        
        with self.conn.cursor() as cursor:
            # Open CSV file and read it into memory for COPY
            with open(file_path, 'r', encoding='utf-8') as f:
                # Skip header row
                next(f)
                
                # Use COPY FROM for high-speed bulk loading
                cursor.copy_expert(
                    """
                    COPY product_metrics (
                        asin, source_category, brand, current_price, 
                        current_rating, review_count, current_sales_rank, monthly_sold
                    )
                    FROM STDIN
                    WITH (FORMAT csv, DELIMITER ',', QUOTE '"', ESCAPE '"')
                    """,
                    f
                )
            
            rows_inserted = cursor.rowcount
            self.conn.commit()
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✓ Loaded {rows_inserted:,} product metrics records in {elapsed_time:.2f} seconds "
                       f"({rows_inserted/elapsed_time:.0f} rows/sec)")
            
            return rows_inserted
    
    def verify_data_integrity(self) -> dict:
        """
        Verify data integrity and return statistics
        
        Returns:
            Dictionary with row counts and integrity checks
        """
        logger.info("Verifying data integrity...")
        
        stats = {}
        
        with self.conn.cursor() as cursor:
            # Count rows in each table
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['products_count'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM price_history")
            stats['price_history_count'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sales_rank_history")
            stats['sales_rank_history_count'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM product_metrics")
            stats['product_metrics_count'] = cursor.fetchone()[0]
            
            # Check for orphaned records
            cursor.execute("""
                SELECT COUNT(*) 
                FROM price_history ph
                LEFT JOIN products p ON ph.asin = p.asin
                WHERE p.asin IS NULL
            """)
            stats['orphaned_price_history'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sales_rank_history srh
                LEFT JOIN products p ON srh.asin = p.asin
                WHERE p.asin IS NULL
            """)
            stats['orphaned_sales_rank_history'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM product_metrics pm
                LEFT JOIN products p ON pm.asin = p.asin
                WHERE p.asin IS NULL
            """)
            stats['orphaned_product_metrics'] = cursor.fetchone()[0]
            
            # Calculate averages
            cursor.execute("""
                SELECT 
                    AVG(price_history_per_product) as avg_price_records,
                    MAX(price_history_per_product) as max_price_records
                FROM (
                    SELECT asin, COUNT(*) as price_history_per_product
                    FROM price_history
                    GROUP BY asin
                ) subq
            """)
            price_stats = cursor.fetchone()
            stats['avg_price_records_per_product'] = float(price_stats[0]) if price_stats[0] else 0
            stats['max_price_records_per_product'] = price_stats[1] if price_stats[1] else 0
            
            cursor.execute("""
                SELECT 
                    AVG(sales_rank_history_per_product) as avg_sales_rank_records,
                    MAX(sales_rank_history_per_product) as max_sales_rank_records
                FROM (
                    SELECT asin, COUNT(*) as sales_rank_history_per_product
                    FROM sales_rank_history
                    GROUP BY asin
                ) subq
            """)
            sales_rank_stats = cursor.fetchone()
            stats['avg_sales_rank_records_per_product'] = float(sales_rank_stats[0]) if sales_rank_stats[0] else 0
            stats['max_sales_rank_records_per_product'] = sales_rank_stats[1] if sales_rank_stats[1] else 0
        
        # Log statistics
        logger.info("=" * 60)
        logger.info("Data Integrity Report:")
        logger.info(f"  Products: {stats['products_count']:,}")
        logger.info(f"  Price History: {stats['price_history_count']:,}")
        logger.info(f"  Sales Rank History: {stats['sales_rank_history_count']:,}")
        logger.info(f"  Product Metrics: {stats['product_metrics_count']:,}")
        logger.info(f"  Avg Price Records/Product: {stats['avg_price_records_per_product']:.1f}")
        logger.info(f"  Avg Sales Rank Records/Product: {stats['avg_sales_rank_records_per_product']:.1f}")
        
        # Check for orphaned records
        if stats['orphaned_price_history'] > 0:
            logger.warning(f"  ⚠️ Found {stats['orphaned_price_history']} orphaned price_history records")
        else:
            logger.info("  ✓ No orphaned price_history records")
        
        if stats['orphaned_sales_rank_history'] > 0:
            logger.warning(f"  ⚠️ Found {stats['orphaned_sales_rank_history']} orphaned sales_rank_history records")
        else:
            logger.info("  ✓ No orphaned sales_rank_history records")
        
        if stats['orphaned_product_metrics'] > 0:
            logger.warning(f"  ⚠️ Found {stats['orphaned_product_metrics']} orphaned product_metrics records")
        else:
            logger.info("  ✓ No orphaned product_metrics records")
        
        logger.info("=" * 60)
        
        return stats
    
    def run_full_load(self) -> dict:
        """
        Execute full data load process:
        1. Load products (must be first due to FK constraints)
        2. Load price_history
        3. Load sales_rank_history
        4. Load product_metrics
        5. Verify data integrity
        
        Returns:
            Dictionary with load statistics
        """
        overall_start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("Starting PostgreSQL CSV data load process")
        logger.info("=" * 60)
        
        try:
            self.connect()
            
            # Disable autocommit for transaction control
            self.conn.autocommit = False
            
            # Step 1: Load products first (required for FK constraints)
            products_count = self.load_products()
            
            # Step 2: Load time-series data (can be parallel, but doing sequentially for safety)
            price_history_count = self.load_price_history()
            sales_rank_history_count = self.load_sales_rank_history()
            
            # Step 3: Load product metrics
            product_metrics_count = self.load_product_metrics()
            
            # Step 4: Verify data integrity
            stats = self.verify_data_integrity()
            
            # Calculate total elapsed time
            total_elapsed = (datetime.now() - overall_start_time).total_seconds()
            
            logger.info("=" * 60)
            logger.info("Data load complete!")
            logger.info(f"Total elapsed time: {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} minutes)")
            logger.info(f"Total rows loaded: {products_count + price_history_count + sales_rank_history_count + product_metrics_count:,}")
            logger.info("=" * 60)
            
            return {
                'products_count': products_count,
                'price_history_count': price_history_count,
                'sales_rank_history_count': sales_rank_history_count,
                'product_metrics_count': product_metrics_count,
                'total_elapsed_seconds': total_elapsed,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error during data load: {e}", exc_info=True)
            if self.conn:
                self.conn.rollback()
                logger.error("Transaction rolled back")
            raise
        finally:
            self.close()


if __name__ == "__main__":
    # Example usage
    loader = PostgresCSVLoader(data_dir='data')
    results = loader.run_full_load()
    print(f"\nLoad Results: {results}")

