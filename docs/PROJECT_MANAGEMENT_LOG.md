# Project Management & Task Log

> **Status:** Completed  
> **Project Duration:** November 25, 2025 - December 9, 2025  
> **Documentation Owner:** Lucas Kim

---

## Project Overview

**Project Name:** Comparative Data Warehouse Design: PostgreSQL vs. MongoDB  
**Team:** SQLWarriors (Philip Anand, Kevin Perez, Lucas Kim)  
**Course:** CMSI-620 Database Systems  
**Institution:** Loyola Marymount University

**Objective:** Design, implement, and benchmark two parallel data warehouse architectures using PostgreSQL (relational) and MongoDB (document-oriented) paradigms with a real-world e-commerce dataset.

**Final Status:** ✅ All core objectives completed, benchmark results documented, technical report delivered.

---

## Team Roles & Responsibilities

### Lucas Kim - Lead Data Engineer, System Architect & NoSQL Lead

**Primary Responsibilities:**
- **System Infrastructure:** Design and implementation of the complete Dockerized environment
- **Core Engineering:** Sole developer of Python ETL loaders (PostgreSQL and MongoDB CSV loaders)
- **Orchestration:** Management of the GitHub repository and CI/CD workflows
- **Automation:** End-to-end pipeline automation and testing
- **Documentation:** Comprehensive technical documentation and reporting
- **Benchmarking:** Query performance testing and visualization

### Philip Anand - Data Mining Lead

**Primary Responsibilities:**
- **Data Procurement:** Identification and sourcing of raw CSV datasets
- **Data Migration:** Migrating raw data files into the project environment
- **Quality Assurance:** Performing initial integrity checks on raw CSV content
- **Data Validation:** Verifying CSV headers and row counts to ensure data completeness

### Kevin Perez - SQL Warehouse Architect

**Primary Responsibilities:**
- **Schema Design:** Designing the relational database schema and entity relationships
- **Warehousing:** Developing complex SQL queries for data warehousing
- **Query Development:** Writing analytical queries and optimization
- **Presentation:** Structuring the final project presentation

---

## Execution Log & Task Assignment

### Phase 1: Setup & Infrastructure

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- Set up the project development environment
- Configured Docker containers for PostgreSQL 13 and MongoDB 5.0
- Created `docker-compose.yml` with volume mounts and health checks
- Initialized and managed the GitHub repository
- Established version control protocols and `.gitignore` configuration
- Configured environment variables and connection settings
- Resolved port conflicts (PostgreSQL mapped to port 5433)

**Deliverables:**
- ✅ `docker-compose.yml` - Complete container orchestration
- ✅ `.gitignore` - Data security and repository configuration
- ✅ Environment setup documentation

---

### Phase 2: Data Source Migration

**Assignee:** Philip Anand  
**Status:** ✅ Completed

**Details:**
- Sourced external datasets for the project
- Identified and obtained CSV files containing Amazon product data
- Migrated raw CSV files into the `data/` directory
- Verified file integrity and structure
- Documented data provenance and source limitations
- Performed initial data quality assessment

**Deliverables:**
- ✅ CSV data files in `data/` directory:
  - `products.csv` (~110,000 records)
  - `price_history.csv` (~9.9M records)
  - `sales_rank_history.csv` (~9.9M records)
  - `product_metrics.csv` (~110,000 records)

---

### Phase 3: Data Extraction & Quality Assurance

**Assignee:** Philip Anand  
**Status:** ✅ Completed

**Details:**
- Performed raw data extraction from source locations
- **Initial Data Quality Check:** Verified CSV headers and row counts
- Ensured data completeness before loading
- Validated data formats and structure
- Documented data characteristics and volume

**Deliverables:**
- ✅ Data quality validation report
- ✅ CSV structure verification
- ✅ Data completeness confirmation

---

### Phase 4: Data Warehousing & Schema Design

**Assignee:** Kevin Perez  
**Status:** ✅ Completed

**Details:**
- Designed the Relational Database (RDBMS) schema
- Created Entity-Relationship Diagrams (ERD)
- Wrote SQL DDL scripts for table creation
- Designed normalized star schema architecture
- Implemented foreign key relationships and constraints
- Created indexing strategy for query optimization
- Developed analytical views for common query patterns

**Deliverables:**
- ✅ `postgres/schema/create_tables_csv.sql` - Table definitions with constraints
- ✅ `postgres/schema/create_indexes.sql` - Index creation scripts
- ✅ `postgres/schema/create_views.sql` - Analytical views
- ✅ Schema design documentation

**Query Development:**
- ✅ `postgres/queries/analytical_queries.sql` - Three benchmark queries
  - Price trends by category (monthly aggregation)
  - Top products by sales rank improvement
  - Brand performance analysis

---

### Phase 5: Data Loading (Engineering)

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- **PostgreSQL Loader:** Developed and optimized `etl/loader_postgres_csv.py`
  - Implemented high-performance bulk loading using COPY command
  - Added data type preprocessing (float to integer conversion)
  - Achieved 73,833 rows/second throughput
  - Implemented comprehensive error handling and validation
  - Added data integrity verification post-load
- **MongoDB Loader:** Developed `etl/loader_mongodb_csv.py`
  - Implemented chunked CSV processing to prevent OOM errors
  - Designed in-memory aggregation for embedding time-series arrays
  - Created batch insertion with `insert_many` optimization
  - Implemented post-load indexing strategy
  - Added progress tracking for large-scale operations

**Performance Achievements:**
- PostgreSQL: 271.17 seconds (4.52 minutes) for 20M+ records
- MongoDB: 758.76 seconds (12.65 minutes) for 110K products with embedded arrays

**Deliverables:**
- ✅ `etl/loader_postgres_csv.py` - Production-ready PostgreSQL bulk loader
- ✅ `etl/loader_mongodb_csv.py` - Production-ready MongoDB document loader

---

### Phase 6: MongoDB Schema & Aggregation Development

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- Designed denormalized embedded document schema
- Created MongoDB aggregation pipelines equivalent to PostgreSQL queries
- Implemented indexes for embedded array fields
- Developed query optimization strategies
- Documented MongoDB-specific challenges (memory limits)

**Deliverables:**
- ✅ `mongodb/schema/collections.py` - Collection definitions
- ✅ `mongodb/schema/indexes.py` - Index creation
- ✅ `mongodb/queries/aggregation_pipelines.py` - Analytical queries

---

### Phase 7: ETL Pipeline Orchestration

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- Integrated individual loading scripts into a unified pipeline
- Ensured dependency management between SQL and NoSQL data loads
- Implemented sequential loading with proper order (products → history tables)
- Added comprehensive error handling and recovery mechanisms
- Created data integrity validation workflows

**Deliverables:**
- ✅ Unified ETL pipeline execution flow
- ✅ Dependency management and error handling

---

### Phase 8: Benchmarking & Performance Testing

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- Developed `benchmarks/query_performance.py` for query latency measurement
- Integrated PostgreSQL and MongoDB query execution
- Implemented performance measurement using Python `time` module
- Created comparison framework with speedup calculations
- Documented performance results and analysis

**Benchmark Results:**
- Price Trend Query: PostgreSQL 19.82s vs MongoDB 14.01s
- Top Products Ranking: PostgreSQL 5.53s vs MongoDB (Failed - Memory Error)
- Brand Analysis: PostgreSQL 0.88s vs MongoDB 3.91s

**Deliverables:**
- ✅ `benchmarks/query_performance.py` - Query benchmarking framework
- ✅ Performance metrics and comparisons

---

### Phase 9: Automation & Visualization

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- Scripted the full ETL process to run via a single entry point
- Automated container startup and data initialization sequences
- Created `analysis/generate_dashboard.py` for automated benchmarking
- Implemented visualization generation using Matplotlib/Seaborn
- Automated storage size measurement
- Created result export to JSON for documentation

**Deliverables:**
- ✅ `analysis/generate_dashboard.py` - Automated benchmark suite
- ✅ `benchmark_results.png` - Visualization charts
- ✅ `benchmark_data.json` - Raw benchmark data

---

### Phase 10: Testing & Validation

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- Performed integration testing of the Docker network
- Validated data consistency between raw CSVs and loaded databases
- Tested database connections and health checks
- Verified query result accuracy across both systems
- Cross-validated data integrity (no orphaned records)

**Deliverables:**
- ✅ `analysis/test_db_connection.py` - Connection diagnostics
- ✅ Data integrity validation reports
- ✅ Integration testing completed

---

### Phase 11: Documentation & Reporting

**Assignee:** Lucas Kim  
**Status:** ✅ Completed

**Details:**
- Created comprehensive technical documentation
- Wrote `docs/FINAL_TECHNICAL_REPORT.md` - Professional technical report
- Created `docs/schema_design.md` - Detailed schema documentation
- Developed portfolio-grade `README.md`
- Created `docs/DATA_DICTIONARY.md` - Dataset specifications
- Consolidated and cleaned up project documentation

**Deliverables:**
- ✅ `README.md` - Portfolio-grade project documentation
- ✅ `docs/FINAL_TECHNICAL_REPORT.md` - Comprehensive technical report
- ✅ `docs/schema_design.md` - Schema design documentation
- ✅ `docs/DATA_DICTIONARY.md` - Data dictionary
- ✅ `docs/PROJECT_MANAGEMENT_LOG.md` - This document

---

### Phase 12: Presentation Preparation

**Assignee:** Kevin Perez  
**Status:** ✅ Completed

**Details:**
- **Presentation Structure:** Designed the flow and outline of the final project presentation
- Collaborated on visualizing SQL query results for the final report
- Organized benchmark results for presentation
- Structured comparative analysis for demonstration

**Deliverables:**
- ✅ Final presentation structure and outline
- ✅ Query result visualizations
- ✅ Benchmark comparison materials

---

## Key Achievements by Team Member

### Lucas Kim

**Engineering Accomplishments:**
- Designed and implemented complete Docker infrastructure
- Developed both PostgreSQL and MongoDB CSV loaders from scratch
- Achieved 73,833 rows/second throughput for PostgreSQL
- Implemented memory-efficient chunked processing for MongoDB
- Created automated benchmarking and visualization pipeline
- Resolved critical infrastructure issues (port conflicts, connection problems)

**Documentation Accomplishments:**
- Wrote comprehensive technical report (548 lines)
- Created professional portfolio-grade README
- Developed complete data dictionary
- Established documentation standards and structure

**Total Contributions:**
- 10+ Python scripts
- Docker infrastructure
- Benchmarking framework
- Complete documentation suite

### Philip Anand

**Data Accomplishments:**
- Sourced and procured 20+ million record dataset
- Validated data quality and completeness
- Migrated raw CSV files into project structure
- Performed initial data integrity checks

**Contributions:**
- Data procurement and validation
- Initial quality assurance

### Kevin Perez

**SQL Accomplishments:**
- Designed normalized star schema architecture
- Created optimized indexing strategy
- Developed complex analytical SQL queries
- Achieved superior query performance (0.88s for brand analysis)

**Presentation Accomplishments:**
- Structured final presentation
- Organized benchmark results for demonstration
- Created visualization materials

**Contributions:**
- Complete PostgreSQL schema design
- SQL query development and optimization
- Presentation structure

---

## Final Project Statistics

### Code Contributions
- **Lucas Kim:** ~4,500 lines (loaders, automation, documentation)
- **Kevin Perez:** ~500 lines (SQL schemas and queries)
- **Philip Anand:** Data validation and quality assurance

### File Deliverables

**Lucas Kim:**
- ✅ `docker-compose.yml`
- ✅ `etl/loader_postgres_csv.py`
- ✅ `etl/loader_mongodb_csv.py`
- ✅ `benchmarks/query_performance.py`
- ✅ `analysis/generate_dashboard.py`
- ✅ `analysis/test_db_connection.py`
- ✅ Complete documentation suite

**Kevin Perez:**
- ✅ `postgres/schema/create_tables_csv.sql`
- ✅ `postgres/schema/create_indexes.sql`
- ✅ `postgres/schema/create_views.sql`
- ✅ `postgres/queries/analytical_queries.sql`
- ✅ Presentation materials

**Philip Anand:**
- ✅ CSV data files procurement
- ✅ Data quality validation
- ✅ Initial data integrity checks

---

## Performance Benchmarks

### Data Loading
- **PostgreSQL:** 271.17 seconds (4.52 minutes) - 20,018,544 records
- **MongoDB:** 758.76 seconds (12.65 minutes) - 109,992 products with embedded arrays

### Query Performance
- **Price Trend Query:** MongoDB 1.42x faster (14.01s vs 19.82s)
- **Top Products Ranking:** PostgreSQL only (5.53s; MongoDB failed with memory error)
- **Brand Analysis:** PostgreSQL 4.45x faster (0.88s vs 3.91s)

### Storage Efficiency
- **PostgreSQL:** 3,184.79 MB (3.11 GB)
- **MongoDB:** 2,574.42 MB (2.51 GB) - 19% smaller

---

## Project Timeline

### November 25, 2025
- ✅ Project proposal submitted
- ✅ Team roles assigned
- ✅ Initial planning and architecture design

### November 26 - December 1, 2025
- ✅ Infrastructure setup (Lucas)
- ✅ Data procurement (Philip)
- ✅ Schema design finalized (Kevin)
- ✅ Initial loaders implemented (Lucas)

### December 2 - December 8, 2025
- ✅ Full data loading completed (Lucas)
- ✅ Benchmarking suite implemented (Lucas)
- ✅ Query performance testing (Lucas, Kevin)
- ✅ Visualization and reporting (Lucas)
- ✅ Documentation completion (Lucas)
- ✅ Presentation preparation (Kevin)

### December 9, 2025
- ✅ Final presentation delivered
- ✅ Deliverables review
- ✅ Project completion

---

## Conclusion

The SQLWarriors project successfully completed all objectives with clear role divisions:

- **Lucas Kim** handled the majority of engineering work including infrastructure, loaders, automation, and documentation
- **Philip Anand** focused on data procurement and quality assurance
- **Kevin Perez** specialized in SQL schema design and presentation structure

This collaborative effort resulted in a comprehensive comparative analysis providing valuable insights for database selection in data warehousing scenarios.

**Project Status:** ✅ **COMPLETED**

---

**Last Updated:** December 2025  
**Document Version:** 2.0  
**Documentation Owner:** Lucas Kim  
**Status:** Final
