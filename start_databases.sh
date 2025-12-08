#!/bin/bash
# Script to start PostgreSQL and MongoDB databases

echo "=========================================="
echo "Starting Database Servers"
echo "=========================================="

# Try to start PostgreSQL
echo ""
echo "[1] Attempting to start PostgreSQL..."

# Method 1: brew services
if command -v brew &> /dev/null; then
    echo "   Trying brew services..."
    brew services start postgresql@17 2>/dev/null && echo "   ✓ Started via brew services" && PG_STARTED=1 || \
    brew services start postgresql@16 2>/dev/null && echo "   ✓ Started via brew services" && PG_STARTED=1 || \
    brew services start postgresql@15 2>/dev/null && echo "   ✓ Started via brew services" && PG_STARTED=1 || \
    brew services start postgresql 2>/dev/null && echo "   ✓ Started via brew services" && PG_STARTED=1
fi

# Method 2: Check if pgAdmin4 can start it
if [ -z "$PG_STARTED" ]; then
    echo "   ⚠ PostgreSQL not started automatically"
    echo "   → Please start PostgreSQL manually:"
    echo "     1. Open pgAdmin4"
    echo "     2. Right-click on your server → Start Server"
    echo "     3. Or use: pg_ctl -D [data_directory] start"
fi

# Try to start MongoDB
echo ""
echo "[2] Attempting to start MongoDB..."

# Method 1: brew services
if command -v brew &> /dev/null; then
    echo "   Trying brew services..."
    brew services start mongodb-community@7.0 2>/dev/null && echo "   ✓ Started via brew services" && MONGO_STARTED=1 || \
    brew services start mongodb-community@8.0 2>/dev/null && echo "   ✓ Started via brew services" && MONGO_STARTED=1 || \
    brew services start mongodb-community 2>/dev/null && echo "   ✓ Started via brew services" && MONGO_STARTED=1
fi

# Method 2: Direct mongod
if [ -z "$MONGO_STARTED" ]; then
    if command -v mongod &> /dev/null; then
        echo "   Trying direct mongod..."
        # Try common data directories
        for dbpath in "/usr/local/var/mongodb" "$HOME/data/db" "/data/db"; do
            if [ -d "$dbpath" ]; then
                mongod --dbpath "$dbpath" --fork --logpath /tmp/mongod.log 2>/dev/null && \
                echo "   ✓ Started mongod with dbpath: $dbpath" && MONGO_STARTED=1 && break
            fi
        done
    fi
fi

if [ -z "$MONGO_STARTED" ]; then
    echo "   ⚠ MongoDB not started automatically"
    echo "   → Please start MongoDB manually:"
    echo "     1. Open MongoDB Compass"
    echo "     2. It should auto-connect or show connection dialog"
    echo "     3. Or use: mongod --dbpath [data_directory]"
fi

echo ""
echo "=========================================="
echo "Checking server status..."
echo "=========================================="

sleep 2

# Check PostgreSQL
if lsof -i :5432 &> /dev/null; then
    echo "✓ PostgreSQL is running on port 5432"
else
    echo "✗ PostgreSQL is NOT running on port 5432"
fi

# Check MongoDB
if lsof -i :27017 &> /dev/null; then
    echo "✓ MongoDB is running on port 27017"
else
    echo "✗ MongoDB is NOT running on port 27017"
fi

echo ""
echo "To verify, run: python analysis/test_db_connection.py"

