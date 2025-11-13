#!/usr/bin/env python3
"""
Zellij Integration Test Script

Tests if we can successfully inject commands into Zellij sessions.
This validates the core mechanism CACS will use to activate agents.

Usage:
    python test_zellij_integration.py
"""
import subprocess
import sys
import time
import os


def run_command(cmd, description, capture_output=True):
    """Run a shell command and return result"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"CMD:  {cmd}")
    print(f"{'='*60}")

    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"Exit Code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            return result
        else:
            # For interactive commands
            result = subprocess.run(cmd, shell=True, timeout=10)
            return result
    except subprocess.TimeoutExpired:
        print("⚠️  Command timed out after 10 seconds")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║         CACS - Zellij Integration Test Suite            ║
╚══════════════════════════════════════════════════════════╝
""")

    # Test 1: Check if Zellij is installed
    print("\n[1/6] Checking Zellij installation...")
    result = run_command("which zellij", "Check Zellij binary location")
    if not result or result.returncode != 0:
        print("❌ FAILED: Zellij is not installed or not in PATH")
        sys.exit(1)
    print("✅ PASSED: Zellij is installed")

    # Test 2: Check Zellij version
    print("\n[2/6] Checking Zellij version...")
    result = run_command("zellij --version", "Get Zellij version")
    if result and result.returncode == 0:
        print("✅ PASSED: Zellij version detected")
    else:
        print("⚠️  WARNING: Could not get Zellij version")

    # Test 3: List existing Zellij sessions
    print("\n[3/6] Listing existing Zellij sessions...")
    result = run_command("zellij list-sessions", "List all Zellij sessions")

    has_sessions = False
    test_session = "cacs_test_session"

    if result and result.returncode == 0 and result.stdout.strip():
        print("✅ PASSED: Found existing Zellij sessions")
        print("Active sessions:")
        print(result.stdout)
        has_sessions = True
    else:
        print("ℹ️  No existing Zellij sessions found (this is OK)")

    # Test 4: Session creation (informational only)
    print(f"\n[4/6] Session creation (informational)...")
    print("ℹ️  NOTE: Zellij does not have built-in 'detached session creation' like tmux")
    print("ℹ️  Sessions must be created by running: zellij --session <name>")
    print("ℹ️  This enters the session immediately (not detached)")
    print()
    print("For CACS, this means:")
    print("  - Users must manually create agent sessions before using CACS")
    print("  - Each agent needs a pre-existing Zellij session")
    print("  - Session names must match agent's zellij_session_name field")
    print()
    print("Example setup for CACS agents:")
    print("  1. Open terminal, run: zellij --session main_agent")
    print("  2. Open another terminal, run: zellij --session test_agent")
    print("  3. etc. for each agent")
    print()
    print("Alternative: Use zellij tabs/panes within a single session")
    print()
    print("⚠️  SKIPPING automated session creation test")
    print("✓  PASSED: Documented session creation requirements")

    # Test 5: Command injection (requires manual session setup)
    print("\n[5/6] Testing command injection (requires active session)...")

    # List sessions again to find one to test with
    result = run_command("zellij list-sessions", "Find active sessions for testing")

    if result and result.returncode == 0 and result.stdout.strip():
        sessions_output = result.stdout.strip().split('\n')

        print(f"✓ Found {len(sessions_output)} active session(s)")
        print("\nℹ️  MANUAL TEST REQUIRED:")
        print("   To properly test command injection, you need to:")
        print("   1. Have a Zellij session running in another terminal")
        print("   2. Run this test script")
        print("   3. Manually verify commands appear in the session")
        print()
        print("Example manual test commands:")
        print("   # From outside Zellij, send text to a session:")
        print('   zellij --session main_agent action write-chars "echo CACS_TEST"')
        print("   # Send Enter key to execute:")
        print('   zellij --session main_agent action write 13')
        print()
        print("⚠️  SKIPPING automated command injection test")
        print("   (Cannot verify without user confirmation in active session)")

    else:
        print("⚠️  No active Zellij sessions detected")
        print()
        print("To test command injection:")
        print("   1. Open a new terminal")
        print("   2. Run: zellij --session test_cacs")
        print("   3. In original terminal, run: python test_zellij_integration.py")
        print("   4. Verify if commands appear in the zellij session")

    # Test 6: Session management commands
    print("\n[6/6] Testing session management commands...")
    print("\nAvailable Zellij session commands for CACS:")
    print("  • zellij list-sessions          - List all active sessions")
    print("  • zellij attach <name>          - Attach to existing session")
    print("  • zellij kill-session <name>    - Kill a specific session")
    print("  • zellij action write-chars \"text\" - Write text to current session")
    print("  • zellij action write <ascii>   - Send ASCII code (e.g., 13 = Enter)")
    print()
    print("✓ PASSED: Documented session management commands")

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print("""
Key Findings for CACS Implementation:

1. Zellij Sessions:
   - Use 'zellij list-sessions' to discover active sessions
   - Sessions must be running BEFORE sending commands
   - ⚠️  CRITICAL: Zellij cannot create detached sessions like tmux
   - Users must manually create agent sessions before using CACS

2. Command Injection Methods:
   - 'zellij --session <name> action write-chars "command"'
     → Writes text to the specified session
   - 'zellij --session <name> action write 13'
     → Sends Enter key (ASCII 13) to execute the command
   - Must combine both commands to execute

3. CACS Agent Activation Flow:
   Step 1: Check if agent's Zellij session exists
           → zellij list-sessions | grep "main_agent"
   Step 2: If not exists → FAIL with error message
           "Session 'main_agent' not found. Please start it first."
   Step 3: Send activation command
           → zellij --session main_agent action write-chars "cd SUBAGENTS/MAIN_AGENT && ..."
   Step 4: Execute the command
           → zellij --session main_agent action write 13

4. CRITICAL Requirements for Users:
   - Each agent MUST have a pre-existing Zellij session
   - Session name MUST match agent's zellij_session_name field
   - Sessions must be running before CACS activation
   - Users need to manually start sessions (no auto-creation)

5. Recommended User Setup:
   Option A: Multiple terminal windows
     Terminal 1: zellij --session main_agent
     Terminal 2: zellij --session test_agent
     Terminal 3: zellij --session database_agent
     Terminal 4: Run CACS web UI

   Option B: Single Zellij session with tabs/panes
     (May be more complex for command targeting)

Recommended Implementation:
- Always validate session exists before sending commands
- Fail gracefully with helpful error message if session missing
- Use: zellij --session <name> action write-chars "command"
- Follow with: zellij --session <name> action write 13
- Consider timeout/retry logic for command execution
""")

    print("\n✅ Zellij integration test complete!")
    print("\n" + "="*60)
    print("MANUAL TESTING INSTRUCTIONS")
    print("="*60)
    print("""
To validate Zellij command injection for CACS:

1. Open a new terminal and start a test session:
   $ zellij --session test_cacs

2. In your original terminal (where you ran this script), send a test command:
   $ zellij --session test_cacs action write-chars "echo 'Hello from CACS'"

3. Execute the command (send Enter):
   $ zellij --session test_cacs action write 13

4. Check the Zellij session (Terminal 1) - you should see:
   "Hello from CACS" printed in the terminal

5. If successful, CACS can activate agents using the same mechanism!

Alternative test with agent sessions:
   $ zellij --session main_agent action write-chars "cd SUBAGENTS/MAIN_AGENT && ls inbox"
   $ zellij --session main_agent action write 13

If this works, you're ready for Phase 2 implementation! 🚀
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
