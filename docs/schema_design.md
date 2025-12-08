# Schema Design Documentation

## Overview

This document details the schema design strategies for both PostgreSQL (relational) and MongoDB (document-oriented) implementations, explaining the design philosophy, structural decisions, and optimization approaches for each database paradigm.

---

## PostgreSQL Schema (Relational)

### Design Philosophy

The PostgreSQL schema implements a **normalized star schema** optimized for analytical workloads:

- **Normalization:** Separate fact and dimension tables to eliminate data redundancy
- **Referential Integrity:** Foreign key relationships ensure data consistency
- **Query Optimization:** Strategic indexing for JOIN operations and time-series queries
- **Scalability:** Designed to handle 20+ million records with efficient query performance

### Schema Structure

#### Dimension Table: `products`

The primary dimension table containing product master data:

- **Primary Key:** `asin` (VARCHAR(10)) - Amazon Standard Identification Number
- **Attributes:**
  - `title` (TEXT) - Product title
  - `brand` (VARCHAR(255)) - Product brand
  - `source_category` (VARCHAR(255)) - Product category
  - `current_price` (NUMERIC(10, 2)) - Latest price
  - `current_sales_rank` (NUMERIC(12, 2)) - Current sales rank
  - `rating` (NUMERIC(3, 2)) - Average rating
  - `review_count` (INTEGER) - Total review count
  - `created_at`, `updated_at` (TIMESTAMP) - Audit fields

- **Indexes:**
  - Primary key index on `asin`
  - Index on `brand` for brand-based queries
  - Index on `source_category` for category filtering

#### Fact Table: `price_history`

Time-series fact table storing historical price data:

- **Primary Key:** `id` (SERIAL)
- **Foreign Key:** `asin` → `products.asin` (ON DELETE CASCADE)
- **Attributes:**
  - `asin` (VARCHAR(10)) - Product identifier
  - `date` (DATE) - Price observation date
  - `price_usd` (NUMERIC(10, 2)) - Price in USD
  - `source_category` (VARCHAR(255)) - Denormalized category
  - `brand` (VARCHAR(255)) - Denormalized brand
  - `price_bucket` (VARCHAR(50)) - Price range categorization
  - `created_at` (TIMESTAMP) - Record creation timestamp

- **Constraints:**
  - Unique constraint on (`asin`, `date`) to prevent duplicate entries
  - Foreign key constraint ensures referential integrity

- **Indexes:**
  - Composite index on (`asin`, `date`) for efficient time-series queries
  - Index on `date` for date range filtering
  - Index on `source_category` for category-based aggregations

#### Fact Table: `sales_rank_history`

Time-series fact table storing historical sales rank data:

- **Primary Key:** `id` (SERIAL)
- **Foreign Key:** `asin` → `products.asin` (ON DELETE CASCADE)
- **Attributes:**
  - `asin` (VARCHAR(10)) - Product identifier
  - `date` (DATE) - Rank observation date
  - `sales_rank` (NUMERIC(12, 2)) - Sales rank value
  - `source_category` (VARCHAR(255)) - Denormalized category
  - `brand` (VARCHAR(255)) - Denormalized brand
  - `rank_bucket` (VARCHAR(50)) - Rank range categorization
  - `created_at` (TIMESTAMP) - Record creation timestamp

- **Constraints:**
  - Unique constraint on (`asin`, `date`)
  - Foreign key constraint ensures referential integrity

- **Indexes:**
  - Composite index on (`asin`, `date`) for time-series queries
  - Index on `date` for temporal filtering
  - Index on `sales_rank` for ranking queries

#### Aggregation Table: `product_metrics`

Pre-computed metrics snapshot table for optimized analytical queries:

- **Primary Key:** `id` (SERIAL)
- **Foreign Key:** `asin` → `products.asin` (ON DELETE CASCADE)
- **Attributes:**
  - `asin` (VARCHAR(10)) - Product identifier
  - `source_category` (VARCHAR(255)) - Product category
  - `brand` (VARCHAR(255)) - Product brand
  - `current_price` (NUMERIC(10, 2)) - Latest price
  - `current_rating` (NUMERIC(3, 2)) - Current rating
  - `review_count` (INTEGER) - Total reviews
  - `current_sales_rank` (NUMERIC(12, 2)) - Current rank
  - `monthly_sold` (INTEGER) - Estimated monthly sales
  - `created_at`, `updated_at` (TIMESTAMP) - Audit fields

- **Constraints:**
  - Unique constraint on `asin` ensures one record per product

**Purpose:** This denormalized aggregation table provides fast access to commonly queried metrics without requiring JOINs across multiple tables.

### Optimization Strategies

1. **Composite Indexes:** Indexes on (`asin`, `date`) optimize time-series queries that filter by product and date range
2. **Partial Denormalization:** Category and brand are stored in fact tables to reduce JOIN operations
3. **Aggregation Tables:** Pre-computed metrics eliminate expensive aggregations at query time
4. **Foreign Key Indexes:** Automatic indexes on foreign keys optimize JOIN operations

---

## MongoDB Schema (Document)

### Design Philosophy

The MongoDB schema implements a **denormalized embedded document model** optimized for read-heavy analytical workloads:

- **Data Locality:** Related data embedded in single documents eliminates JOIN overhead
- **Schema Flexibility:** Dynamic schema supports evolving data structures without migrations
- **Read Optimization:** Document structure aligns with common query access patterns
- **Compression:** WiredTiger storage engine provides efficient document storage

### Collection Structure

#### Collection: `products`

Single collection containing all product data with embedded time-series arrays:

**Document Structure:**
```javascript
{
  _id: ObjectId("..."),
  asin: "B0DGHMNQ5Z",                    // Unique identifier
  title: "Product Title",                // Product title
  brand: "Brand Name",                   // Product brand
  source_category: "Electronics",        // Product category
  current_price: 19.9,                   // Latest price
  current_sales_rank: 1.0,               // Current sales rank
  rating: 4.5,                           // Average rating
  review_count: 18819,                   // Total reviews
  
  // Embedded time-series arrays
  price_history: [
    {
      date: ISODate("2025-01-01"),
      price_usd: 19.9,
      source_category: "Electronics",
      brand: "Brand Name",
      price_bucket: "$10-$20"
    },
    // ... additional price records
  ],
  
  sales_rank_history: [
    {
      date: ISODate("2025-01-01"),
      sales_rank: 1.0,
      source_category: "Electronics",
      brand: "Brand Name",
      rank_bucket: "Top 100"
    },
    // ... additional rank records
  ]
}
```

**Indexes:**
- **Unique Index:** `{ asin: 1 }` - Ensures unique product identifiers
- **Compound Indexes:**
  - `{ "price_history.date": 1 }` - Optimizes date filtering on price history
  - `{ "sales_rank_history.date": 1 }` - Optimizes date filtering on sales rank history
- **Single Field Indexes:**
  - `{ brand: 1 }` - Optimizes brand-based queries
  - `{ source_category: 1 }` - Optimizes category-based queries

**Design Rationale:**
- **Embedding Strategy:** Time-series data is embedded within product documents because:
  1. Price and sales rank history are typically accessed together with product information
  2. Average 90 records per product results in manageable document sizes (< 16MB limit)
  3. Eliminates JOIN operations for common query patterns
  4. Provides data locality benefits for read operations

### Optimization Strategies

1. **Embedded Arrays:** Related time-series data stored within product documents reduces query complexity
2. **Compound Indexes on Arrays:** Indexes on embedded array fields enable efficient filtering and aggregation
3. **Selective Denormalization:** Category and brand duplicated in embedded documents to avoid additional lookups
4. **Index Selection:** Strategic indexing balances query performance with write overhead

---

## Design Decisions and Trade-offs

### Normalization vs Denormalization

**PostgreSQL Approach (Normalized):**
- **Advantages:**
  - Eliminates data redundancy
  - Ensures data consistency through foreign key constraints
  - Supports flexible ad-hoc queries through JOINs
  - Optimizes storage for large datasets
  
- **Trade-offs:**
  - Requires JOINs for related data access
  - Schema changes require ALTER TABLE operations (potential downtime)

**MongoDB Approach (Denormalized):**
- **Advantages:**
  - Eliminates JOIN overhead for read operations
  - Provides data locality benefits
  - Schema changes are application-level (no downtime)
  
- **Trade-offs:**
  - Data redundancy increases storage requirements
  - Updates to embedded data require full document replacement
  - Document size limits (16MB) constrain embedding strategy

### Historical Data Tracking

**PostgreSQL:**
- Separate fact tables with `date` columns
- Enables efficient time-series queries using date range filters
- Supports complex temporal aggregations and window functions
- Allows independent indexing and partitioning strategies

**MongoDB:**
- Embedded arrays with date fields within documents
- Requires array unwinding for time-series queries
- Efficient for queries accessing complete product history
- Challenges arise with large arrays and complex temporal queries

### Query Optimization

**PostgreSQL:**
- **Materialized Views:** Pre-computed aggregations for common query patterns
- **Composite Indexes:** Optimize multi-column filters and JOINs
- **Query Planner:** Cost-based optimizer selects efficient execution plans
- **Partitioning:** Table partitioning strategies for very large datasets

**MongoDB:**
- **Aggregation Pipelines:** Flexible pipeline stages for complex transformations
- **Compound Indexes:** Support complex query patterns including array operations
- **Query Planner:** Rule-based optimizer for aggregation pipeline execution
- **Sharding:** Horizontal scaling for datasets exceeding single-node capacity

---

## Schema Evolution Considerations

### PostgreSQL Schema Changes

**Process:**
1. Design schema modification (ALTER TABLE statements)
2. Create migration script
3. Plan downtime window (if required)
4. Execute migration with rollback plan
5. Verify data integrity

**Challenges:**
- ALTER TABLE operations may lock tables (downtime)
- Large tables require careful migration planning
- Foreign key constraints limit modification flexibility

### MongoDB Schema Changes

**Process:**
1. Modify application-level document structure
2. Update application code to handle both old and new formats
3. Migrate existing documents (if necessary) via update operations
4. Remove backward compatibility after migration complete

**Advantages:**
- No downtime required
- Gradual migration possible (supporting both formats)
- Application-level control over migration timing

**Challenges:**
- Application code must handle schema versioning
- Data consistency depends on application logic
- Full document replacement required for embedded array updates

---

## Performance Implications

### Storage Efficiency

- **PostgreSQL:** Normalized schema with foreign keys results in ~3.1 GB storage
- **MongoDB:** Denormalized schema with compression results in ~2.5 GB storage (19% smaller)

### Query Performance

**Simple Reads (Price Trends):**
- **MongoDB:** Faster (1.42x) due to embedded data locality eliminating JOINs
- **PostgreSQL:** Requires JOINs but benefits from optimized query planner

**Complex Analytics (Ranking):**
- **PostgreSQL:** Robust handling of window functions and complex sorting
- **MongoDB:** Memory limitations on complex aggregations require configuration tuning

**Aggregations (Brand Analysis):**
- **PostgreSQL:** Superior performance (4.45x faster) for standard GROUP BY operations
- **MongoDB:** Pipeline overhead impacts aggregation performance

---

## Recommendations

1. **Use PostgreSQL for:**
   - Write-heavy workloads with frequent updates
   - Complex analytical queries requiring window functions
   - Ad-hoc query flexibility requirements
   - Strong consistency requirements

2. **Use MongoDB for:**
   - Read-heavy workloads with specific access patterns
   - Rapid schema evolution requirements
   - Document-centric data models
   - Horizontal scaling requirements

3. **Hybrid Approach:**
   - Consider using both systems: MongoDB for operational data store and PostgreSQL for analytical warehouse
   - ETL pipeline can replicate data from MongoDB to PostgreSQL for analytical processing

