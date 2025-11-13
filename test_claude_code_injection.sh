#!/bin/bash
# Test script for injecting commands into Claude Code sessions via Zellij

echo "=========================================="
echo "Claude Code Command Injection Test"
echo "=========================================="
echo ""
echo "Prerequisites:"
echo "  - Zellij session 'MAIN_AGENT' must be running"
echo "  - Claude Code must be running in that session"
echo "  - Session should be in 'waiting for input' state"
echo ""
echo "Press Enter to continue..."
read

# Check if MAIN_AGENT session exists
echo ""
echo "[1/6] Checking if MAIN_AGENT session exists..."
if zellij list-sessions | grep -q "MAIN_AGENT"; then
    echo "✅ MAIN_AGENT session found"
else
    echo "❌ MAIN_AGENT session NOT found"
    echo "   Please start it with: zellij --session MAIN_AGENT"
    echo "   Then run: claude --dangerously-skip-permissions"
    exit 1
fi

# Test 1: Simple echo command
echo ""
echo "[2/6] Test 1: Simple echo command"
echo "Injecting: echo 'Test 1: Simple command from CACS'"
zellij --session MAIN_AGENT action write-chars "echo 'Test 1: Simple command from CACS'"
sleep 0.5
zellij --session MAIN_AGENT action write 13
echo "✓ Sent. Check MAIN_AGENT session for Claude Code response."
echo "Press Enter to continue..."
read

# Test 2: Natural language instruction
echo ""
echo "[3/6] Test 2: Natural language instruction"
echo "Injecting: List all files in the current directory"
zellij --session MAIN_AGENT action write-chars "List all files in the current directory"
sleep 0.5
zellij --session MAIN_AGENT action write 13
echo "✓ Sent. Check MAIN_AGENT session for Claude Code response."
echo "Press Enter to continue..."
read

# Test 3: File operation in agent directory
echo ""
echo "[4/6] Test 3: Check inbox directory"
echo "Injecting: Check if there are any files in SUBAGENTS/MAIN_AGENT/inbox/"
zellij --session MAIN_AGENT action write-chars "Check if there are any files in SUBAGENTS/MAIN_AGENT/inbox/"
sleep 0.5
zellij --session MAIN_AGENT action write 13
echo "✓ Sent. Check MAIN_AGENT session for Claude Code response."
echo "Press Enter to continue..."
read

# Test 4: Multi-step instruction
echo ""
echo "[5/6] Test 4: Multi-step instruction"
echo "Injecting: Create a test file in inbox, then read it back"
zellij --session MAIN_AGENT action write-chars "Create a file SUBAGENTS/MAIN_AGENT/inbox/test.txt with content 'Hello from CACS test', then read it back to verify"
sleep 0.5
zellij --session MAIN_AGENT action write 13
echo "✓ Sent. Check MAIN_AGENT session for Claude Code response."
echo "Press Enter to continue..."
read

# Test 5: Structured CACS task format
echo ""
echo "[6/6] Test 5: Structured CACS task format"
echo "Injecting: CACS TASK - Read inbox and count messages"
zellij --session MAIN_AGENT action write-chars "CACS TASK: Check SUBAGENTS/MAIN_AGENT/inbox/ directory and count how many files are present. Report the count."
sleep 0.5
zellij --session MAIN_AGENT action write 13
echo "✓ Sent. Check MAIN_AGENT session for Claude Code response."
echo ""

# Summary
echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "Please review the MAIN_AGENT session and answer:"
echo ""
echo "1. Did Claude Code respond to all 5 tests?"
echo "2. Which message format worked best?"
echo "3. Did any tests fail or cause errors?"
echo "4. How did Claude Code handle multi-step instructions?"
echo "5. Is there any delay/lag in responses?"
echo ""
echo "Next steps:"
echo "  - Document which formats work reliably"
echo "  - Test edge cases (Claude Code busy, multiple rapid injections)"
echo "  - Design official CACS message protocol"
echo "  - Build agent-to-agent communication workflow"
echo ""
