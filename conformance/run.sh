#!/usr/bin/env bash
# run.sh <command...>   — starts the mock, resets it, runs the SDK smoke script, verifies the wire log.
set -e
cd "$(dirname "$0")"
PORT=${PORT:-4010} node mock-server.mjs >/dev/null & MOCK_PID=$!
trap "kill $MOCK_PID 2>/dev/null" EXIT
for i in $(seq 1 30); do curl -s localhost:${PORT:-4010}/__log >/dev/null && break; sleep 0.2; done
curl -s localhost:${PORT:-4010}/__reset >/dev/null
"$@"
MOCK=http://127.0.0.1:${PORT:-4010} node verify.mjs
