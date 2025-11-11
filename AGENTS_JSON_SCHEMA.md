# Agent Configuration Schema

## Overview

The `test_agents.json` (or your custom agents file) defines the agents in your CACS system.

**Important**: Directory paths are **automatically calculated** from `SUBAGENTS_DIR` environment variable + agent name. You do NOT need to specify `directory_path` in the JSON file.

---

## JSON Schema

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Agent name (UPPERCASE, underscores allowed) | `"MAIN_AGENT"` |
| `role` | string | Agent's role/responsibility | `"CTO & Development Driver"` |
| `category` | string | Agent category | `"core"`, `"infrastructure"`, `"support"` |
| `zellij_session_name` | string | Zellij session name (lowercase) | `"main_agent"` |

### Optional Fields

None currently. All fields above are required.

### Auto-Calculated Fields

| Field | Calculated From | Example |
|-------|-----------------|---------|
| `directory_path` | `SUBAGENTS_DIR` + `name` | `/path/to/SUBAGENTS/MAIN_AGENT` |

---

## Example Configuration

```json
{
  "agents": [
    {
      "name": "MAIN_AGENT",
      "role": "Founder, Manager and Coder of Central Glue Logic",
      "category": "core",
      "zellij_session_name": "main_agent"
    },
    {
      "name": "TEST_AGENT",
      "role": "Testing Specialist - System Validation & Quality Assurance",
      "category": "support",
      "zellij_session_name": "test_agent"
    }
  ]
}
```

---

## Validation Rules

### Agent Name
- ✅ Must be UPPERCASE
- ✅ Can contain letters, numbers, and underscores
- ❌ No lowercase letters
- ❌ No special characters (except `_`)

**Valid**: `MAIN_AGENT`, `DATABASE_AGENT`, `TEST_AGENT_V2`
**Invalid**: `main_agent`, `Main-Agent`, `agent@1`

### Role
- ✅ Can be any non-empty string
- ✅ Descriptive recommended

### Category
- ✅ Can be any string (no predefined list)
- Common values: `core`, `infrastructure`, `support`, `executive`

### Zellij Session Name
- ✅ Must be lowercase
- ✅ Typically the agent name in lowercase
- Recommended format: `agent_name` (lowercase with underscores)

---

## Directory Structure Requirements

The import command validates that the following structure exists:

```
SUBAGENTS/
└── AGENT_NAME/              # Auto-detected from agent name
    ├── inbox/               # ✅ REQUIRED
    ├── TODO.txt             # ⚠️  Optional (warning if missing)
    └── .triggers/           # ⚠️  Optional (warning if missing)
        └── wake_up.txt      # Optional
```

### Creating Required Directories

If directories don't exist, create them:

```bash
# For a single agent
mkdir -p SUBAGENTS/MAIN_AGENT/{inbox,.triggers}
touch SUBAGENTS/MAIN_AGENT/TODO.txt

# For multiple agents
mkdir -p SUBAGENTS/{MAIN_AGENT,TEST_AGENT,DATABASE_AGENT}/{inbox,.triggers}
touch SUBAGENTS/MAIN_AGENT/TODO.txt
touch SUBAGENTS/TEST_AGENT/TODO.txt
touch SUBAGENTS/DATABASE_AGENT/TODO.txt
```

---

## How Path Calculation Works

When you run `python manage.py import_agents --json-file agents.json`:

1. Command reads `SUBAGENTS_DIR` from Django settings
2. Django settings reads it from `.env` file
3. For each agent in JSON:
   - Calculates: `directory_path = SUBAGENTS_DIR + "/" + agent_name`
   - Example: `/home/user/cacs-hitl/SUBAGENTS` + `/` + `MAIN_AGENT`
   - Result: `/home/user/cacs-hitl/SUBAGENTS/MAIN_AGENT`
4. Validates the calculated path exists
5. Imports agent with calculated path

---

## Configuration Files

### .env (Required)
```bash
PROJECT_ROOT=/path/to/your/project
SUBAGENTS_DIR=/path/to/your/project/SUBAGENTS
```

### agents.json (Required)
```json
{
  "agents": [
    {
      "name": "AGENT_NAME",
      "role": "Agent role description",
      "category": "category",
      "zellij_session_name": "agent_name"
    }
  ]
}
```

---

## Benefits of Auto-Calculated Paths

### Before (Hardcoded Paths)
```json
{
  "name": "MAIN_AGENT",
  "directory_path": "/home/alice/projects/cacs-hitl/SUBAGENTS/MAIN_AGENT",
  "role": "...",
  "category": "core",
  "zellij_session_name": "main_agent"
}
```

**Problems**:
- ❌ Not portable (different users have different paths)
- ❌ Must update JSON when moving project
- ❌ Redundant (path repeats SUBAGENTS_DIR)

### After (Auto-Calculated)
```json
{
  "name": "MAIN_AGENT",
  "role": "...",
  "category": "core",
  "zellij_session_name": "main_agent"
}
```

**Benefits**:
- ✅ Portable (works on any machine)
- ✅ Only need to update `.env` file
- ✅ Cleaner, shorter configuration
- ✅ Single source of truth (SUBAGENTS_DIR)

---

## Import Command Usage

```bash
# Import agents
python manage.py import_agents --json-file test_agents.json

# Clear existing agents before importing
python manage.py import_agents --json-file test_agents.json --clear

# The command will:
# 1. Read SUBAGENTS_DIR from settings
# 2. Calculate paths: SUBAGENTS_DIR + agent_name
# 3. Validate directories exist
# 4. Import agents to database
```

---

## Error Messages

### Missing Directory
```
❌ Validation failed
   - Directory does not exist: '/path/to/SUBAGENTS/AGENT_NAME'
   - Expected agent directory at: /path/to/SUBAGENTS/AGENT_NAME
   - Create it with: mkdir -p /path/to/SUBAGENTS/AGENT_NAME/inbox /path/to/SUBAGENTS/AGENT_NAME/.triggers
```

**Solution**: Create the directory structure as shown in the error message.

### Invalid Name Format
```
❌ Validation failed
   - Agent name must be uppercase: 'main_agent'
```

**Solution**: Change agent name to `MAIN_AGENT` in JSON.

### Missing inbox/
```
❌ Validation failed
   - Missing required subdirectory: inbox/ at /path/to/SUBAGENTS/AGENT_NAME/inbox
```

**Solution**: `mkdir -p /path/to/SUBAGENTS/AGENT_NAME/inbox`

---

## Migration from Old Format

If you have an old `agents.json` with `directory_path` fields:

### Old Format (Still Works)
```json
{
  "name": "MAIN_AGENT",
  "directory_path": "/home/user/cacs-hitl/SUBAGENTS/MAIN_AGENT",
  "role": "...",
  "category": "core",
  "zellij_session_name": "main_agent"
}
```

The `directory_path` field will be **ignored** and recalculated.

### New Format (Recommended)
```json
{
  "name": "MAIN_AGENT",
  "role": "...",
  "category": "core",
  "zellij_session_name": "main_agent"
}
```

Simply remove the `directory_path` fields from your JSON file.

---

**Last Updated**: 2025-11-11
**Schema Version**: 2.0 (Auto-calculated paths)
