#!/bin/bash
# Linux/Mac script to start the scheduler

echo "Starting AI Content Creator Scheduler..."
echo

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the scheduler
python main.py --start-scheduler
