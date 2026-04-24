#!/bin/bash

# Setup virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Clean up stale processes/logs
echo "Cleaning up..."
lsof -i :8001 -t | xargs kill -9 2>/dev/null
lsof -i :8002 -t | xargs kill -9 2>/dev/null
lsof -i :8003 -t | xargs kill -9 2>/dev/null
rm -f logs.txt

# Boot the microservices via the runner script
echo "Starting microservices..."
chmod +x run_all.sh
./run_all.sh > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for startup
sleep 3

echo "Triggering Scenario 1: SQLite Schema Mismatch..."
curl -s -o /dev/null -w "%{http_code}\n" -X POST "http://127.0.0.1:8001/orders/create" -H "Content-Type: application/json" -d '{"user_id": 1, "product_id": 101, "quantity": 1, "user_data": {"billing_address": "123 Main St", "card_number": "1111222233334444"}}'

echo "Triggering Scenario 2: Null Property Defect..."
curl -s -o /dev/null -w "%{http_code}\n" -X POST "http://127.0.0.1:8001/orders/create" -H "Content-Type: application/json" -d '{"user_id": 1, "product_id": 101, "quantity": 1, "user_data": {"card_number": "1111222233334444"}}'

echo "Triggering Scenario 3: Live API Vendor Outage (Hangs for timeout)..."
curl -s -m 2 -o /dev/null -w "Timeout hit!\n" -X POST "http://127.0.0.1:8001/orders/create" -H "Content-Type: application/json" -d '{"user_id": 1, "product_id": 101, "quantity": 1, "user_data": {"billing_address": "123 Main St", "card_number": "4242424242424242"}}'

sleep 2
echo "Done! The bugs have been logged. Please inspect logs.txt."

# Optionally, you can leave the servers running or kill them. Let's kill them so they don't silently drag in the background.
kill -9 $SERVER_PID
lsof -i :8001 -t | xargs kill -9 2>/dev/null
lsof -i :8002 -t | xargs kill -9 2>/dev/null
lsof -i :8003 -t | xargs kill -9 2>/dev/null
