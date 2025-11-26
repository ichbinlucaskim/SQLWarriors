# Setup Guide

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- MongoDB 4.4 or higher
- Keepa API key

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/ichbinlucaskim/SQLWarriors.git
cd SQLWarriors
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and edit with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with:
- PostgreSQL connection details
- MongoDB connection details
- Keepa API key

### 5. Set Up PostgreSQL

```bash
# Create database
createdb amazon_warehouse

# Run schema creation
psql -U postgres -d amazon_warehouse -f postgres/schema/create_tables.sql
psql -U postgres -d amazon_warehouse -f postgres/schema/create_indexes.sql
psql -U postgres -d amazon_warehouse -f postgres/schema/create_views.sql
```

### 6. Set Up MongoDB

```bash
# Start MongoDB (if not running)
mongod

# Create collections and indexes
python mongodb/schema/collections.py
python mongodb/schema/indexes.py
```

### 7. Verify Installation

Run tests to verify everything is set up correctly:

```bash
pytest tests/
```

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Start PostgreSQL
docker run -d --name postgres-warehouse \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=amazon_warehouse \
  -p 5432:5432 \
  postgres:15

# Start MongoDB
docker run -d --name mongodb-warehouse \
  -p 27017:27017 \
  mongo:6
```

## Troubleshooting

### PostgreSQL Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check firewall settings
- Verify credentials in `.env`

### MongoDB Connection Issues
- Verify MongoDB is running: `mongosh --eval "db.adminCommand('ping')"`
- Check connection string format

### Keepa API Issues
- Verify API key is valid
- Check rate limits
- Review API documentation

