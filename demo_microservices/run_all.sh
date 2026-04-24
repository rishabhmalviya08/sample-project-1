#!/bin/bash
source .venv/bin/activate

echo "Starting Inventory API on port 8003..."
uvicorn main_inventory:app --port 8003 &
INV_PID=$!

echo "Starting Payment API on port 8002..."
uvicorn main_payment:app --port 8002 &
PAY_PID=$!

echo "Starting Orders API on port 8001..."
uvicorn main_orders:app --port 8001 &
ORD_PID=$!

echo "All services started! Press Ctrl+C to stop."

# Trap Ctrl+C (SIGINT) to kill child processes
trap "kill -9 $INV_PID $PAY_PID $ORD_PID 2>/dev/null" SIGINT SIGTERM

# Wait for background jobs
wait
