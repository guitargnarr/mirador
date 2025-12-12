#!/bin/bash
# Mirador Test Harness - Verify Installation
# Run this to confirm Mirador is working correctly

set -e

echo "=== Mirador Test Suite ==="
echo ""

# 1. Check Ollama
echo "[1/4] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "FAIL: Ollama not installed"
    echo "Install from: https://ollama.ai"
    exit 1
fi
echo "OK: Ollama installed"
ollama list | head -3
echo ""

# 2. Check dependencies
echo "[2/4] Checking Python dependencies..."
python3 -c "import flask; import flask_cors" 2>/dev/null || {
    echo "Installing missing dependencies..."
    pip3 install flask flask-cors
}
echo "OK: Dependencies installed"
echo ""

# 3. Start API and test health
echo "[3/4] Testing API..."
API_PID=""
cleanup() {
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

python3 api.py &
API_PID=$!
sleep 3

HEALTH=$(curl -s http://localhost:5001/api/health 2>/dev/null)
if echo "$HEALTH" | grep -q "ok"; then
    echo "OK: API responding"
else
    echo "FAIL: API not responding"
    echo "Response: $HEALTH"
    exit 1
fi

# 4. List personas
echo ""
echo "[4/4] Checking personas..."
PERSONAS=$(curl -s http://localhost:5001/api/personas 2>/dev/null)
COUNT=$(echo "$PERSONAS" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('chain_order',[])))" 2>/dev/null || echo "0")
echo "OK: Found $COUNT personas in chain"
echo ""

echo "=== All Tests Passed ==="
echo ""
echo "Next steps:"
echo "  - Run a query: curl -X POST http://localhost:5001/api/run/master_coder -H 'Content-Type: application/json' -d '{\"input\": \"Hello\"}'"
echo "  - View personas: curl http://localhost:5001/api/personas"
