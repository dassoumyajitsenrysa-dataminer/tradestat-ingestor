#!/bin/bash
# Start multiple RQ workers in parallel

NUM_WORKERS=${1:-20}
VENV_PATH="$HOME/tradestat-venv"
PROJECT_PATH="/mnt/c/Users/dassa/Desktop/tradestat-ingestor"

cd "$PROJECT_PATH"
source "$VENV_PATH/bin/activate"

echo "Starting $NUM_WORKERS RQ workers..."

for i in $(seq 1 $NUM_WORKERS); do
    echo "Starting worker $i..."
    python3 scripts/rq_worker.py &
    sleep 0.5
done

echo "All $NUM_WORKERS workers started!"
echo "Press Ctrl+C to stop all workers"

wait
