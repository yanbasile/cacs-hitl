# Zellij Integration Test for CACS

## Purpose

This test validates that `zellij pipe` can be used to send messages to Zellij sessions, which is the foundation of CACS's remote agent activation feature.

## What We're Testing

1. **Zellij Installation**: Verify Zellij is installed and accessible
2. **Session Creation**: Programmatically create Zellij sessions
3. **Message Sending**: Send messages to sessions via `zellij pipe`
4. **Claude Code Integration**: Verify Claude Code can receive these messages

## Running the Test

```bash
cd /home/user/cacs-hitl
./test_zellij_integration.sh
```

## What to Look For

### ✅ Success Criteria

1. Script reports all checks passed
2. When you attach to the test session (`zellij attach cacs_test_session`), you see:
   - "Test message from CACS"
   - "🔔 CACS: You have 3 pending communications"
   - Multi-line message
3. If you run `claude code` in the session, it starts normally
4. Messages sent via `zellij pipe` while Claude is running appear in the terminal

### ❌ Failure Scenarios

If any of these fail, we'll need an alternative approach:

1. **Messages don't appear**: `zellij pipe` doesn't display text in the session
2. **Claude Code doesn't see messages**: Messages appear but Claude Code doesn't process them
3. **Session creation fails**: Can't create sessions programmatically

## Alternative Approaches (if needed)

If `zellij pipe` doesn't work as expected:

### Plan B: File-Based Triggers
- CACS writes to `.triggers/wake_up.txt`
- Agents poll this file via Claude Code Skill
- More reliable but less elegant

### Plan C: TODO.txt Injection
- CACS prepends notification to agent's TODO.txt
- Agent sees notification when reviewing tasks
- Works but intrusive

### Plan D: stdin Injection (Complex)
- Use `tmux` instead of Zellij
- Send keys directly via `tmux send-keys`
- More complex but proven approach

## Expected Timeline

- **Test Execution**: 5 minutes
- **Manual Verification**: 10 minutes
- **Decision**: Proceed with `zellij pipe` or switch to Plan B

## Next Steps After Test

### If Test Passes ✅
→ Proceed with CACS implementation using Zellij integration

### If Test Fails ❌
→ Discuss alternative approaches
→ Choose Plan B, C, or D
→ Update CACS design accordingly

## Questions to Answer

1. Do messages sent via `zellij pipe` appear in the terminal?
2. Does Claude Code running in the session see these messages?
3. Is there any delay or lag in message delivery?
4. Do emoji characters render correctly?
5. Can we send longer messages (communication summaries)?

## Notes

- Test session name: `cacs_test_session`
- Script creates session in background
- Use `Ctrl+C` to exit and clean up
- Safe to run multiple times

---

**Document**: `ZELLIJ_TEST_README.md`
**Created**: 2025-11-10
**Purpose**: Validate Zellij integration approach before CACS implementation
