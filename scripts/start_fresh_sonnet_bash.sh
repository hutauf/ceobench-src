#!/bin/bash
# Fresh Bedrock Sonnet 4.6 bash_agent run (500 days, seed 42, xhigh reasoning).
# Uses nohup+setsid so the process survives shell exit.

set -euo pipefail
cd "$(dirname "$0")/.."

LOG="/tmp/bossbench_sonnet_bash_fresh.log"

echo "Starting fresh Bedrock Sonnet 4.6 bash_agent run..." | tee "$LOG"
nohup setsid uv run python -m saas_bench.agents.bash_agent.run_test \
  --model us.anthropic.claude-sonnet-4-6 \
  --provider bedrock \
  --reasoning-effort max \
  --seed 42 \
  --days 500 \
  --workspace bash_agent_runs \
  >> "$LOG" 2>&1 &

PID=$!
echo "PID: $PID"
echo "Log: $LOG"

sleep 5
if kill -0 $PID 2>/dev/null; then
    echo "Process alive (PID $PID)"
    for i in 1 2 3 4 5 6 7 8 9 10; do
        RUN_DIR=$(ls -td bash_agent_runs/run_*/ 2>/dev/null | head -1)
        if [ -n "$RUN_DIR" ] && [ -f "$RUN_DIR/checkpoint.json" ]; then
            break
        fi
        sleep 2
    done
    if [ -n "$RUN_DIR" ]; then
        echo "Run dir: $RUN_DIR"
        bash start_monitor.sh "$RUN_DIR" 2>/dev/null || echo "Monitor failed to start (non-fatal)"
    fi
else
    echo "ERROR: Process died immediately"
    tail -40 "$LOG"
fi
