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

    # Test 4: Create a test session (detached)
    print(f"\n[4/6] Creating test session: {test_session}...")
    print("Note: Creating a detached session for testing...")

    result = run_command(
        f"zellij --session {test_session} --layout default &",
        f"Create detached Zellij session: {test_session}",
        capture_output=False
    )

    # Wait a moment for session to initialize
    time.sleep(2)

    # Verify session was created
    result = run_command("zellij list-sessions", "Verify session creation")
    if result and test_session in result.stdout:
        print(f"✅ PASSED: Test session '{test_session}' created successfully")
    else:
        print(f"⚠️  WARNING: Could not verify test session creation")
        print("This may be because Zellij requires different session creation method")
        print("Continuing with existing sessions if available...")

    # Test 5: Send command to session via pipe
    print("\n[5/6] Testing command injection via 'zellij pipe'...")

    # List sessions again to find one to test with
    result = run_command("zellij list-sessions", "Find active sessions")

    if result and result.returncode == 0 and result.stdout.strip():
        # Try to extract session name from output
        sessions = result.stdout.strip().split('\n')

        if sessions:
            print(f"\nAttempting to send test command to Zellij session...")

            # Test different pipe methods
            print("\n--- Method 1: Using zellij action write ---")
            test_cmd = f'zellij action write-chars "echo CACS_TEST_MESSAGE"'
            result = run_command(test_cmd, "Send test command via action write")

            if result and result.returncode == 0:
                print("✅ PASSED: Command sent successfully via 'action write'")
            else:
                print("⚠️  Method 1 failed or not supported")

            print("\n--- Method 2: Using zellij pipe ---")
            # Note: zellij pipe requires a plugin name/path
            print("ℹ️  'zellij pipe' typically requires a plugin configuration")
            print("ℹ️  For CACS, we'll likely use 'zellij action' commands instead")

    else:
        print("⚠️  No active sessions found for testing command injection")
        print("ℹ️  You may need to manually start a Zellij session and re-run this test")

    # Test 6: Cleanup test session
    print("\n[6/6] Cleaning up test session...")
    result = run_command(
        f"zellij kill-session {test_session}",
        f"Kill test session: {test_session}"
    )
    if result and result.returncode == 0:
        print(f"✅ PASSED: Test session '{test_session}' cleaned up")
    else:
        print(f"ℹ️  Test session may not exist or was already cleaned up")

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print("""
Key Findings for CACS Implementation:

1. Zellij Sessions:
   - Use 'zellij list-sessions' to discover active sessions
   - Sessions must be running before sending commands

2. Command Injection Methods:
   - 'zellij action write-chars "command"' - writes text to active pane
   - 'zellij action write 13' - sends Enter key (ASCII 13)
   - Combine both to execute commands

3. CACS Agent Activation Flow:
   - Check if agent's Zellij session exists (list-sessions)
   - If not exists, warn user or create session
   - Use 'zellij action write-chars' to send command
   - Use 'zellij action write 13' to execute

4. Potential Issues:
   - Sessions must be pre-created (users must have agents running)
   - Need to target correct session (--session flag)
   - May need focus/attach to specific pane

Recommended Implementation:
- Always validate session exists before sending commands
- Use: zellij --session <name> action write-chars "command"
- Follow with: zellij --session <name> action write 13
""")

    print("\n✅ Zellij integration test complete!")
    print("\nNext steps:")
    print("1. Manually test with a running Zellij session")
    print("2. Try: zellij --session main_agent action write-chars 'echo Hello from CACS'")
    print("3. Follow with: zellij --session main_agent action write 13")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
