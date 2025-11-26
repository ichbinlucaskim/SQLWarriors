-- PostgreSQL Data Warehouse Schema
-- SQL Warehouse Architect: Kevin Perez
-- 
-- This schema implements a normalized star schema design for Amazon product data
-- Core tables: products, price_history, reviews

-- Products Dimension Table
CREATE TABLE IF NOT EXISTS products (
    asin VARCHAR(10) PRIMARY KEY,
    title TEXT NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(255),
    features TEXT[],
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price History Fact Table
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(10) NOT NULL REFERENCES products(asin) ON DELETE CASCADE,
    date DATE NOT NULL,
    price DECIMAL(10, 2),
    offer_count INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asin, date)
);

-- Reviews/Sales Fact Table
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(10) NOT NULL REFERENCES products(asin) ON DELETE CASCADE,
    date DATE NOT NULL,
    sales_rank INTEGER,
    review_count INTEGER,
    average_rating DECIMAL(3, 2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asin, date)
);

-- TODO: Add additional indexes for query optimization
-- TODO: Add constraints and validations
-- TODO: Consider partitioning for large tables

