# PostgreSQL Schema ERD

## Star Schema Design (Normalized Relational Model)

> **Note:** GitHub automatically renders the Mermaid diagram below. Image versions (PNG/SVG) are also available in `docs/images/` directory.

<!-- ![PostgreSQL ERD](images/postgresql_erd.png) -->

### Interactive Diagram (GitHub Renders Automatically)

```mermaid
erDiagram
    PRODUCTS {
        varchar asin PK "Primary Key"
        text title
        varchar brand
        varchar source_category
        numeric current_price
        numeric current_sales_rank
        numeric rating
        int review_count
        timestamp created_at
        timestamp updated_at
    }
    
    PRICE_HISTORY {
        serial id PK "Primary Key"
        varchar asin FK "Foreign Key"
        date date
        numeric price_usd
        varchar source_category "Denormalized"
        varchar brand "Denormalized"
        varchar price_bucket
        timestamp created_at
    }
    
    SALES_RANK_HISTORY {
        serial id PK "Primary Key"
        varchar asin FK "Foreign Key"
        date date
        numeric sales_rank
        varchar source_category "Denormalized"
        varchar brand "Denormalized"
        varchar rank_bucket
        timestamp created_at
    }
    
    PRODUCT_METRICS {
        serial id PK "Primary Key"
        varchar asin FK "Foreign Key (Unique)"
        varchar source_category
        varchar brand
        numeric current_price
        numeric current_rating
        int review_count
        numeric current_sales_rank
        int monthly_sold
        timestamp created_at
        timestamp updated_at
    }
    
    PRODUCTS ||--o{ PRICE_HISTORY : "has many (1:N)"
    PRODUCTS ||--o{ SALES_RANK_HISTORY : "has many (1:N)"
    PRODUCTS ||--|| PRODUCT_METRICS : "has one (1:1)"
```

## Schema Notes

### Design Pattern: Normalized Star Schema

- **Dimension Table**: `products` - Master product data
- **Fact Tables**: `price_history`, `sales_rank_history` - Time-series transactional data
- **Aggregation Table**: `product_metrics` - Pre-computed metrics for query optimization
- **Referential Integrity**: All foreign keys enforce `ON DELETE CASCADE`

### Relationship Types

- **PRODUCTS → PRICE_HISTORY**: 1:N (One-to-Many)
  - One product can have multiple price history records
  - Foreign Key: `price_history.asin` → `products.asin`
  - Unique constraint: `(asin, date)` prevents duplicate entries
  - Average ~90 records per product

- **PRODUCTS → SALES_RANK_HISTORY**: 1:N (One-to-Many)
  - One product can have multiple sales rank history records
  - Foreign Key: `sales_rank_history.asin` → `products.asin`
  - Unique constraint: `(asin, date)` prevents duplicate entries
  - Average ~90 records per product

- **PRODUCTS → PRODUCT_METRICS**: 1:1 (One-to-One)
  - One product has exactly one metrics snapshot
  - Foreign Key: `product_metrics.asin` → `products.asin`
  - Unique constraint on `asin` ensures one-to-one relationship
  - Pre-aggregated for fast analytical queries

### Indexes

**Products Table:**
- Primary Key: `asin`
- Index on `brand`
- Index on `source_category`
- Index on `updated_at`

**Price History Table:**
- Primary Key: `id`
- Foreign Key Index: `asin`
- Index on `date`
- Composite Index: `(asin, date)`
- Index on `price_usd`

**Sales Rank History Table:**
- Primary Key: `id`
- Foreign Key Index: `asin`
- Index on `date`
- Composite Index: `(asin, date)`
- Index on `sales_rank`

**Product Metrics Table:**
- Primary Key: `id`
- Foreign Key Index: `asin` (unique)

### Key Characteristics

1. **Normalization**: Separate tables eliminate data redundancy
2. **Referential Integrity**: Foreign key constraints ensure data consistency
3. **Denormalization**: Category and brand duplicated in fact tables for query optimization
4. **Time-Series Optimization**: Composite indexes on `(asin, date)` optimize time-series queries
5. **Query Performance**: Aggregation table eliminates expensive JOINs for common metrics

