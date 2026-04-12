#!/bin/bash
# Start a fresh Sonnet 4.6 run (500 days, seed 42) via Bedrock
# Uses nohup+setsid for proper process isolation

set -euo pipefail
cd "$(dirname "$0")"

LOG="/tmp/bossbench_sonnet_fresh.log"

echo "Starting fresh Sonnet run..." | tee "$LOG"
nohup setsid uv run python -m saas_bench.agents.baseline.run_test \
  --model us.anthropic.claude-sonnet-4-6 \
  --provider bedrock \
  --seed 42 \
  --days 500 \
  --workspace bash_agent_runs \
  >> "$LOG" 2>&1 &

PID=$!
echo "PID: $PID"
echo "Log: $LOG"

# Wait a moment and check it's still alive
sleep 3
if kill -0 $PID 2>/dev/null; then
    echo "Process alive (PID $PID)"

    # Start seashells monitor
    RUN_DIR=$(ls -td bash_agent_runs/run_*/ 2>/dev/null | head -1)
    if [ -n "$RUN_DIR" ]; then
        echo "Run dir: $RUN_DIR"
        bash start_monitor.sh "$RUN_DIR" 2>/dev/null || echo "Monitor failed to start (non-fatal)"
    fi
else
    echo "ERROR: Process died immediately"
    tail -20 "$LOG"
fi
