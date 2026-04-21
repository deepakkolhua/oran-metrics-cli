#!/bin/bash
set -e
echo "============================================"
echo "  Phase 2 Capstone - Full O-RAN Stack Test"
echo "============================================"
echo ""

cd ~/oran-metrics-cli
source .venv/bin/activate

# Step 1: Run all tests
echo "[1/5] Running all tests..."
pytest tests/ -v --tb=short
echo ""

# Step 2: Start both RICs
echo "[2/5] Starting Near-RT RIC and Non-RT RIC..."
python -m uvicorn oran_metrics.api.ric_server:app --port 8000 &
NEARRT_PID=$!
sleep 2
python -m uvicorn oran_metrics.api.nonrt_ric:app --port 8001 &
NONRT_PID=$!
sleep 2
echo "  Both RICs running (PIDs: $NEARRT_PID, $NONRT_PID)"
echo ""

# Step 3: Simulate full network
echo "[3/5] Simulating 5 gNBs sending E2 reports..."
for i in 1 2 3 4 5; do
    BITS=$((20000000 + RANDOM * 2000))
    SINR=$(echo "scale=1; 5 + $RANDOM % 20" | bc)
    PRBS=$((20 + RANDOM % 32))
    curl -s -X POST http://localhost:8000/e2/metric-report \
      -H "Content-Type: application/json" \
      -d "{\"gnb_id\":\"gNB-$i\",\"data_bits\":$BITS,\"time_seconds\":1,\"sinr_db\":$SINR,\"used_prbs\":$PRBS,\"total_prbs\":52}" | python -m json.tool
done
echo ""

# Step 4: Non-RT RIC analyzes all gNBs
echo "[4/5] Non-RT RIC rApp analyzing all gNBs..."
for i in 1 2 3 4 5; do
    echo "  --- gNB-$i ---"
    curl -s http://localhost:8001/rapp/analyze/gNB-$i | python -m json.tool
done
echo ""

# Step 5: Send A1 policy and check health
echo "[5/5] Sending A1 policy and health check..."
curl -s -X POST http://localhost:8001/rapp/create-policy \
  -H "Content-Type: application/json" \
  -d '{"policy_type":"vru-safety","target_gnb":"gNB-1","min_throughput_mbps":40,"priority":"critical"}' | python -m json.tool

echo ""
echo "--- Health Status ---"
echo "Near-RT RIC:"
curl -s http://localhost:8000/health | python -m json.tool
echo "Non-RT RIC:"
curl -s http://localhost:8001/health | python -m json.tool

# Cleanup
kill $NEARRT_PID $NONRT_PID 2>/dev/null

echo ""
echo "============================================"
echo "  Git History:"
git log --oneline
echo ""
echo "  Project Stats:"
echo "  Python files: $(find src tests -name '*.py' | wc -l)"
echo "  Lines of code: $(find src tests -name '*.py' -exec cat {} + | wc -l)"
echo "  Tests: $(pytest tests/ --co -q 2>/dev/null | tail -1)"
echo ""
echo "  Phase 2 Capstone: PASSED"
echo "============================================"
