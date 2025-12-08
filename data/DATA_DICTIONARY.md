# Data Dictionary

**Version:** 1.0  
**Last Updated:** December 2025  
**Data Steward:** SQLWarriors Team

---

## Dataset Overview

### Source Information

- **Data Source:** Keepa Amazon Product Data (Exported/Processed)
- **License & Terms:** Subject to Keepa API Terms of Service
- **Processing:** Pre-processed CSV files for data warehouse benchmarking
- **Context:** Real-world e-commerce analytics dataset representing Amazon product catalog

### Dataset Volume

- **Products:** ~110,000 unique product records
- **Price History:** ~9,899,280 time-series records (average 90 records per product)
- **Sales Rank History:** ~9,899,280 time-series records (average 90 records per product)
- **Product Metrics:** ~110,000 aggregated metric records
- **Total Records:** 20,018,544 rows across all tables
- **Categories:** 11 product categories (Electronics, Home & Kitchen, Clothing, etc.)
- **Time Coverage:** Historical data spanning multiple months with daily granularity

### Data Access & Compliance

**⚠️ IMPORTANT: Data Redistribution Policy**

Due to **Keepa API Terms of Service**, raw CSV data files are **not included** in this repository. The dataset contains proprietary Amazon product information and cannot be redistributed without proper authorization.

**To Run the ETL Pipeline:**

Users must manually obtain and place the following 4 CSV files in the `data/` directory:

1. `products.csv`
2. `price_history.csv`
3. `sales_rank_history.csv`
4. `product_metrics.csv`

These files are excluded from version control via `.gitignore` to ensure compliance with data redistribution policies.

---

## Schema Specifications

### Entity-Relationship Diagram

```
products (Dimension Table)
    │
    ├─── price_history (Fact Table) ──────> FOREIGN KEY: asin
    │
    ├─── sales_rank_history (Fact Table) ──> FOREIGN KEY: asin
    │
    └─── product_metrics (Aggregation Table) -> FOREIGN KEY: asin
```

**Key Relationships:**
- `price_history.asin` → `products.asin` (One-to-Many)
- `sales_rank_history.asin` → `products.asin` (One-to-Many)
- `product_metrics.asin` → `products.asin` (One-to-One)

---

## Table: `products.csv`

**Entity Type:** Dimension Table  
**Primary Key:** `asin`  
**Record Count:** ~110,000  
**File Size:** ~22 MB  
**Description:** Master product catalog containing unique product identifiers and current state attributes.

| Field Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `asin` | VARCHAR(10) | No | Amazon Standard Identification Number (Primary Key). Unique 10-character alphanumeric identifier for each product. Format: `B0XXXXXXXX` or `XXXXXXXXXX` |
| `title` | TEXT | Yes | Full product title as displayed on Amazon. May contain special characters, HTML entities, and product descriptions. |
| `brand` | VARCHAR(255) | Yes | Product manufacturer or brand name. Examples: "Apple", "Samsung", "Generic". May be NULL for unbranded products. |
| `source_category` | VARCHAR(255) | Yes | Primary product category classification. Examples: "Electronics", "Home & Kitchen", "Clothing, Shoes & Jewelry". Used for categorical analysis. |
| `current_price` | NUMERIC(10, 2) | Yes | Current product price in USD at time of export. Represents the lowest available price including shipping. Range: $0.01 - $999,999.99 |
| `current_sales_rank` | NUMERIC(12, 2) | Yes | Current Amazon Best Sellers Rank in primary category. Lower values indicate higher sales volume. Range: 1 - 10,000,000+ |
| `rating` | NUMERIC(3, 2) | Yes | Average customer rating on a 5.0 scale. Derived from customer reviews. Range: 0.00 - 5.00. NULL if no reviews exist. |
| `review_count` | INTEGER | Yes | Total number of customer reviews received. Integer value, zero or positive. May be 0 for new products. |

**Data Quality Notes:**
- `asin` values are unique and non-null (primary key constraint)
- `current_price` values are positive or NULL (negative prices filtered during processing)
- `current_sales_rank` of 1 indicates best-selling product in category
- `rating` and `review_count` may both be NULL if product has no reviews

---

## Table: `price_history.csv`

**Entity Type:** Fact Table (Time-Series)  
**Primary Key:** Composite (`asin`, `date`)  
**Foreign Key:** `asin` → `products.asin`  
**Record Count:** ~9,899,280  
**File Size:** ~550 MB  
**Description:** Daily price observations for products over time. Enables price trend analysis, volatility calculation, and temporal price comparisons.

| Field Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `asin` | VARCHAR(10) | No | Foreign key reference to `products.asin`. Links price record to product master data. |
| `date` | DATE | No | Date of price observation in ISO format (YYYY-MM-DD). Represents daily price snapshot at time of data collection. |
| `price_usd` | NUMERIC(10, 2) | Yes | Product price in USD on the specified date. Includes lowest available price with shipping. NULL indicates price was unavailable or product was out of stock. |
| `source_category` | VARCHAR(255) | Yes | Denormalized category field for query optimization. Duplicated from `products` table to avoid JOINs in analytical queries. |
| `brand` | VARCHAR(255) | Yes | Denormalized brand field for query optimization. Duplicated from `products` table for efficient brand-based aggregations. |
| `price_bucket` | VARCHAR(50) | Yes | Price range categorization for analytical grouping. Examples: "$0-$10", "$10-$20", "$20-$50", "$50-$100", "$100+". Used for price segment analysis. |

**Unique Constraint:** (`asin`, `date`) - Each product can have only one price record per day.

**Data Quality Notes:**
- Time-series data may include synthetic gaps (missing dates) to test query robustness
- `price_usd` values are positive when present (NULL represents missing/out-of-stock)
- Date range typically spans 90 days per product (average 90 records per ASIN)
- Price values may exhibit random walk patterns for synthetic data generation
- Denormalized fields (`source_category`, `brand`) may be NULL if parent product record is incomplete

---

## Table: `sales_rank_history.csv`

**Entity Type:** Fact Table (Time-Series)  
**Primary Key:** Composite (`asin`, `date`)  
**Foreign Key:** `asin` → `products.asin`  
**Record Count:** ~9,899,280  
**File Size:** ~565 MB  
**Description:** Daily sales rank observations tracking product popularity and sales performance over time. Enables trend analysis, ranking comparisons, and sales velocity calculations.

| Field Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `asin` | VARCHAR(10) | No | Foreign key reference to `products.asin`. Links sales rank record to product master data. |
| `date` | DATE | No | Date of sales rank observation in ISO format (YYYY-MM-DD). Daily snapshot of product's ranking position. |
| `sales_rank` | NUMERIC(12, 2) | Yes | Amazon Best Sellers Rank in primary category on the specified date. Lower values indicate higher sales volume. Range: 1 (best seller) to 10,000,000+ (low volume). NULL indicates rank was unavailable. |
| `source_category` | VARCHAR(255) | Yes | Denormalized category field for query optimization. Enables category-based ranking analysis without JOINs. |
| `brand` | VARCHAR(255) | Yes | Denormalized brand field for query optimization. Facilitates brand performance comparisons. |
| `rank_bucket` | VARCHAR(50) | Yes | Sales rank range categorization for analytical grouping. Examples: "Top 100", "Top 1000", "Top 10000", "10000+". Used for rank segment analysis. |

**Unique Constraint:** (`asin`, `date`) - Each product can have only one sales rank record per day.

**Data Quality Notes:**
- Time-series data may include synthetic gaps (missing dates) for robustness testing
- `sales_rank` values are positive integers when present (lower is better)
- Rank of 1 indicates best-selling product in category on that date
- Rank values may exhibit volatility and random walk patterns in synthetic data
- NULL values indicate rank was unavailable or product was not ranked
- Average of 90 records per product provides sufficient granularity for trend analysis

---

## Table: `product_metrics.csv`

**Entity Type:** Aggregation Table  
**Primary Key:** `asin`  
**Foreign Key:** `asin` → `products.asin`  
**Record Count:** ~110,000  
**File Size:** ~6.5 MB  
**Description:** Pre-computed aggregated metrics snapshot for each product. Provides optimized access to commonly queried performance indicators without real-time aggregation.

| Field Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `asin` | VARCHAR(10) | No | Foreign key reference to `products.asin`. One-to-one relationship with products table. |
| `source_category` | VARCHAR(255) | Yes | Denormalized category field for analytical queries. Duplicated for query performance. |
| `brand` | VARCHAR(255) | Yes | Denormalized brand field for brand analysis. Enables efficient brand aggregations. |
| `current_price` | NUMERIC(10, 2) | Yes | Latest price value from price history. Derived from most recent `price_history` record. |
| `current_rating` | NUMERIC(3, 2) | Yes | Latest average rating. Synced with `products.rating` field. |
| `review_count` | INTEGER | Yes | Total review count. Synced with `products.review_count` field. |
| `current_sales_rank` | NUMERIC(12, 2) | Yes | Latest sales rank from sales rank history. Derived from most recent `sales_rank_history` record. |
| `monthly_sold` | INTEGER | Yes | Estimated monthly sales units. Calculated based on sales rank algorithms. Range: 0 - 1,000,000+. NULL if calculation unavailable. |

**Unique Constraint:** `asin` - One metric record per product.

**Data Quality Notes:**
- All aggregated fields are derived from source tables (`products`, `price_history`, `sales_rank_history`)
- `monthly_sold` is an estimated value based on sales rank algorithms and may not reflect actual sales
- Denormalized fields (`source_category`, `brand`) match parent product values
- This table serves as a materialized view for query optimization
- Values should be refreshed periodically to maintain accuracy

---

## Data Quality & Processing Rules

### Data Cleaning Rules

1. **Price Validation:**
   - Negative prices are filtered out during ETL processing
   - Prices exceeding reasonable thresholds (> $1,000,000) are flagged but retained
   - NULL prices represent missing or unavailable data (out of stock)

2. **Sales Rank Validation:**
   - Negative ranks are invalid and filtered out
   - Ranks are positive integers; fractional values (stored as NUMERIC) are rounded
   - NULL ranks indicate product was not ranked in category

3. **Rating Validation:**
   - Ratings are constrained to range 0.00 - 5.00
   - Values outside this range are normalized or set to NULL
   - `review_count` of 0 is valid (product has no reviews)

4. **Date Validation:**
   - All dates are in ISO format (YYYY-MM-DD)
   - Future dates are filtered out (data represents historical observations)
   - Date ranges per product may vary (average 90 days of coverage)

5. **ASIN Validation:**
   - ASIN must be exactly 10 characters (alphanumeric)
   - Invalid ASIN formats are rejected during ETL
   - ASIN serves as primary key and foreign key throughout schema

### Synthetic Data Characteristics

For benchmarking and testing purposes, the dataset may include:

- **Synthetic Gaps:** Missing dates in time-series to test query robustness
- **Random Walk Patterns:** Price and sales rank values may exhibit simulated volatility
- **Synthetic Products:** Additional product records generated for scale testing

These synthetic elements are designed to test system robustness and do not represent actual Amazon product data.

### Data Completeness

- **Products Table:** 100% coverage (all ASINs present)
- **Price History:** Average 90 records per product (coverage varies by product)
- **Sales Rank History:** Average 90 records per product (may have gaps)
- **Product Metrics:** 100% coverage (one record per product)

### Referential Integrity

- All foreign key relationships are enforced at the database level
- `price_history.asin` must exist in `products.asin`
- `sales_rank_history.asin` must exist in `products.asin`
- `product_metrics.asin` must exist in `products.asin`
- Cascading deletes ensure no orphaned records in fact tables

---

## Usage Examples

### Loading Data into PostgreSQL

```sql
-- Products are loaded first (dimension table)
COPY products FROM 'data/products.csv' WITH (FORMAT csv, HEADER);

-- Fact tables loaded after products (foreign key dependency)
COPY price_history FROM 'data/price_history.csv' WITH (FORMAT csv, HEADER);
COPY sales_rank_history FROM 'data/sales_rank_history.csv' WITH (FORMAT csv, HEADER);
COPY product_metrics FROM 'data/product_metrics.csv' WITH (FORMAT csv, HEADER);
```

### Loading Data into MongoDB

```python
# Products collection with embedded arrays
# Price and sales rank history are embedded within product documents
# Requires pre-aggregation in Python before insertion
```

---

## Field Definitions Reference

### ASIN (Amazon Standard Identification Number)

- **Format:** 10-character alphanumeric string
- **Examples:** `B0DGHMNQ5Z`, `1234567890`
- **Uniqueness:** Globally unique product identifier
- **Usage:** Primary key and foreign key throughout schema

### Price Bucket Categories

- `"$0-$10"`: Price range 0.00 to 9.99
- `"$10-$20"`: Price range 10.00 to 19.99
- `"$20-$50"`: Price range 20.00 to 49.99
- `"$50-$100"`: Price range 50.00 to 99.99
- `"$100+"`: Price range 100.00 and above
- `NULL`: Price unavailable

### Rank Bucket Categories

- `"Top 100"`: Sales rank 1-100
- `"Top 1000"`: Sales rank 101-1000
- `"Top 10000"`: Sales rank 1001-10000
- `"10000+"`: Sales rank 10001 and above
- `NULL`: Rank unavailable

### Source Category Values

Common categories include:
- `"Electronics"`
- `"Home & Kitchen"`
- `"Clothing, Shoes & Jewelry"`
- `"Sports & Outdoors"`
- `"Books"`
- `"Toys & Games"`
- `"Beauty & Personal Care"`
- `"Health & Household"`
- `"Pet Supplies"`
- `"Office Products"`
- `"Automotive"`

---

## Data Lineage

```
Keepa API (Source)
    ↓
Raw Data Extraction
    ↓
Data Transformation & Cleaning
    ├─── Price validation
    ├─── Rank normalization
    ├─── Category standardization
    └─── Date formatting
    ↓
CSV Export
    ├─── products.csv
    ├─── price_history.csv
    ├─── sales_rank_history.csv
    └─── product_metrics.csv
    ↓
ETL Pipeline
    ├─── PostgreSQL (Normalized Schema)
    └─── MongoDB (Denormalized Schema)
```

---

## Contact & Support

For questions regarding:
- **Data Structure:** Refer to this document
- **Data Access:** Contact project maintainers (see README.md)
- **Keepa API:** Refer to official Keepa API documentation
- **Schema Design:** See `docs/schema_design.md`

---

**Document Status:** Current  
**Maintained By:** SQLWarriors Data Engineering Team  
**Compliance:** Keepa API Terms of Service

