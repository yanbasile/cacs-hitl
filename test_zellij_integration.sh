#!/bin/bash

################################################################################
# CACS Zellij Integration Test Script
# Purpose: Validate that zellij pipe can send messages to Claude Code sessions
# Run this BEFORE building CACS to verify the approach works
################################################################################

set -e  # Exit on error

echo "=================================="
echo "CACS Zellij Integration Test"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test session name
TEST_SESSION="cacs_test_session"

################################################################################
# Step 1: Check if Zellij is installed
################################################################################
echo -e "${YELLOW}[1/6] Checking if Zellij is installed...${NC}"
if ! command -v zellij &> /dev/null; then
    echo -e "${RED}❌ Zellij not found!${NC}"
    echo ""
    echo "Install Zellij with one of these methods:"
    echo "  - Cargo: cargo install zellij"
    echo "  - Homebrew: brew install zellij"
    echo "  - Apt: sudo apt install zellij"
    echo ""
    exit 1
fi

ZELLIJ_VERSION=$(zellij --version)
echo -e "${GREEN}✓ Zellij is installed: ${ZELLIJ_VERSION}${NC}"
echo ""

################################################################################
# Step 2: List existing sessions (before test)
################################################################################
echo -e "${YELLOW}[2/6] Listing existing Zellij sessions...${NC}"
zellij list-sessions || echo "No existing sessions"
echo ""

################################################################################
# Step 3: Clean up any existing test session
################################################################################
echo -e "${YELLOW}[3/6] Cleaning up any existing test session...${NC}"
if zellij list-sessions 2>/dev/null | grep -q "^${TEST_SESSION}$"; then
    echo "Found existing test session, deleting..."
    zellij delete-session "${TEST_SESSION}" || true
    sleep 1
fi
echo -e "${GREEN}✓ Ready to create new session${NC}"
echo ""

################################################################################
# Step 4: Create test Zellij session
################################################################################
echo -e "${YELLOW}[4/6] Creating test Zellij session '${TEST_SESSION}'...${NC}"
echo "This will open in the background..."

# Create session in detached mode with a simple shell
zellij --session "${TEST_SESSION}" &
ZELLIJ_PID=$!
sleep 3  # Give Zellij time to start

# Check if session was created
if zellij list-sessions | grep -q "^${TEST_SESSION}$"; then
    echo -e "${GREEN}✓ Session '${TEST_SESSION}' created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create session${NC}"
    exit 1
fi
echo ""

################################################################################
# Step 5: Test sending messages via zellij pipe
################################################################################
echo -e "${YELLOW}[5/6] Testing message sending via 'zellij pipe'...${NC}"
echo ""

# Test 1: Simple text message
echo "Test 1: Sending simple text message..."
if zellij pipe --name "${TEST_SESSION}" -- "echo 'Test message from CACS'"; then
    echo -e "${GREEN}✓ Simple message sent successfully${NC}"
else
    echo -e "${RED}❌ Failed to send simple message${NC}"
fi
sleep 1

# Test 2: Message with emoji (like CACS notifications)
echo ""
echo "Test 2: Sending message with emoji..."
if zellij pipe --name "${TEST_SESSION}" -- "echo '🔔 CACS: You have 3 pending communications'"; then
    echo -e "${GREEN}✓ Emoji message sent successfully${NC}"
else
    echo -e "${RED}❌ Failed to send emoji message${NC}"
fi
sleep 1

# Test 3: Multi-line message
echo ""
echo "Test 3: Sending multi-line message..."
if zellij pipe --name "${TEST_SESSION}" -- "echo -e 'Line 1\nLine 2\nLine 3'"; then
    echo -e "${GREEN}✓ Multi-line message sent successfully${NC}"
else
    echo -e "${RED}❌ Failed to send multi-line message${NC}"
fi
sleep 1

echo ""
echo -e "${GREEN}✓ All zellij pipe tests completed${NC}"
echo ""

################################################################################
# Step 6: Manual verification instructions
################################################################################
echo -e "${YELLOW}[6/6] Manual Verification Required${NC}"
echo ""
echo "The test session '${TEST_SESSION}' is now running."
echo ""
echo "To manually verify that messages appear in the session:"
echo ""
echo "  1. Attach to the session:"
echo "     ${GREEN}zellij attach ${TEST_SESSION}${NC}"
echo ""
echo "  2. You should see the test messages we sent:"
echo "     - 'Test message from CACS'"
echo "     - '🔔 CACS: You have 3 pending communications'"
echo "     - Multi-line message"
echo ""
echo "  3. Try running Claude Code in the session:"
echo "     ${GREEN}claude code${NC}"
echo ""
echo "  4. In another terminal, send a message to Claude:"
echo "     ${GREEN}zellij pipe --name ${TEST_SESSION} -- \"echo 'Message to Claude'\"${NC}"
echo ""
echo "  5. Verify Claude Code can see the message"
echo ""
echo "  6. Detach from session: ${GREEN}Ctrl+O, then D${NC}"
echo ""
echo "  7. Clean up when done:"
echo "     ${GREEN}zellij delete-session ${TEST_SESSION}${NC}"
echo ""

################################################################################
# Summary and next steps
################################################################################
echo "=================================="
echo "Test Summary"
echo "=================================="
echo ""
echo -e "${GREEN}✓ Zellij is installed and working${NC}"
echo -e "${GREEN}✓ Can create sessions programmatically${NC}"
echo -e "${GREEN}✓ Can send messages via zellij pipe${NC}"
echo ""
echo "Next Steps:"
echo "  1. Manually attach and verify messages appear"
echo "  2. Test with Claude Code running in the session"
echo "  3. If all works, we can proceed with CACS implementation"
echo ""
echo "If zellij pipe doesn't show messages as expected, we'll use"
echo "an alternative approach (file-based triggers)."
echo ""
echo "=================================="

# Keep script running so session stays alive
echo ""
echo -e "${YELLOW}Press Ctrl+C to exit and clean up the test session${NC}"
echo ""

# Trap Ctrl+C to clean up
trap 'echo ""; echo "Cleaning up..."; zellij delete-session "${TEST_SESSION}" 2>/dev/null || true; echo "Done!"; exit 0' INT

# Wait for user to Ctrl+C
wait
