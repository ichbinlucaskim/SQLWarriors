# MongoDB vs PostgreSQL Schema Comparison

## Why MongoDB ERD Shows Only 3 "Tables"?

### Key Difference: **Actual Collections vs Conceptual Entities**

The MongoDB ERD shows 3 entities, but **MongoDB actually has only 1 collection** (`products`). The other two are **embedded subdocuments**, not separate collections.

---

## PostgreSQL: 4 Actual Tables (Normalized Star Schema)

```
┌─────────────────┐
│   products      │  ← Dimension Table (110K rows)
└────────┬────────┘
         │
    ┌────┴───────────────────┐
    │                        │
┌───▼──────────────┐  ┌──────▼──────────────┐
│ price_history    │  │ sales_rank_history  │  ← Fact Tables
│ (9.9M rows)      │  │ (9.9M rows)         │
└──────────────────┘  └─────────────────────┘
    │
┌───▼──────────────┐
│ product_metrics  │  ← Aggregation Table (110K rows)
└──────────────────┘

Total: 4 separate physical tables
```

**Characteristics:**
- ✅ Each table is stored separately
- ✅ Relationships maintained via foreign keys (`asin`)
- ✅ JOINs required to combine data
- ✅ Normalized: No data duplication in base tables

---

## MongoDB: 1 Actual Collection (Embedded Document Model)

```
┌──────────────────────────────────────────────┐
│           products (Collection)              │
│  ─────────────────────────────────────────  │
│  {                                          │
│    _id: ObjectId(...),                      │
│    asin: "B08XXX",                          │
│    title: "...",                            │
│    brand: "...",                            │
│                                             │
│    price_history: [          ← EMBEDDED     │
│      {date: ..., price: ...},  ARRAY        │
│      {date: ..., price: ...},               │
│      ... (~90 records)                      │
│    ],                                       │
│                                             │
│    sales_rank_history: [    ← EMBEDDED     │
│      {date: ..., rank: ...},   ARRAY        │
│      {date: ..., rank: ...},                │
│      ... (~90 records)                      │
│    ]                                        │
│  }                                          │
│  ─────────────────────────────────────────  │
│  (110K documents, each with embedded arrays)│
└──────────────────────────────────────────────┘

Total: 1 physical collection
```

**ERD Representation:**
The ERD shows 3 entities for **conceptual clarity**, but they're all in one collection:
- `PRODUCTS` = The actual MongoDB collection
- `PRICE_HISTORY_ENTRY` = Embedded array within each product document
- `SALES_RANK_HISTORY_ENTRY` = Embedded array within each product document

**Characteristics:**
- ✅ All data stored in a single collection
- ✅ Related data embedded as arrays (no JOINs needed)
- ✅ Denormalized: Category/brand duplicated in embedded arrays
- ✅ Single document read gets all related data

---

## Visual Comparison

### PostgreSQL Query Pattern

```sql
-- Need to JOIN multiple tables
SELECT p.title, ph.price, srh.sales_rank
FROM products p
JOIN price_history ph ON p.asin = ph.asin
JOIN sales_rank_history srh ON p.asin = srh.asin
WHERE p.asin = 'B08XXX';
```

**Data Access:**
1. Read `products` table → Get product info
2. JOIN `price_history` table → Get price data
3. JOIN `sales_rank_history` table → Get rank data
4. Combine results

### MongoDB Query Pattern

```javascript
// Single collection query - no JOINs needed
db.products.findOne({ asin: "B08XXX" })
```

**Data Access:**
1. Read one document from `products` collection
2. All data (product info, price history, rank history) in one document
3. No JOIN operations

---

## Why This Design Choice?

### MongoDB: Embedded Model Benefits

1. **Data Locality**: Related data stored together → faster reads
2. **No JOINs**: Single document read gets everything
3. **Read Optimization**: Perfect for read-heavy workloads
4. **Simpler Queries**: No complex JOIN operations

**Trade-offs:**
- Document size limit (16MB per document)
- Update operations require replacing entire document
- Data redundancy (category/brand duplicated in arrays)

### PostgreSQL: Normalized Model Benefits

1. **Data Integrity**: Foreign keys ensure referential integrity
2. **Storage Efficiency**: No data duplication (in base tables)
3. **Flexible Queries**: JOIN any combination of tables
4. **Scalability**: Can partition large fact tables independently

**Trade-offs:**
- JOIN overhead for related data access
- More complex queries for common access patterns
- Schema changes require migrations

---

## Summary

| Aspect | PostgreSQL | MongoDB |
|--------|-----------|---------|
| **Actual Tables/Collections** | 4 tables | 1 collection |
| **Data Storage** | Normalized (separate tables) | Denormalized (embedded arrays) |
| **Relationships** | Foreign keys (JOINs) | Embedded documents (no JOINs) |
| **Query Pattern** | JOIN multiple tables | Read single document |
| **ERD Entities Shown** | 4 (actual tables) | 3 (conceptual: 1 collection + 2 embedded types) |

**Key Takeaway:** MongoDB ERD shows 3 entities for conceptual clarity, but all data is stored in **1 collection** with embedded arrays. This is the fundamental difference between normalized relational (PostgreSQL) and denormalized document (MongoDB) models.

