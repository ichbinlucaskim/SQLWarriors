-- PostgreSQL Data Warehouse Schema for CSV Import
-- SQL Warehouse Architect: Kevin Perez
-- 
-- This schema implements a normalized star schema design for Amazon product data
-- Tables: products, price_history, sales_rank_history, product_metrics
-- Designed for high-speed CSV import using COPY command

-- Drop existing tables if they exist (for clean reload)
DROP TABLE IF EXISTS product_metrics CASCADE;
DROP TABLE IF EXISTS sales_rank_history CASCADE;
DROP TABLE IF EXISTS price_history CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Products Dimension Table (Primary Table)
CREATE TABLE products (
    asin VARCHAR(10) PRIMARY KEY,
    title TEXT,
    brand VARCHAR(255),
    source_category VARCHAR(255),
    current_price NUMERIC(10, 2),
    current_sales_rank NUMERIC(12, 2),
    rating NUMERIC(3, 2),
    review_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price History Fact Table
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(10) NOT NULL REFERENCES products(asin) ON DELETE CASCADE,
    date DATE NOT NULL,
    price_usd NUMERIC(10, 2),
    source_category VARCHAR(255),
    brand VARCHAR(255),
    price_bucket VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asin, date)
);

-- Sales Rank History Fact Table
CREATE TABLE sales_rank_history (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(10) NOT NULL REFERENCES products(asin) ON DELETE CASCADE,
    date DATE NOT NULL,
    sales_rank NUMERIC(12, 2),
    source_category VARCHAR(255),
    brand VARCHAR(255),
    rank_bucket VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asin, date)
);

-- Product Metrics Table (Aggregated metrics)
CREATE TABLE product_metrics (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(10) NOT NULL REFERENCES products(asin) ON DELETE CASCADE,
    source_category VARCHAR(255),
    brand VARCHAR(255),
    current_price NUMERIC(10, 2),
    current_rating NUMERIC(3, 2),
    review_count INTEGER,
    current_sales_rank NUMERIC(12, 2),
    monthly_sold INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asin)
);

-- Add comments for documentation
COMMENT ON TABLE products IS 'Product master data dimension table';
COMMENT ON TABLE price_history IS 'Time-series price history fact table';
COMMENT ON TABLE sales_rank_history IS 'Time-series sales rank history fact table';
COMMENT ON TABLE product_metrics IS 'Aggregated product metrics snapshot';

-- Indexes will be created after data load for better performance
-- See create_indexes.sql for index creation

