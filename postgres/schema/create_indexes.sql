-- PostgreSQL Indexes for Query Optimization
-- SQL Warehouse Architect: Kevin Perez

-- Products indexes
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_updated_at ON products(updated_at);

-- Price History indexes
CREATE INDEX IF NOT EXISTS idx_price_history_asin ON price_history(asin);
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(date);
CREATE INDEX IF NOT EXISTS idx_price_history_asin_date ON price_history(asin, date);
CREATE INDEX IF NOT EXISTS idx_price_history_price ON price_history(price);

-- Reviews indexes
CREATE INDEX IF NOT EXISTS idx_reviews_asin ON reviews(asin);
CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(date);
CREATE INDEX IF NOT EXISTS idx_reviews_asin_date ON reviews(asin, date);
CREATE INDEX IF NOT EXISTS idx_reviews_sales_rank ON reviews(sales_rank);

-- Composite indexes for common query patterns
-- TODO: Analyze query patterns and add additional composite indexes

