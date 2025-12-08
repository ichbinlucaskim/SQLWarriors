"""
Benchmark Dashboard Generation
Orchestrates benchmark execution and generates visualization dashboard.

This script:
1. Executes load performance benchmarks
2. Executes query performance benchmarks  
3. Measures database storage sizes
4. Generates visualization charts
5. Saves results to JSON for documentation
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import psycopg2
import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.query_performance import QueryBenchmark
from etl.loader_postgres_csv import PostgresCSVLoader
from etl.loader_mongodb_csv import MongoCSVLoader
from postgres.config import get_connection_string
from mongodb.config import get_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10


class BenchmarkDashboard:
    """Orchestrates benchmark execution and visualization"""
    
    def __init__(self, skip_load: bool = True):
        """
        Initialize dashboard generator
        
        Args:
            skip_load: If True, skip data loading (assumes data already loaded)
        """
        self.skip_load = skip_load
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'load_performance': {},
            'query_performance': {},
            'storage_size': {}
        }
        
    def measure_load_performance(self) -> Dict:
        """
        Measure data loading performance for both databases
        
        Returns:
            Dictionary with load time measurements
        """
        logger.info("=" * 60)
        logger.info("Measuring Load Performance")
        logger.info("=" * 60)
        
        if self.skip_load:
            logger.info("Skipping data load (assuming data already loaded)")
            logger.info("Using placeholder values for demonstration")
            # Return placeholder values - in production, load would be measured
            return {
                'postgres_load_time': 0.0,
                'mongodb_load_time': 0.0,
                'postgres_throughput': 0,
                'mongodb_throughput': 0,
                'note': 'Load skipped - data already in database'
            }
        
        # Measure PostgreSQL load
        logger.info("Loading data into PostgreSQL...")
        postgres_loader = PostgresCSVLoader(data_dir='data')
        
        start_time = time.time()
        try:
            postgres_results = postgres_loader.run_full_load()
            postgres_load_time = time.time() - start_time
            
            postgres_rows = (
                postgres_results.get('products_count', 0) +
                postgres_results.get('price_history_count', 0) +
                postgres_results.get('sales_rank_history_count', 0) +
                postgres_results.get('product_metrics_count', 0)
            )
            postgres_throughput = postgres_rows / postgres_load_time if postgres_load_time > 0 else 0
        except Exception as e:
            logger.error(f"PostgreSQL load failed: {e}")
            postgres_load_time = float('inf')
            postgres_throughput = 0
        
        # Measure MongoDB load
        logger.info("Loading data into MongoDB...")
        mongo_loader = MongoCSVLoader(data_dir='data', chunk_size=10000)
        
        start_time = time.time()
        try:
            mongo_loader.run_full_load()
            mongodb_load_time = time.time() - start_time
            
            # Get document count for throughput calculation
            db = get_database()
            mongodb_rows = db['products'].count_documents({})
            mongodb_throughput = mongodb_rows / mongodb_load_time if mongodb_load_time > 0 else 0
        except Exception as e:
            logger.error(f"MongoDB load failed: {e}")
            mongodb_load_time = float('inf')
            mongodb_throughput = 0
        
        results = {
            'postgres_load_time': postgres_load_time,
            'mongodb_load_time': mongodb_load_time,
            'postgres_throughput': postgres_throughput,
            'mongodb_throughput': mongodb_throughput
        }
        
        logger.info(f"PostgreSQL load time: {postgres_load_time:.2f}s")
        logger.info(f"MongoDB load time: {mongodb_load_time:.2f}s")
        
        return results
    
    def measure_query_performance(self, iterations: int = 3) -> List[Dict]:
        """
        Measure query performance using QueryBenchmark
        
        Args:
            iterations: Number of iterations per query
            
        Returns:
            List of query benchmark results
        """
        logger.info("=" * 60)
        logger.info("Measuring Query Performance")
        logger.info("=" * 60)
        
        benchmark = QueryBenchmark()
        try:
            results = benchmark.run_all_benchmarks(iterations=iterations)
            return results
        except Exception as e:
            logger.error(f"Query benchmark failed: {e}", exc_info=True)
            return []
    
    def measure_storage_size(self) -> Dict:
        """
        Measure database storage sizes
        
        Returns:
            Dictionary with storage size measurements in MB
        """
        logger.info("=" * 60)
        logger.info("Measuring Storage Sizes")
        logger.info("=" * 60)
        
        results = {
            'postgres_size_mb': 0.0,
            'mongodb_size_mb': 0.0
        }
        
        # PostgreSQL storage size
        try:
            conn = psycopg2.connect(get_connection_string())
            with conn.cursor() as cursor:
                # Get database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                           pg_database_size(current_database()) as size_bytes
                """)
                row = cursor.fetchone()
                postgres_size_bytes = row[1]
                postgres_size_mb = postgres_size_bytes / (1024 * 1024)
                results['postgres_size_mb'] = postgres_size_mb
                logger.info(f"PostgreSQL database size: {row[0]} ({postgres_size_mb:.2f} MB)")
            conn.close()
        except Exception as e:
            logger.error(f"Failed to measure PostgreSQL size: {e}")
        
        # MongoDB storage size
        try:
            db = get_database()
            stats = db.command("dbStats")
            mongodb_size_bytes = stats.get('dataSize', 0) + stats.get('indexSize', 0)
            mongodb_size_mb = mongodb_size_bytes / (1024 * 1024)
            results['mongodb_size_mb'] = mongodb_size_mb
            logger.info(f"MongoDB database size: {mongodb_size_mb:.2f} MB")
        except Exception as e:
            logger.error(f"Failed to measure MongoDB size: {e}")
        
        return results
    
    def generate_visualization(self, output_path: str = 'benchmark_results.png'):
        """
        Generate visualization charts
        
        Args:
            output_path: Path to save the visualization
        """
        logger.info("=" * 60)
        logger.info("Generating Visualization")
        logger.info("=" * 60)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Left plot: Load Time Comparison
        if self.results['load_performance']:
            databases = ['PostgreSQL', 'MongoDB']
            load_times = [
                self.results['load_performance'].get('postgres_load_time', 0),
                self.results['load_performance'].get('mongodb_load_time', 0)
            ]
            
            # Handle infinite values
            load_times = [t if t != float('inf') else 0 for t in load_times]
            
            colors = ['#2E86AB', '#06A77D']  # Blue for PostgreSQL, Green for MongoDB
            bars1 = ax1.bar(databases, load_times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
            
            # Add value annotations
            for i, (bar, val) in enumerate(zip(bars1, load_times)):
                if val > 0:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{val:.2f}s',
                            ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            ax1.set_ylabel('Load Time (seconds)', fontsize=12, fontweight='bold')
            ax1.set_title('Load Time Comparison', fontsize=14, fontweight='bold', pad=15)
            ax1.set_ylim(bottom=0)
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Right plot: Query Latency Comparison
        if self.results['query_performance']:
            query_results = self.results['query_performance']
            
            # Extract query names and times
            query_names = []
            postgres_times = []
            mongodb_times = []
            
            for query_result in query_results:
                # Shorten query names for display
                query_name = query_result.get('query_name', 'Unknown')
                # Extract shorter name
                if 'Price Trend' in query_name:
                    short_name = 'Price Trend'
                elif 'Sales Rank' in query_name:
                    short_name = 'Sales Rank\nImprovement'
                elif 'Brand Analysis' in query_name:
                    short_name = 'Brand Analysis'
                else:
                    short_name = query_name[:20]
                
                query_names.append(short_name)
                postgres_times.append(query_result.get('postgres_time', 0))
                mongodb_times.append(query_result.get('mongodb_time', 0))
            
            # Handle infinite values - mark as failed
            postgres_times_clean = []
            mongodb_times_clean = []
            mongodb_failed = []
            
            for i, (pg_time, mongo_time) in enumerate(zip(postgres_times, mongodb_times)):
                postgres_times_clean.append(pg_time if pg_time != float('inf') else 0)
                if mongo_time == float('inf') or mongo_time == 0:
                    mongodb_times_clean.append(0)
                    mongodb_failed.append(i)
                else:
                    mongodb_times_clean.append(mongo_time)
                    mongodb_failed.append(None)
            
            x = np.arange(len(query_names))
            width = 0.35
            
            bars2_1 = ax2.bar(x - width/2, postgres_times_clean, width, 
                             label='PostgreSQL', color='#2E86AB', alpha=0.8, 
                             edgecolor='black', linewidth=1.5)
            bars2_2 = ax2.bar(x + width/2, mongodb_times_clean, width,
                             label='MongoDB', color='#06A77D', alpha=0.8,
                             edgecolor='black', linewidth=1.5)
            
            # Add value annotations
            for i, (bar, height) in enumerate(zip(bars2_1, postgres_times_clean)):
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.3f}s',
                            ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            for i, (bar, height) in enumerate(zip(bars2_2, mongodb_times_clean)):
                if mongodb_failed[i] is not None:
                    # Show "Failed" annotation for failed queries
                    ax2.text(bar.get_x() + bar.get_width()/2., ax2.get_ylim()[1] * 0.05,
                            'Failed',
                            ha='center', va='bottom', fontsize=9, fontweight='bold',
                            color='red', style='italic')
                elif height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.3f}s',
                            ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            ax2.set_ylabel('Query Latency (seconds)', fontsize=12, fontweight='bold')
            ax2.set_title('Query Latency Comparison', fontsize=14, fontweight='bold', pad=15)
            ax2.set_xticks(x)
            ax2.set_xticklabels(query_names, rotation=0, ha='center')
            ax2.legend(loc='upper left', fontsize=10)
            ax2.set_ylim(bottom=0)
            ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Visualization saved to {output_path}")
        plt.close()
    
    def save_results(self, output_path: str = 'benchmark_data.json'):
        """
        Save benchmark results to JSON
        
        Args:
            output_path: Path to save JSON file
        """
        logger.info(f"Saving results to {output_path}")
        
        # Convert to JSON-serializable format
        json_results = json.loads(json.dumps(self.results, default=str))
        
        with open(output_path, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def run_full_benchmark(self, skip_load: bool = True, query_iterations: int = 3):
        """
        Execute full benchmark suite
        
        Args:
            skip_load: Skip data loading step
            query_iterations: Number of iterations for query benchmarks
        """
        logger.info("=" * 70)
        logger.info("Starting Comprehensive Benchmark Suite")
        logger.info("=" * 70)
        
        self.skip_load = skip_load
        
        # Step 1: Load Performance
        try:
            self.results['load_performance'] = self.measure_load_performance()
        except Exception as e:
            logger.error(f"Load performance measurement failed: {e}")
            self.results['load_performance'] = {}
        
        # Step 2: Query Performance
        try:
            self.results['query_performance'] = self.measure_query_performance(
                iterations=query_iterations
            )
        except Exception as e:
            logger.error(f"Query performance measurement failed: {e}")
            self.results['query_performance'] = []
        
        # Step 3: Storage Size
        try:
            self.results['storage_size'] = self.measure_storage_size()
        except Exception as e:
            logger.error(f"Storage size measurement failed: {e}")
            self.results['storage_size'] = {}
        
        # Step 4: Generate Visualization
        try:
            self.generate_visualization()
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
        
        # Step 5: Save Results
        try:
            self.save_results()
        except Exception as e:
            logger.error(f"Results save failed: {e}")
        
        # Print Summary
        logger.info("=" * 70)
        logger.info("Benchmark Summary")
        logger.info("=" * 70)
        
        if self.results['load_performance']:
            lp = self.results['load_performance']
            logger.info(f"Load Performance:")
            logger.info(f"  PostgreSQL: {lp.get('postgres_load_time', 0):.2f}s")
            logger.info(f"  MongoDB: {lp.get('mongodb_load_time', 0):.2f}s")
        
        if self.results['query_performance']:
            logger.info(f"Query Performance:")
            for qr in self.results['query_performance']:
                logger.info(f"  {qr.get('query_name', 'Unknown')}:")
                logger.info(f"    PostgreSQL: {qr.get('postgres_time', 0):.3f}s")
                logger.info(f"    MongoDB: {qr.get('mongodb_time', 0):.3f}s")
        
        if self.results['storage_size']:
            ss = self.results['storage_size']
            logger.info(f"Storage Size:")
            logger.info(f"  PostgreSQL: {ss.get('postgres_size_mb', 0):.2f} MB")
            logger.info(f"  MongoDB: {ss.get('mongodb_size_mb', 0):.2f} MB")
        
        logger.info("=" * 70)
        logger.info("Benchmark suite completed")
        logger.info("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate benchmark dashboard')
    parser.add_argument('--skip-load', action='store_true', 
                       help='Skip data loading (assumes data already loaded)')
    parser.add_argument('--query-iterations', type=int, default=3,
                       help='Number of iterations for query benchmarks')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    dashboard = BenchmarkDashboard(skip_load=args.skip_load)
    dashboard.run_full_benchmark(
        skip_load=args.skip_load,
        query_iterations=args.query_iterations
    )

