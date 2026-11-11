#!/bin/bash
# deployment-check.sh - Verify TAKK deployment is working correctly

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "TAKK Deployment Verification"
echo "=========================================="
echo ""

# Usage: ./deployment-check.sh [base-url]   (default: production)
BASE_URL="${1:-https://takk.betaniahemmet.se}"
BASE_URL="${BASE_URL%/}"

echo "Testing server: $BASE_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -n "Testing $description... "
    
    if curl -s -f -o /dev/null "$BASE_URL$endpoint"; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Track failures. (Not ((FAILURES++)): it returns status 1 when FAILURES is 0,
# which makes `set -e` exit on the first failed check.)
FAILURES=0
fail() { FAILURES=$((FAILURES + 1)); }

# Test health endpoint
test_endpoint "/health" "Health check" || fail

# Test main page
test_endpoint "/" "Home page" || fail

# Test API endpoints
test_endpoint "/api/version" "Version API" || fail
test_endpoint "/api/levels" "Levels API" || fail
test_endpoint "/api/signs" "Signs API" || fail
test_endpoint "/api/distractors" "Distractors API" || fail
test_endpoint "/api/scores" "Scores API" || fail

# HTTPS: HSTS header should be present
if [[ "$BASE_URL" == https://* ]]; then
    echo -n "Testing HSTS header... "
    if curl -s -I "$BASE_URL/" | grep -qi "strict-transport-security"; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ MISSING${NC}"
        fail
    fi
fi

# Test media serving
echo -n "Testing media serving... "
if curl -s -f -o /dev/null "$BASE_URL/media/ui/correct.mp3"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Media might not be configured${NC}"
fi

echo ""
echo "=========================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}All checks passed! ✓${NC}"
    echo ""
    echo "Your TAKK app is ready!"
    echo "Share this URL with users: $BASE_URL"
else
    echo -e "${RED}$FAILURES check(s) failed!${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check if services are running:"
    echo "   sudo systemctl status takk"
    echo "   sudo systemctl status nginx"
    echo ""
    echo "2. Check logs:"
    echo "   sudo journalctl -u takk -n 50"
    echo "   sudo tail -f /var/log/nginx/takk-error.log"
    exit 1
fi

echo "=========================================="