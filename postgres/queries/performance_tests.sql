-- PostgreSQL Performance Test Queries
-- SQL Warehouse Architect: Kevin Perez
-- 
-- Queries to measure query execution time and resource usage

-- Enable query timing
\timing on

-- Test 1: Simple SELECT (baseline)
SELECT COUNT(*) FROM products;

-- Test 2: JOIN performance
SELECT COUNT(*) 
FROM products p
JOIN price_history ph ON p.asin = ph.asin;

-- Test 3: Aggregation performance
SELECT category, COUNT(*) as count
FROM products
GROUP BY category;

-- Test 4: Window function performance
SELECT 
    asin,
    price,
    AVG(price) OVER (PARTITION BY asin ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg
FROM price_history
LIMIT 10000;

-- Test 5: Complex analytical query
-- (Use queries from analytical_queries.sql with EXPLAIN ANALYZE)

-- TODO: Add EXPLAIN ANALYZE for all queries
-- TODO: Measure execution time for each query
-- TODO: Document index usage and query plans

