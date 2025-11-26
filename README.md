# SQLWarriors - Comparative Data Warehouse Design

**Comparative Data Warehouse Design and Evaluation using Live Amazon Product Data: PostgreSQL vs. MongoDB**

Team Members:
- **Philip Anand** - ETL Lead
- **Kevin Perez** - SQL Warehouse Architect  
- **Lucas Kim** - NoSQL Warehouse Architect / Documentation

## Project Overview

This project compares PostgreSQL and MongoDB for data warehouse implementations using real Amazon product data from the Keepa API. We evaluate schema design, ingestion throughput, analytical query performance, and operational complexity across both database paradigms.

## Research Questions

1. How does each database manage schema design, ingestion throughput, and analytical queries with rapidly changing product, price, and sales data?
2. What modeling decisions and challenges arise when implementing data warehouse concepts (star schemas, historical tracking) in document-oriented versus relational paradigms?
3. Where does each platform excel or face limitations in bulk import speed, query performance, schema evolution, and developer experience?

## Dataset

- **Source**: Keepa API (Amazon product information, pricing trends, sales rankings)
- **Target**: 100,000+ unique product listings
- **Data Types**:
  - Products: ASIN, title, category, brand, features, descriptions
  - Price History: Daily price records, offer counts, timestamps
  - Sales/Reviews: Sales rank and review statistics

## Project Structure

```
SQLWarriors/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
│
├── etl/                      # ETL Pipeline (Philip)
│   ├── __init__.py
│   ├── keepa_client.py      # Keepa API client wrapper
│   ├── extractor.py         # Data extraction logic
│   ├── transformer.py       # Data cleaning and transformation
│   ├── loader_postgres.py   # PostgreSQL data loader
│   ├── loader_mongodb.py    # MongoDB data loader
│   ├── pipeline.py          # Main ETL orchestration
│   └── utils.py             # Helper functions
│
├── postgres/                 # PostgreSQL Warehouse (Kevin)
│   ├── schema/
│   │   ├── create_tables.sql    # Table definitions
│   │   ├── create_indexes.sql   # Index creation
│   │   └── create_views.sql     # Analytical views
│   ├── queries/
│   │   ├── analytical_queries.sql    # Benchmark queries
│   │   └── performance_tests.sql    # Performance evaluation
│   └── config.py            # PostgreSQL connection config
│
├── mongodb/                  # MongoDB Warehouse (Lucas)
│   ├── schema/
│   │   ├── collections.py       # Collection definitions
│   │   └── indexes.py            # Index creation
│   ├── queries/
│   │   ├── aggregation_pipelines.py  # Analytical queries
│   │   └── performance_tests.py       # Performance evaluation
│   └── config.py            # MongoDB connection config
│
├── benchmarks/               # Benchmarking Scripts
│   ├── __init__.py
│   ├── load_performance.py  # Bulk/incremental load benchmarks
│   ├── query_performance.py # Query latency benchmarks
│   ├── resource_usage.py    # CPU/memory/storage monitoring
│   └── schema_evolution.py  # Schema change evaluation
│
├── notebooks/                # Jupyter Notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_etl_pipeline.ipynb
│   ├── 03_postgres_analysis.ipynb
│   ├── 04_mongodb_analysis.ipynb
│   ├── 05_comparative_analysis.ipynb
│   └── 06_visualizations.ipynb
│
├── visualizations/           # Visualization Scripts
│   ├── __init__.py
│   ├── dashboards.py        # Interactive dashboards
│   └── charts.py            # Static charts (matplotlib/seaborn)
│
├── config/                   # Configuration Files
│   ├── database.yaml         # Database connection settings
│   ├── keepa_config.yaml     # Keepa API configuration
│   └── benchmark_config.yaml # Benchmark parameters
│
├── tests/                    # Unit Tests
│   ├── __init__.py
│   ├── test_etl.py
│   ├── test_postgres.py
│   └── test_mongodb.py
│
└── docs/                     # Documentation
    ├── setup_guide.md        # Environment setup instructions
    ├── schema_design.md      # Schema design decisions
    └── results/              # Final results and reports
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- MongoDB 4.4+
- Docker (optional, for containerized databases)
- Keepa API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ichbinlucaskim/SQLWarriors.git
cd SQLWarriors
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials and Keepa API key
```

5. Set up databases:
```bash
# PostgreSQL
psql -U postgres -f postgres/schema/create_tables.sql

# MongoDB
python mongodb/schema/collections.py
```

## Team Roles & Responsibilities

### Philip Anand - ETL Lead
**Primary Responsibilities:**
- [ ] Design and implement Keepa API client wrapper
- [ ] Build data extraction pipeline (100,000+ products)
- [ ] Implement data cleaning and transformation logic
- [ ] Create PostgreSQL and MongoDB loaders
- [ ] Set up automated ETL jobs (APScheduler/cron)
- [ ] Handle data deduplication and validation
- [ ] Monitor ETL performance and error handling

**Key Deliverables:**
- `etl/keepa_client.py` - API integration
- `etl/pipeline.py` - Main ETL orchestration
- Automated refresh scheduling
- Data quality reports

### Kevin Perez - SQL Warehouse Architect
**Primary Responsibilities:**
- [ ] Design normalized PostgreSQL schema (products, price_history, reviews)
- [ ] Create primary/foreign key relationships
- [ ] Design and implement indexing strategy for analytics
- [ ] Write optimized analytical queries
- [ ] Create materialized views for common aggregations
- [ ] Benchmark PostgreSQL query performance
- [ ] Document schema design decisions

**Key Deliverables:**
- `postgres/schema/create_tables.sql` - Complete schema
- `postgres/queries/analytical_queries.sql` - Benchmark queries
- Performance optimization documentation
- Query execution plans and analysis

### Lucas Kim - NoSQL Warehouse Architect
**Primary Responsibilities:**
- [ ] Design MongoDB schema (embedded vs. referenced documents)
- [ ] Implement collection structures and indexes
- [ ] Build aggregation pipelines for analytical queries
- [ ] Benchmark MongoDB ingestion throughput
- [ ] Evaluate schema flexibility and evolution
- [ ] Compare denormalization strategies
- [ ] Document NoSQL modeling decisions

**Key Deliverables:**
- `mongodb/schema/collections.py` - Collection definitions
- `mongodb/queries/aggregation_pipelines.py` - Analytical queries
- Schema evolution documentation
- Throughput and performance metrics

### Shared Responsibilities
- [ ] Cross-validate data integrity between both systems
- [ ] Collaborate on benchmarking scripts
- [ ] Create visualizations and dashboards
- [ ] Write final report and presentation
- [ ] Code reviews and testing

## Timeline

### Week 1 (Nov 25 – Dec 1)
- **Nov 25**: Proposal submission ✅
- **Nov 26–27**: Environment setup (deploy databases, configure Python/API)
- **Nov 28–29**: Finalize schemas, prototype ETL with sample data
- **Nov 30–Dec 1**: Execute bulk extraction, initial loads, validate data integrity

### Week 2 (Dec 2 – Dec 8)
- **Dec 2–3**: Run benchmarking scripts (load times, storage, resources)
- **Dec 4–5**: Execute analytical queries, document performance
- **Dec 6–7**: Create visualizations, compile findings into presentation
- **Dec 8**: Final rehearsal and deliverable preparation

### Dec 9
- **Final Presentation and Demonstration**

## Benchmarking Metrics

We will measure and compare:

1. **Ingestion Performance**
   - Bulk load time (100,000+ records)
   - Incremental load time
   - Throughput (records/second)

2. **Query Performance**
   - Simple queries (single table/collection)
   - Complex analytical queries (joins/aggregations)
   - Query latency (p50, p95, p99)

3. **Resource Utilization**
   - CPU usage
   - Memory consumption
   - Storage footprint

4. **Schema Evolution**
   - Schema change implementation time
   - Downtime during migrations
   - Data migration complexity

## Tools & Technologies

- **Python**: ETL pipeline, benchmarking
- **SQLAlchemy**: PostgreSQL ORM
- **Psycopg2**: PostgreSQL driver
- **PyMongo**: MongoDB driver
- **Keepa API**: Data source
- **Jupyter Notebooks**: Interactive analysis
- **Tableau/Grafana**: Dashboards
- **Matplotlib/Seaborn**: Visualizations
- **Docker**: Containerized databases
- **APScheduler**: Automated ETL jobs

## Repository

GitHub: https://github.com/ichbinlucaskim/SQLWarriors

## License

This project is for academic purposes (CMSI-620 Final Project).
