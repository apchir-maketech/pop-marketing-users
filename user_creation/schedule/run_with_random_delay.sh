#!/bin/bash

# Make this script executable
# chmod +x run_with_random_delay.sh

# Exit on error
set -e

# Log start time
echo "[$(date)] Starting execution"

# Create/increment counter file for today
TODAY=$(date +%Y-%m-%d)
COUNTER_FILE="/home/augustine_chirra/pop-marketing-users/user_creation/schedule/counts_${TODAY}.txt"

# Initialize counter file if it doesn't exist
if [ ! -f "$COUNTER_FILE" ]; then
    echo "0" > "$COUNTER_FILE"
fi

# Increment counter
count=$(($(cat "$COUNTER_FILE") + 1))
echo $count > "$COUNTER_FILE"

echo "[$(date)] Execution #$count for $TODAY"

# Navigate to the project directory
cd /home/augustine_chirra/pop-marketing-users/user_creation

# Calculate random delay between 0-240 seconds
DELAY=$((RANDOM % 240))
echo "[$(date)] Starting with random delay of $DELAY seconds"
sleep $DELAY

# Activate the virtual environment
source venv/bin/activate

# Run with proper error handling
if python3 create_user.py; then
    echo "[$(date)] Successfully executed create_user.py"
else
    echo "[$(date)] Error executing create_user.py"
    exit 1
fi 

# Deactivate the virtual environment after the script runs
deactivate

echo "[$(date)] Script completed"