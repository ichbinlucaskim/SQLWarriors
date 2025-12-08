"""
Quick database connection test script
Tests connections and provides troubleshooting information
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Database Connection Diagnostic Tool")
print("=" * 70)

print("\n[Environment Variables]")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT SET')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT', 'NOT SET')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB', 'NOT SET')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER', 'NOT SET')}")
print(f"POSTGRES_PASSWORD: {'***' if os.getenv('POSTGRES_PASSWORD') else 'NOT SET'}")
print(f"MONGODB_HOST: {os.getenv('MONGODB_HOST', 'NOT SET')}")
print(f"MONGODB_PORT: {os.getenv('MONGODB_PORT', 'NOT SET')}")

print("\n[Port Status]")
import subprocess

# Check PostgreSQL port
try:
    result = subprocess.run(['lsof', '-i', ':5432'], 
                          capture_output=True, text=True, timeout=2)
    if result.stdout:
        print("✓ Port 5432 is in use (PostgreSQL may be running)")
    else:
        print("✗ Port 5432 is NOT in use (PostgreSQL not running)")
except:
    print("? Could not check port 5432")

# Check MongoDB port
try:
    result = subprocess.run(['lsof', '-i', ':27017'], 
                          capture_output=True, text=True, timeout=2)
    if result.stdout:
        print("✓ Port 27017 is in use (MongoDB may be running)")
    else:
        print("✗ Port 27017 is NOT in use (MongoDB not running)")
except:
    print("? Could not check port 27017")

print("\n[Connection Tests]")

# Test PostgreSQL
try:
    import psycopg2
    from postgres.config import get_connection_string
    
    conn_str = get_connection_string()
    conn = psycopg2.connect(conn_str, connect_timeout=3)
    print("✓ PostgreSQL: CONNECTED")
    conn.close()
except ImportError:
    print("✗ PostgreSQL: psycopg2 not installed (pip install psycopg2-binary)")
except Exception as e:
    print(f"✗ PostgreSQL: {type(e).__name__}: {str(e)[:80]}")
    if "password" in str(e).lower():
        print("  → Fix: Set POSTGRES_PASSWORD in .env file")
    elif "refused" in str(e).lower() or "connect" in str(e).lower():
        print("  → Fix: Start PostgreSQL server")

# Test MongoDB
try:
    from mongodb.config import get_database
    
    db = get_database()
    client = db.client
    client.admin.command('ping')
    print("✓ MongoDB: CONNECTED")
except ImportError:
    print("✗ MongoDB: pymongo not installed (pip install pymongo)")
except Exception as e:
    print(f"✗ MongoDB: {type(e).__name__}: {str(e)[:80]}")
    if "refused" in str(e).lower() or "connect" in str(e).lower():
        print("  → Fix: Start MongoDB server")

print("\n" + "=" * 70)
print("Troubleshooting Steps:")
print("=" * 70)
print("""
1. If ports are NOT in use:
   - PostgreSQL: Start server via pgAdmin4 or terminal
   - MongoDB: Start server via MongoDB Compass or terminal

2. If password errors:
   - Edit .env file and set correct POSTGRES_PASSWORD

3. If connection refused:
   - Verify server is running: lsof -i :5432 (PostgreSQL)
   - Verify server is running: lsof -i :27017 (MongoDB)

4. Check pgAdmin4/MongoDB Compass for:
   - Server connection details
   - Port numbers (may differ from defaults)
   - Authentication settings
""")

