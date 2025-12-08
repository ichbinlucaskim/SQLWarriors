"""
Query Performance Benchmarking
Compares query execution time between PostgreSQL and MongoDB for analytical queries.
"""

import time
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, Optional
from postgres.config import get_connection_string
from mongodb.config import get_database
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QueryBenchmark:
    """Benchmark queries for PostgreSQL and MongoDB"""
    
    def __init__(self):
        """Initialize database connections"""
        self.postgres_conn = None
        self.mongo_db = None
        
    def connect_postgres(self):
        """Connect to PostgreSQL"""
        try:
            conn_string = get_connection_string()
            self.postgres_conn = psycopg2.connect(conn_string)
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            raise
    
    def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_db = get_database()
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise
    
    def close_postgres(self):
        """Close PostgreSQL connection"""
        if self.postgres_conn:
            self.postgres_conn.close()
            logger.info("PostgreSQL connection closed")
    
    # ==================== Query 1: Price Trend by Category ====================
    
    def postgres_query_price_trend(self, category: Optional[str] = None, months: int = 12) -> list:
        """
        Query 1: Price trend by category - Monthly average price by category
        
        Args:
            category: Optional category filter (e.g., 'Electronics')
            months: Number of months to look back
            
        Returns:
            List of results
        """
        query = """
            SELECT 
                source_category as category,
                DATE_TRUNC('month', date)::DATE as month,
                COUNT(DISTINCT asin) as product_count,
                AVG(price_usd) as avg_price,
                MIN(price_usd) as min_price,
                MAX(price_usd) as max_price,
                STDDEV(price_usd) as price_stddev
            FROM price_history
            WHERE date >= CURRENT_DATE - INTERVAL '%s months'
        """
        
        if category:
            query += " AND source_category = %s"
            params = (months, category)
        else:
            params = (months,)
        
        query += """
            GROUP BY source_category, DATE_TRUNC('month', date)
            ORDER BY month DESC, category
        """
        
        with self.postgres_conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return results
    
    def mongodb_query_price_trend(self, category: Optional[str] = None, months: int = 12) -> list:
        """
        Query 1: Price trend by category - Monthly average price by category
        
        Args:
            category: Optional category filter (e.g., 'Electronics')
            months: Number of months to look back
            
        Returns:
            List of results
        """
        # Calculate start date string (YYYY-MM-DD format)
        start_date_str = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
        
        pipeline = [
            # Unwind price history array
            {'$unwind': '$price_history'},
            # Filter by date range (string comparison works for YYYY-MM-DD format)
            {
                '$match': {
                    'price_history.date': {'$gte': start_date_str}
                }
            }
        ]
        
        # Add category filter if provided
        if category:
            pipeline[1]['$match']['category'] = category
        
        pipeline.extend([
            # Extract year-month from date string (YYYY-MM-DD format)
            {
                '$addFields': {
                    'year_month': {
                        '$substr': ['$price_history.date', 0, 7]  # Extract YYYY-MM
                    }
                }
            },
            # Group by category and year-month
            {
                '$group': {
                    '_id': {
                        'category': '$category',
                        'year_month': '$year_month'
                    },
                    'product_count': {'$addToSet': '$asin'},
                    'avg_price': {'$avg': '$price_history.price_usd'},
                    'min_price': {'$min': '$price_history.price_usd'},
                    'max_price': {'$max': '$price_history.price_usd'},
                    'price_stddev': {'$stdDevPop': '$price_history.price_usd'}
                }
            },
            # Project results
            {
                '$project': {
                    'category': '$_id.category',
                    'month': {'$concat': ['$_id.year_month', '-01']},  # Convert to YYYY-MM-01 for date
                    'product_count': {'$size': '$product_count'},
                    'avg_price': 1,
                    'min_price': 1,
                    'max_price': 1,
                    'price_stddev': 1,
                    '_id': 0
                }
            },
            # Sort
            {'$sort': {'month': -1, 'category': 1}}
        ])
        
        collection = self.mongo_db['products']
        return list(collection.aggregate(pipeline))
    
    # ==================== Query 2: Top Products by Sales Rank Improvement ====================
    
    def postgres_query_top_sales_rank_improvement(self, days: int = 30, limit: int = 10) -> list:
        """
        Query 2: Top products by sales rank improvement
        Find products with the largest sales rank improvement in recent days
        
        Args:
            days: Number of days to look back
            limit: Number of top products to return
            
        Returns:
            List of results
        """
        query = """
            WITH rank_changes AS (
                SELECT 
                    srh.asin,
                    p.title,
                    p.brand,
                    p.source_category as category,
                    srh.date,
                    srh.sales_rank,
                    LAG(srh.sales_rank) OVER (PARTITION BY srh.asin ORDER BY srh.date) as previous_rank,
                    srh.sales_rank - LAG(srh.sales_rank) OVER (PARTITION BY srh.asin ORDER BY srh.date) as rank_change
                FROM sales_rank_history srh
                JOIN products p ON srh.asin = p.asin
                WHERE srh.date >= CURRENT_DATE - INTERVAL '%s days'
                  AND srh.sales_rank IS NOT NULL
            )
            SELECT 
                asin,
                title,
                brand,
                category,
                date,
                sales_rank,
                previous_rank,
                rank_change
            FROM rank_changes
            WHERE rank_change IS NOT NULL
              AND rank_change < 0  -- Negative means improvement (lower rank number = better)
            ORDER BY rank_change ASC  -- Most negative = best improvement
            LIMIT %s
        """
        
        with self.postgres_conn.cursor() as cursor:
            cursor.execute(query, (days, limit))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return results
    
    def mongodb_query_top_sales_rank_improvement(self, days: int = 30, limit: int = 10) -> list:
        """
        Query 2: Top products by sales rank improvement
        Find products with the largest sales rank improvement in recent days
        
        Args:
            days: Number of days to look back
            limit: Number of top products to return
            
        Returns:
            List of results
        """
        start_date = datetime.now() - timedelta(days=days)
        
        pipeline = [
            # Unwind sales rank history
            {'$unwind': '$sales_rank_history'},
            # Filter by date range and non-null sales_rank
            {
                '$match': {
                    'sales_rank_history.date': {'$gte': start_date.strftime('%Y-%m-%d')},
                    'sales_rank_history.sales_rank': {'$ne': None}
                }
            },
            # Sort by asin and date
            {'$sort': {'asin': 1, 'sales_rank_history.date': 1}},
            # Group to calculate rank changes
            {
                '$group': {
                    '_id': '$asin',
                    'product': {'$first': '$$ROOT'},
                    'rank_history': {'$push': '$sales_rank_history'}
                }
            },
            # Calculate rank improvements
            {
                '$project': {
                    'asin': '$_id',
                    'title': '$product.title',
                    'brand': '$product.brand',
                    'category': '$product.category',
                    'rank_improvements': {
                        '$map': {
                            'input': {'$range': [1, {'$size': '$rank_history'}]},
                            'as': 'idx',
                            'in': {
                                'date': {'$arrayElemAt': ['$rank_history.date', '$$idx']},
                                'sales_rank': {'$arrayElemAt': ['$rank_history.sales_rank', '$$idx']},
                                'previous_rank': {'$arrayElemAt': ['$rank_history.sales_rank', {'$subtract': ['$$idx', 1]}]},
                                'rank_change': {
                                    '$subtract': [
                                        {'$arrayElemAt': ['$rank_history.sales_rank', {'$subtract': ['$$idx', 1]}]},
                                        {'$arrayElemAt': ['$rank_history.sales_rank', '$$idx']}
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            # Unwind improvements
            {'$unwind': '$rank_improvements'},
            # Filter for improvements (negative rank_change means improvement)
            {'$match': {'rank_improvements.rank_change': {'$lt': 0}}},
            # Sort by rank improvement (most negative first)
            {'$sort': {'rank_improvements.rank_change': 1}},
            # Limit results
            {'$limit': limit},
            # Project final format
            {
                '$project': {
                    'asin': 1,
                    'title': 1,
                    'brand': 1,
                    'category': 1,
                    'date': '$rank_improvements.date',
                    'sales_rank': '$rank_improvements.sales_rank',
                    'previous_rank': '$rank_improvements.previous_rank',
                    'rank_change': '$rank_improvements.rank_change'
                }
            }
        ]
        
        collection = self.mongo_db['products']
        return list(collection.aggregate(pipeline))
    
    # ==================== Query 3: Brand Analysis ====================
    
    def postgres_query_brand_analysis(self, brand: Optional[str] = None) -> list:
        """
        Query 3: Brand analysis - Average rating and review count by product for a brand
        
        Args:
            brand: Brand name to analyze (optional, if None analyzes all brands)
            
        Returns:
            List of results
        """
        query = """
            SELECT 
                p.brand,
                p.asin,
                p.title,
                AVG(p.rating) as avg_rating,
                AVG(p.review_count) as avg_review_count,
                MAX(p.review_count) as max_review_count,
                COUNT(*) as metric_count
            FROM products p
            WHERE p.brand IS NOT NULL
        """
        
        params = []
        if brand:
            query += " AND p.brand = %s"
            params.append(brand)
        
        query += """
            GROUP BY p.brand, p.asin, p.title
            ORDER BY p.brand, avg_rating DESC, avg_review_count DESC
        """
        
        with self.postgres_conn.cursor() as cursor:
            cursor.execute(query, params if params else None)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return results
    
    def mongodb_query_brand_analysis(self, brand: Optional[str] = None) -> list:
        """
        Query 3: Brand analysis - Average rating and review count by product for a brand
        
        Args:
            brand: Brand name to analyze (optional, if None analyzes all brands)
            
        Returns:
            List of results
        """
        pipeline = [
            # Filter for products with brand
            {'$match': {'brand': {'$ne': None}}}
        ]
        
        # Add brand filter if provided
        if brand:
            pipeline[0]['$match']['brand'] = brand
        
        pipeline.extend([
            # Group by brand and asin
            {
                '$group': {
                    '_id': {
                        'brand': '$brand',
                        'asin': '$asin'
                    },
                    'title': {'$first': '$title'},
                    'avg_rating': {'$avg': '$rating'},
                    'avg_review_count': {'$avg': '$review_count'},
                    'max_review_count': {'$max': '$review_count'},
                    'metric_count': {'$sum': 1}
                }
            },
            # Project results
            {
                '$project': {
                    'brand': '$_id.brand',
                    'asin': '$_id.asin',
                    'title': 1,
                    'avg_rating': 1,
                    'avg_review_count': 1,
                    'max_review_count': 1,
                    'metric_count': 1,
                    '_id': 0
                }
            },
            # Sort
            {'$sort': {'brand': 1, 'avg_rating': -1, 'avg_review_count': -1}}
        ])
        
        collection = self.mongo_db['products']
        return list(collection.aggregate(pipeline))
    
    # ==================== Benchmarking Methods ====================
    
    def benchmark_query(self, query_name: str, postgres_func, mongodb_func, 
                       postgres_args: tuple = (), mongodb_args: tuple = (),
                       iterations: int = 1) -> Dict:
        """
        Benchmark a query on both databases
        
        Args:
            query_name: Name of the query being benchmarked
            postgres_func: PostgreSQL query function
            mongodb_func: MongoDB query function
            postgres_args: Arguments for PostgreSQL function
            mongodb_args: Arguments for MongoDB function
            iterations: Number of iterations to run (for averaging)
            
        Returns:
            Dictionary with benchmark results
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Benchmarking: {query_name}")
        logger.info(f"{'='*60}")
        
        postgres_times = []
        mongodb_times = []
        
        # Benchmark PostgreSQL
        logger.info("Running PostgreSQL query...")
        for i in range(iterations):
            try:
                start = time.time()
                postgres_results = postgres_func(*postgres_args)
                elapsed = time.time() - start
                postgres_times.append(elapsed)
                if i == 0:
                    logger.info(f"  Results: {len(postgres_results)} rows")
            except Exception as e:
                logger.error(f"PostgreSQL query failed: {e}")
                postgres_times.append(float('inf'))
        
        # Benchmark MongoDB
        logger.info("Running MongoDB query...")
        for i in range(iterations):
            try:
                start = time.time()
                mongodb_results = mongodb_func(*mongodb_args)
                elapsed = time.time() - start
                mongodb_times.append(elapsed)
                if i == 0:
                    logger.info(f"  Results: {len(mongodb_results)} rows")
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}")
                mongodb_times.append(float('inf'))
        
        # Calculate averages
        postgres_avg = sum(postgres_times) / len(postgres_times) if postgres_times else float('inf')
        mongodb_avg = sum(mongodb_times) / len(mongodb_times) if mongodb_times else float('inf')
        
        # Print results in requested format
        postgres_str = f"{postgres_avg:.3f}s" if postgres_avg != float('inf') else "ERROR"
        mongodb_str = f"{mongodb_avg:.3f}s" if mongodb_avg != float('inf') else "ERROR"
        
        print(f"\n{query_name}:")
        print(f"  Postgres: {postgres_str} vs Mongo: {mongodb_str}")
        
        # Determine winner
        if postgres_avg < mongodb_avg:
            faster = "PostgreSQL"
            speedup = mongodb_avg / postgres_avg if postgres_avg > 0 else float('inf')
        elif mongodb_avg < postgres_avg:
            faster = "MongoDB"
            speedup = postgres_avg / mongodb_avg if mongodb_avg > 0 else float('inf')
        else:
            faster = "Tie"
            speedup = 1.0
        
        if faster != "Tie" and speedup != float('inf'):
            print(f"  → {faster} is {speedup:.2f}x faster")
        
        return {
            'query_name': query_name,
            'postgres_time': postgres_avg,
            'mongodb_time': mongodb_avg,
            'faster': faster,
            'speedup': speedup,
            'postgres_results_count': len(postgres_results) if 'postgres_results' in locals() else 0,
            'mongodb_results_count': len(mongodb_results) if 'mongodb_results' in locals() else 0
        }
    
    def run_all_benchmarks(self, iterations: int = 1):
        """
        Run all benchmark queries
        
        Args:
            iterations: Number of iterations per query (for averaging)
        """
        logger.info("="*60)
        logger.info("Starting Query Performance Benchmarks")
        logger.info("="*60)
        
        try:
            self.connect_postgres()
            self.connect_mongodb()
            
            results = []
            
            # Query 1: Price Trend by Category
            results.append(self.benchmark_query(
                "Price Trend by Category (12 months)",
                self.postgres_query_price_trend,
                self.mongodb_query_price_trend,
                postgres_args=(None, 12),
                mongodb_args=(None, 12),
                iterations=iterations
            ))
            
            # Query 2: Top Products by Sales Rank Improvement
            results.append(self.benchmark_query(
                "Top Products by Sales Rank Improvement (30 days, top 10)",
                self.postgres_query_top_sales_rank_improvement,
                self.mongodb_query_top_sales_rank_improvement,
                postgres_args=(30, 10),
                mongodb_args=(30, 10),
                iterations=iterations
            ))
            
            # Query 3: Brand Analysis
            results.append(self.benchmark_query(
                "Brand Analysis (all brands)",
                self.postgres_query_brand_analysis,
                self.mongodb_query_brand_analysis,
                postgres_args=(None,),
                mongodb_args=(None,),
                iterations=iterations
            ))
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("Benchmark Summary")
            logger.info("="*60)
            for result in results:
                print(f"{result['query_name']}: Postgres: {result['postgres_time']:.3f}s vs Mongo: {result['mongodb_time']:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}", exc_info=True)
            raise
        finally:
            self.close_postgres()


if __name__ == "__main__":
    benchmark = QueryBenchmark()
    results = benchmark.run_all_benchmarks(iterations=1)
