-- PostgreSQL Analytical Queries for Benchmarking
-- SQL Warehouse Architect: Kevin Perez
-- 
-- These queries will be used to benchmark PostgreSQL performance

-- Query 1: Pricing trends by category and time
-- Measures: Join performance, aggregation, time-series analysis
SELECT 
    p.category,
    DATE_TRUNC('month', ph.date) as month,
    COUNT(DISTINCT p.asin) as product_count,
    AVG(ph.price) as avg_price,
    STDDEV(ph.price) as price_stddev,
    MIN(ph.price) as min_price,
    MAX(ph.price) as max_price
FROM products p
JOIN price_history ph ON p.asin = ph.asin
WHERE ph.date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY p.category, DATE_TRUNC('month', ph.date)
ORDER BY month DESC, p.category;

-- Query 2: Top products by sales rank or price change
-- Measures: Window functions, sorting, filtering
WITH price_changes AS (
    SELECT 
        p.asin,
        p.title,
        p.brand,
        p.category,
        ph.date,
        ph.price,
        LAG(ph.price) OVER (PARTITION BY ph.asin ORDER BY ph.date) as previous_price,
        (ph.price - LAG(ph.price) OVER (PARTITION BY ph.asin ORDER BY ph.date)) / 
            NULLIF(LAG(ph.price) OVER (PARTITION BY ph.asin ORDER BY ph.date), 0) * 100 as price_change_pct
    FROM products p
    JOIN price_history ph ON p.asin = ph.asin
    WHERE ph.date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    asin,
    title,
    brand,
    category,
    date,
    price,
    price_change_pct
FROM price_changes
WHERE price_change_pct IS NOT NULL
ORDER BY ABS(price_change_pct) DESC
LIMIT 100;

-- Query 3: Aggregated monthly statistics
-- Measures: Complex aggregations, multiple joins
SELECT 
    p.category,
    p.brand,
    DATE_TRUNC('month', ph.date) as month,
    COUNT(DISTINCT p.asin) as unique_products,
    COUNT(ph.id) as price_records,
    AVG(ph.price) as avg_price,
    AVG(ph.offer_count) as avg_offers,
    AVG(r.sales_rank) as avg_sales_rank,
    AVG(r.average_rating) as avg_rating
FROM products p
LEFT JOIN price_history ph ON p.asin = ph.asin
LEFT JOIN reviews r ON p.asin = r.asin AND DATE_TRUNC('month', ph.date) = DATE_TRUNC('month', r.date)
WHERE ph.date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY p.category, p.brand, DATE_TRUNC('month', ph.date)
HAVING COUNT(ph.id) > 0
ORDER BY month DESC, p.category, p.brand;

-- Query 4: Brand performance analysis
-- Measures: Multi-table joins, aggregations, filtering
SELECT 
    p.brand,
    COUNT(DISTINCT p.asin) as product_count,
    AVG(r.sales_rank) as avg_sales_rank,
    AVG(r.average_rating) as avg_rating,
    AVG(ph.price) as avg_price,
    SUM(CASE WHEN r.sales_rank <= 100 THEN 1 ELSE 0 END) as top_100_count
FROM products p
LEFT JOIN reviews r ON p.asin = r.asin
LEFT JOIN price_history ph ON p.asin = ph.asin
WHERE p.brand IS NOT NULL
GROUP BY p.brand
HAVING COUNT(DISTINCT p.asin) >= 10
ORDER BY avg_sales_rank ASC NULLS LAST
LIMIT 50;

-- TODO: Add more complex queries for comprehensive benchmarking

