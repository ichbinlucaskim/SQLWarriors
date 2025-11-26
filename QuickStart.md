# Quick Start Guide

## Quick Start (5-Minute Setup)

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables Configuration

```bash
# Create .env file
cp .env.example .env

# Edit .env file (open with editor and modify)
# - PostgreSQL connection information
# - MongoDB connection information  
# - Keepa API key
```

### 3. Database Setup

#### PostgreSQL
```bash
# Create database
createdb amazon_warehouse

# Create schema
psql -U postgres -d amazon_warehouse -f postgres/schema/create_tables.sql
psql -U postgres -d amazon_warehouse -f postgres/schema/create_indexes.sql
psql -U postgres -d amazon_warehouse -f postgres/schema/create_views.sql
```

#### MongoDB
```bash
# Start MongoDB (skip if already running)
mongod

# Create collections and indexes
python mongodb/schema/collections.py
python mongodb/schema/indexes.py
```

### 4. Run Tests

```bash
# Basic tests
pytest tests/

# ETL pipeline test (small dataset)
python -c "from etl.pipeline import ETLPipeline; pipeline = ETLPipeline(); pipeline.run_full_load(target_count=100)"
```

## Role-Based Getting Started Guide

### Philip (ETL Lead)

1. **Verify Keepa API Key**
   ```bash
   # Check KEEPA_API_KEY in .env file
   ```

2. **Test API Connection**
   ```python
   from etl.keepa_client import KeepaClient
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   client = KeepaClient(os.getenv('KEEPA_API_KEY'))
   # Write API test code
   ```

3. **Start Working**
   - Begin with implementing `etl/keepa_client.py`
   - Reference Keepa API documentation: https://keepa.com/#!api

### Kevin (PostgreSQL Architect)

1. **Verify PostgreSQL Connection**
   ```python
   from postgres.config import get_connection_string
   from sqlalchemy import create_engine
   
   engine = create_engine(get_connection_string())
   # Test connection
   ```

2. **Review and Modify Schema**
   - Review `postgres/schema/create_tables.sql`
   - Add/modify fields as needed

3. **Start Working**
   - Complete schema → Design indexes → Write queries

### Lucas (MongoDB Architect)

1. **Verify MongoDB Connection**
   ```python
   from mongodb.config import get_database
   
   db = get_database()
   # Test connection
   print(db.list_collection_names())
   ```

2. **Design Schema**
   - Review `mongodb/schema/collections.py`
   - Decide on Embedding vs Referencing strategy

3. **Start Working**
   - Define collection structure → Create indexes → Write aggregation pipelines

## Common Workflow

### Data Loading
```bash
# Full load (100,000 products)
python etl/pipeline.py

# Or in Python
from etl.pipeline import ETLPipeline
pipeline = ETLPipeline()
pipeline.run_full_load(target_count=100000)
```

### Run Benchmarks
```bash
# Load performance benchmark
python benchmarks/load_performance.py

# Query performance benchmark
python benchmarks/query_performance.py
```

### Using Jupyter Notebook
```bash
# Start Jupyter
jupyter notebook

# Or JupyterLab
jupyter lab
```

## Troubleshooting

### PostgreSQL Connection Error
- Check if PostgreSQL is running: `pg_isready`
- Verify connection information in `.env` file
- Check firewall settings

### MongoDB Connection Error
- Check if MongoDB is running: `mongosh --eval "db.adminCommand('ping')"`
- Verify connection string format

### Keepa API Error
- Verify API key validity
- Check rate limit (1 request per second)
- Review API documentation

## Next Steps

1. Start implementing files according to your role
2. Check tasks in `TASKS.md`
3. Regular code reviews and integration testing
4. Document benchmark results

## Useful Commands

```bash
# Check project structure
tree -L 2  # if tree is installed
find . -type f -name "*.py" | head -20

# Code formatting (optional)
black .  # if black is installed

# Linting (optional)
flake8 .  # if flake8 is installed
```

## Help

- Project README: `README.md`
- Detailed task list: `TASKS.md`
- Setup guide: `docs/setup_guide.md`
- Schema design: `docs/schema_design.md`
