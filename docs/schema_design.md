# Schema Design Documentation

## PostgreSQL Schema (Relational)

### Design Philosophy
- Normalized star schema
- Separate fact and dimension tables
- Foreign key relationships for data integrity
- Indexes optimized for analytical queries

### Tables

#### Products (Dimension Table)
- Primary key: `asin`
- Stores product master data
- Indexed on: brand, category, updated_at

#### Price History (Fact Table)
- Primary key: `id` (serial)
- Foreign key: `asin` → products
- Time-series data with unique constraint on (asin, date)
- Indexed on: asin, date, price

#### Reviews (Fact Table)
- Primary key: `id` (serial)
- Foreign key: `asin` → products
- Sales rank and review metrics
- Indexed on: asin, date, sales_rank

### Views
- `product_price_trends`: Price changes over time
- `top_products_by_rank`: Top products by sales rank
- `monthly_category_stats`: Aggregated monthly statistics

## MongoDB Schema (Document)

### Design Philosophy
- Embedded documents for frequently accessed data
- Flexible schema for evolving data structures
- Optimized for read-heavy analytical workloads

### Collections

#### Products Collection
- Document structure with embedded arrays:
  - `price_history[]`: Embedded price records
  - `reviews[]`: Embedded review/sales records
- Indexes:
  - `asin` (unique)
  - `brand`, `category`
  - `price_history.date`, `reviews.date`
  - Text index on `title` and `description`

### Schema Evolution Considerations
- PostgreSQL: Requires ALTER TABLE (may cause downtime)
- MongoDB: Schema changes are application-level (no downtime)

## Design Decisions

### Normalization vs Denormalization
- **PostgreSQL**: Fully normalized for data integrity and storage efficiency
- **MongoDB**: Denormalized with embedded documents for query performance

### Historical Data Tracking
- **PostgreSQL**: Separate fact tables with date columns
- **MongoDB**: Embedded arrays with date fields

### Query Optimization
- **PostgreSQL**: Materialized views, composite indexes
- **MongoDB**: Aggregation pipelines, compound indexes

