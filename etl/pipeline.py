"""
Main ETL Pipeline Orchestration
Coordinates extraction, transformation, and loading
"""

import logging
import os
from dotenv import load_dotenv
from etl.keepa_client import KeepaClient
from etl.extractor import DataExtractor
from etl.transformer import DataTransformer
from etl.loader_postgres import PostgresLoader
from etl.loader_mongodb import MongoLoader

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL pipeline orchestrator"""
    
    def __init__(self):
        # Initialize clients and loaders
        keepa_key = os.getenv('KEEPA_API_KEY')
        self.keepa_client = KeepaClient(keepa_key)
        self.extractor = DataExtractor(self.keepa_client)
        self.transformer = DataTransformer()
        
        # PostgreSQL connection
        postgres_conn = (
            f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        )
        self.postgres_loader = PostgresLoader(postgres_conn)
        
        # MongoDB connection
        mongo_conn = (
            f"mongodb://{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}"
        )
        self.mongo_loader = MongoLoader(mongo_conn, os.getenv('MONGODB_DB'))
    
    def run_full_load(self, target_count: int = 100000):
        """
        Execute full data warehouse load
        
        Args:
            target_count: Target number of products to load
        """
        logger.info("Starting full ETL pipeline")
        
        # Extract
        logger.info("Phase 1: Extraction")
        raw_data = self.extractor.extract_products(target_count)
        
        # Transform
        logger.info("Phase 2: Transformation")
        cleaned_data = self.transformer.clean_product_data(raw_data)
        postgres_data = self.transformer.transform_for_postgres(cleaned_data)
        mongo_data = self.transformer.transform_for_mongodb(cleaned_data)
        
        # Load
        logger.info("Phase 3: Loading to PostgreSQL")
        self.postgres_loader.load_products(postgres_data['products'])
        self.postgres_loader.load_price_history(postgres_data['price_history'])
        self.postgres_loader.load_reviews(postgres_data['reviews'])
        
        logger.info("Phase 3: Loading to MongoDB")
        self.mongo_loader.load_products(mongo_data)
        
        logger.info("ETL pipeline completed successfully")
    
    def run_incremental_load(self):
        """
        Execute incremental data warehouse refresh
        """
        logger.info("Starting incremental ETL pipeline")
        # TODO: Implement incremental load logic
        pass


if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run_full_load(target_count=100000)

