#!/bin/bash
# Test Zellij session naming - validates we can force session names

echo "=========================================="
echo "Zellij Session Naming Test"
echo "=========================================="
echo ""
echo "This test validates that we can force specific session names"
echo "instead of getting random names like 'didactic-megalodon'"
echo ""

# Test 1: Check current sessions
echo "[TEST 1] Current Zellij sessions:"
echo "---"
zellij list-sessions
echo "---"
echo ""

# Test 2: Instructions for manual test
echo "[TEST 2] Manual validation required:"
echo ""
echo "1. Open a NEW terminal window"
echo "2. Run: zellij --session test_naming"
echo "3. Come back to this terminal"
echo "4. Press Enter to continue..."
read -p ""

echo ""
echo "[TEST 3] Listing sessions again to check if 'test_naming' appears:"
echo "---"
zellij list-sessions
echo "---"
echo ""

# Check if test_naming appears
if zellij list-sessions | grep -q "test_naming"; then
    echo "✅ SUCCESS: Session 'test_naming' found!"
    echo "   This means we CAN force session names with --session flag"
    echo ""
    echo "For CACS, this means:"
    echo "  - Users must start sessions with exact names from agent config"
    echo "  - MAIN_AGENT → zellij --session main_agent"
    echo "  - TEST_AGENT → zellij --session test_agent"
    echo "  - etc."
    echo ""
    echo "Cleaning up test session..."
    zellij kill-session test_naming 2>/dev/null
    echo "✅ Test complete!"
else
    echo "❌ FAILED: Session 'test_naming' NOT found"
    echo "   Expected to see 'test_naming' in the list"
    echo "   This could mean:"
    echo "   1. You didn't start the session yet (go back to step 2)"
    echo "   2. Zellij version doesn't support --session naming"
    echo "   3. Session name format is different"
    echo ""
    echo "Please check your Zellij version:"
    zellij --version
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
