#!/bin/bash
# =============================================================================
# TTL Validation Script
# Validates Turtle files using rapper (preferred) or Python rdflib (fallback)
# =============================================================================

set -e
cd "$(dirname "$0")/.."

FILES=("ontology/upw.owl.ttl" "ontology/sample_data.ttl")

echo "============================================================"
echo "TTL Validation"
echo "============================================================"

# Check for rapper first
if command -v rapper &> /dev/null; then
    echo "Using: rapper (raptor)"
    echo ""

    all_passed=true
    for f in "${FILES[@]}"; do
        echo -n "Validating $f ... "
        if rapper -i turtle -c "$f" 2>&1; then
            echo "✓ OK"
        else
            echo "✗ FAILED"
            all_passed=false
        fi
    done

    echo ""
    echo "============================================================"
    if $all_passed; then
        echo "RESULT: ✓ TTL 문법 검증 통과"
        exit 0
    else
        echo "RESULT: ✗ TTL 문법 검증 실패"
        exit 1
    fi

# Fallback to Python rdflib
elif command -v python3 &> /dev/null && python3 -c "import rdflib" 2>/dev/null; then
    echo "Using: Python rdflib (rapper not found)"
    echo ""

    python3 << 'PYEOF'
import sys
from rdflib import Graph

files = ["ontology/upw.owl.ttl", "ontology/sample_data.ttl"]
all_passed = True

for f in files:
    try:
        g = Graph()
        g.parse(f, format="turtle")
        print(f"✓ {f} ({len(g)} triples)")
    except Exception as e:
        print(f"✗ {f}")
        print(f"  Error: {e}")
        all_passed = False

print("")
print("=" * 60)
if all_passed:
    print("RESULT: ✓ TTL 문법 검증 통과")
else:
    print("RESULT: ✗ TTL 문법 검증 실패")
sys.exit(0 if all_passed else 1)
PYEOF

else
    echo "ERROR: No validator available!"
    echo ""
    echo "Install one of the following:"
    echo ""
    echo "  Option 1 - rapper (recommended):"
    echo "    brew install raptor"
    echo ""
    echo "  Option 2 - Python rdflib:"
    echo "    pip install rdflib"
    echo ""
    exit 1
fi
