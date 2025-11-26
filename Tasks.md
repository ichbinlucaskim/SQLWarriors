# Team Tasks & Responsibilities

## Philip Anand - ETL Lead

### Phase 1: Setup & Infrastructure
- [ ] Set up Keepa API account and obtain API key
- [ ] Configure environment variables (.env file)
- [ ] Test Keepa API connection and understand rate limits
- [ ] Set up Python virtual environment and install dependencies

### Phase 2: Keepa API Integration
- [ ] Implement `etl/keepa_client.py`
  - [ ] `get_product(asin)` - Fetch single product
  - [ ] `get_products_batch(asins)` - Batch product fetching
  - [ ] `search_products(category, limit)` - Product search by category
  - [ ] Handle rate limiting and retries
  - [ ] Error handling and logging

### Phase 3: Data Extraction
- [ ] Implement `etl/extractor.py`
  - [ ] `extract_products(target_count)` - Main extraction logic
    - [ ] Search products by multiple categories
    - [ ] Fetch detailed product data for each ASIN
    - [ ] Collect price history for each product
    - [ ] Collect sales/review data
  - [ ] `extract_price_history(asin)` - Price history extraction
  - [ ] `extract_sales_data(asin)` - Sales rank and review extraction
  - [ ] Progress tracking and logging

### Phase 4: Data Transformation
- [ ] Implement `etl/transformer.py`
  - [ ] `clean_product_data(raw_data)` - Data cleaning
    - [ ] Remove duplicates
    - [ ] Normalize fields (dates, prices, etc.)
    - [ ] Handle missing values
    - [ ] Validate data types and ASINs
  - [ ] `transform_for_postgres(products)` - Normalize for SQL
    - [ ] Split into products, price_history, reviews tables
    - [ ] Ensure referential integrity
  - [ ] `transform_for_mongodb(products)` - Document format
    - [ ] Decide on embedding vs referencing strategy
    - [ ] Structure documents appropriately
  - [ ] `deduplicate(data, key_field)` - Remove duplicates

### Phase 5: Data Loading
- [ ] Implement `etl/loader_postgres.py`
  - [ ] `load_products(products, batch_size)` - Bulk insert
    - [ ] Use COPY or batch inserts for performance
    - [ ] Handle errors and retries
  - [ ] `load_price_history(price_records, batch_size)`
  - [ ] `load_reviews(review_records, batch_size)`
  - [ ] `incremental_load(new_data)` - Upsert logic
  - [ ] Measure and log load performance

- [ ] Implement `etl/loader_mongodb.py`
  - [ ] `load_products(products, batch_size)` - Bulk insert
    - [ ] Use insert_many with ordered=False for performance
  - [ ] `load_price_history(price_records, batch_size)`
  - [ ] `load_reviews(review_records, batch_size)`
  - [ ] `incremental_load(new_data)` - Upsert with update_one
  - [ ] Measure and log load performance

### Phase 6: ETL Pipeline Orchestration
- [ ] Complete `etl/pipeline.py`
  - [ ] `run_full_load(target_count)` - Full warehouse load
  - [ ] `run_incremental_load()` - Incremental refresh
  - [ ] Error handling and recovery
  - [ ] Progress reporting

### Phase 7: Automation
- [ ] Set up APScheduler for periodic ETL jobs
- [ ] Configure cron jobs (alternative)
- [ ] Implement data validation checks
- [ ] Create ETL monitoring and alerting

### Phase 8: Testing & Validation
- [ ] Test with sample data (100 products)
- [ ] Test with medium dataset (10,000 products)
- [ ] Full load test (100,000+ products)
- [ ] Validate data integrity between PostgreSQL and MongoDB
- [ ] Performance testing and optimization

### Deliverables
- Working ETL pipeline that extracts 100,000+ products
- Automated refresh scheduling
- Data quality reports
- Documentation of ETL process

---

## Kevin Perez - SQL Warehouse Architect

### Phase 1: Schema Design
- [ ] Review dataset requirements and design normalized schema
- [ ] Complete `postgres/schema/create_tables.sql`
  - [ ] Products table with all required fields
  - [ ] Price_history table with proper foreign keys
  - [ ] Reviews table with proper foreign keys
  - [ ] Add constraints (NOT NULL, CHECK, etc.)
  - [ ] Consider partitioning for large tables
- [ ] Document schema design decisions

### Phase 2: Indexing Strategy
- [ ] Complete `postgres/schema/create_indexes.sql`
  - [ ] Primary key indexes (automatic)
  - [ ] Foreign key indexes
  - [ ] Single-column indexes for common filters
  - [ ] Composite indexes for query patterns
  - [ ] Analyze query patterns and optimize
- [ ] Test index performance
- [ ] Document indexing decisions

### Phase 3: Analytical Views
- [ ] Complete `postgres/schema/create_views.sql`
  - [ ] `product_price_trends` view
  - [ ] `top_products_by_rank` view
  - [ ] `monthly_category_stats` view
  - [ ] Consider materialized views for performance
- [ ] Test view performance
- [ ] Refresh strategies for materialized views

### Phase 4: Query Development
- [ ] Complete `postgres/queries/analytical_queries.sql`
  - [ ] Query 1: Pricing trends by category/time
  - [ ] Query 2: Top products by sales rank/price change
  - [ ] Query 3: Aggregated monthly statistics
  - [ ] Query 4: Brand performance analysis
  - [ ] Additional complex analytical queries
- [ ] Optimize queries using EXPLAIN ANALYZE
- [ ] Document query execution plans

### Phase 5: Performance Testing
- [ ] Complete `postgres/queries/performance_tests.sql`
  - [ ] Simple SELECT benchmarks
  - [ ] JOIN performance tests
  - [ ] Aggregation performance tests
  - [ ] Window function performance
  - [ ] EXPLAIN ANALYZE for all queries
- [ ] Measure query execution times
- [ ] Identify bottlenecks and optimize

### Phase 6: Query Optimization
- [ ] Analyze slow queries
- [ ] Add missing indexes
- [ ] Rewrite inefficient queries
- [ ] Use query hints if needed
- [ ] Consider query result caching

### Phase 7: Integration Testing
- [ ] Test with sample data
- [ ] Test with full dataset (100,000+ products)
- [ ] Validate query results
- [ ] Compare results with MongoDB queries
- [ ] Performance benchmarking

### Deliverables
- Complete PostgreSQL schema (tables, indexes, views)
- Optimized analytical queries
- Performance benchmarks and analysis
- Query execution plans and optimization notes
- Schema design documentation

---

## Lucas Kim - NoSQL Warehouse Architect

### Phase 1: Schema Design
- [ ] Review dataset and design MongoDB document structure
- [ ] Decide on embedding vs referencing strategy
  - [ ] Evaluate trade-offs
  - [ ] Document decision rationale
- [ ] Complete `mongodb/schema/collections.py`
  - [ ] Define product document structure
  - [ ] Design embedded arrays (price_history, reviews)
  - [ ] Create example documents
- [ ] Document schema design decisions

### Phase 2: Index Creation
- [ ] Complete `mongodb/schema/indexes.py`
  - [ ] Single field indexes (asin, brand, category)
  - [ ] Compound indexes for common queries
  - [ ] Indexes for embedded array fields
  - [ ] Text indexes for search
- [ ] Test index performance
- [ ] Optimize index strategy

### Phase 3: Aggregation Pipelines
- [ ] Complete `mongodb/queries/aggregation_pipelines.py`
  - [ ] `pricing_trends_by_category()` - Equivalent to PostgreSQL Query 1
  - [ ] `top_products_by_price_change()` - Equivalent to PostgreSQL Query 2
  - [ ] `monthly_category_statistics()` - Equivalent to PostgreSQL Query 3
  - [ ] `brand_performance_analysis()` - Equivalent to PostgreSQL Query 4
- [ ] Optimize aggregation pipelines
- [ ] Test with sample data

### Phase 4: Performance Testing
- [ ] Complete `mongodb/queries/performance_tests.py`
  - [ ] Simple find operations
  - [ ] Aggregation pipeline performance
  - [ ] Explain plans for all queries
  - [ ] Measure execution times
- [ ] Compare with PostgreSQL performance
- [ ] Identify optimization opportunities

### Phase 5: Schema Evolution Testing
- [ ] Test adding new fields to documents
- [ ] Test modifying existing fields
- [ ] Measure schema change effort
- [ ] Compare with PostgreSQL schema evolution
- [ ] Document flexibility advantages

### Phase 6: Throughput Testing
- [ ] Measure bulk insert performance
- [ ] Measure incremental insert performance
- [ ] Test with different batch sizes
- [ ] Compare with PostgreSQL load times
- [ ] Document throughput advantages

### Phase 7: Query Optimization
- [ ] Analyze slow aggregations
- [ ] Optimize pipeline stages
- [ ] Add missing indexes
- [ ] Use projection to reduce data transfer
- [ ] Consider denormalization for performance

### Phase 8: Integration Testing
- [ ] Test with sample data
- [ ] Test with full dataset (100,000+ products)
- [ ] Validate query results match PostgreSQL
- [ ] Performance benchmarking
- [ ] Document MongoDB-specific advantages

### Deliverables
- Complete MongoDB schema (collections, indexes)
- Optimized aggregation pipelines
- Performance benchmarks
- Schema evolution documentation
- Throughput analysis
- NoSQL modeling best practices documentation

---

## Shared Responsibilities

### Week 1 Tasks (Nov 26 - Dec 1)
- [ ] **All**: Environment setup
  - [ ] Install PostgreSQL and MongoDB
  - [ ] Set up Python environment
  - [ ] Configure database connections
  - [ ] Test basic connectivity

- [ ] **All**: Initial data validation
  - [ ] Cross-validate data between PostgreSQL and MongoDB
  - [ ] Verify data integrity
  - [ ] Check for missing or corrupted data

### Week 2 Tasks (Dec 2 - Dec 8)
- [ ] **All**: Benchmarking
  - [ ] Run load performance benchmarks
  - [ ] Run query performance benchmarks
  - [ ] Measure resource usage
  - [ ] Document all results

- [ ] **All**: Visualization
  - [ ] Create comparison charts
  - [ ] Build interactive dashboards
  - [ ] Generate performance reports

- [ ] **All**: Documentation
  - [ ] Write final report
  - [ ] Create presentation
  - [ ] Prepare demonstration

- [ ] **All**: Code Review
  - [ ] Review each other's code
  - [ ] Test integration points
  - [ ] Fix bugs and issues

### Final Deliverables (Dec 9)
- [ ] Complete working data warehouse in both databases
- [ ] Comprehensive benchmark results
- [ ] Final presentation
- [ ] Written report
- [ ] Code repository with documentation

---

## Quick Reference

### Key Files by Role

**Philip (ETL)**:
- `etl/keepa_client.py`
- `etl/extractor.py`
- `etl/transformer.py`
- `etl/loader_postgres.py`
- `etl/loader_mongodb.py`
- `etl/pipeline.py`

**Kevin (PostgreSQL)**:
- `postgres/schema/create_tables.sql`
- `postgres/schema/create_indexes.sql`
- `postgres/schema/create_views.sql`
- `postgres/queries/analytical_queries.sql`
- `postgres/queries/performance_tests.sql`

**Lucas (MongoDB)**:
- `mongodb/schema/collections.py`
- `mongodb/schema/indexes.py`
- `mongodb/queries/aggregation_pipelines.py`
- `mongodb/queries/performance_tests.py`

**All**:
- `benchmarks/` - Performance testing
- `notebooks/` - Analysis and exploration
- `visualizations/` - Charts and dashboards
- `docs/` - Documentation

