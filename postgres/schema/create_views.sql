-- PostgreSQL Analytical Views
-- SQL Warehouse Architect: Kevin Perez
-- 
-- Materialized views for common analytical queries

-- Product Price Trends View
CREATE OR REPLACE VIEW product_price_trends AS
SELECT 
    p.asin,
    p.title,
    p.brand,
    p.category,
    ph.date,
    ph.price,
    ph.offer_count,
    LAG(ph.price) OVER (PARTITION BY ph.asin ORDER BY ph.date) as previous_price,
    ph.price - LAG(ph.price) OVER (PARTITION BY ph.asin ORDER BY ph.date) as price_change
FROM products p
JOIN price_history ph ON p.asin = ph.asin
ORDER BY p.asin, ph.date;

-- Top Products by Sales Rank View
CREATE OR REPLACE VIEW top_products_by_rank AS
SELECT 
    p.asin,
    p.title,
    p.brand,
    p.category,
    r.date,
    r.sales_rank,
    r.review_count,
    r.average_rating
FROM products p
JOIN reviews r ON p.asin = r.asin
WHERE r.sales_rank IS NOT NULL
ORDER BY r.sales_rank ASC, r.date DESC;

-- Monthly Category Statistics View
CREATE OR REPLACE VIEW monthly_category_stats AS
SELECT 
    p.category,
    DATE_TRUNC('month', ph.date) as month,
    COUNT(DISTINCT p.asin) as product_count,
    AVG(ph.price) as avg_price,
    MIN(ph.price) as min_price,
    MAX(ph.price) as max_price,
    AVG(ph.offer_count) as avg_offer_count
FROM products p
JOIN price_history ph ON p.asin = ph.asin
GROUP BY p.category, DATE_TRUNC('month', ph.date)
ORDER BY month DESC, p.category;

-- TODO: Create materialized views for better performance on large datasets
-- CREATE MATERIALIZED VIEW monthly_category_stats_mv AS ...

