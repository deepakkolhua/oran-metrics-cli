#!/bin/bash
echo "=== Starting O-RAN RIC Infrastructure ==="
echo ""
echo "[1] Starting Near-RT RIC on port 8000..."
python -m uvicorn oran_metrics.api.ric_server:app --port 8000 &
NEARRT_PID=$!
sleep 2
echo "[2] Starting Non-RT RIC on port 8001..."
python -m uvicorn oran_metrics.api.nonrt_ric:app --port 8001 &
NONRT_PID=$!
sleep 2
echo ""
echo "=== Both RICs running ==="
echo "  Near-RT RIC: http://localhost:8000/docs"
echo "  Non-RT RIC:  http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop both..."
trap "kill $NEARRT_PID $NONRT_PID 2>/dev/null; echo 'Stopped both RICs.'; exit" INT
wait
