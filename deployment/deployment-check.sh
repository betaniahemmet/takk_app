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

# Get server IP
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: ./deployment-check.sh <server-ip>${NC}"
    echo "Example: ./deployment-check.sh 192.168.1.100"
    exit 1
fi

SERVER_IP=$1
BASE_URL="http://$SERVER_IP"

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

# Track failures
FAILURES=0

# Test health endpoint
test_endpoint "/api/health" "Health check" || ((FAILURES++))

# Test main page
test_endpoint "/" "Home page" || ((FAILURES++))

# Test API endpoints
test_endpoint "/api/levels" "Levels API" || ((FAILURES++))
test_endpoint "/api/signs" "Signs API" || ((FAILURES++))
test_endpoint "/api/distractors" "Distractors API" || ((FAILURES++))
test_endpoint "/api/scores" "Scores API" || ((FAILURES++))

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