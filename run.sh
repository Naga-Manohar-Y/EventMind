#!/bin/bash
echo "Starting Linq Event Finder pipeline..."
python run.py
if [ $? -eq 0 ]; then
    echo "run.py completed successfully. Starting sum_agent.py..."
    python sum_agent.py
else
    echo "run.py failed. Exiting..."
    exit 1
fi