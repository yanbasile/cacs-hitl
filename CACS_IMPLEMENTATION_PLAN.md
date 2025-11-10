# CACS Implementation Plan - MVP v0.1

**Status**: Ready to Implement
**Approach**: Strict Alpha Version - Fast Validation
**Priority**: File Watcher → Zellij → Web UI

---

## 🎯 Architecture Decisions (Finalized)

### 1. **CACS as Django App (Not Standalone Project)**

```
user-project/              # User's existing/new Django project
├── manage.py
├── user_project/
│   ├── settings.py        # User adds 'cacs' to INSTALLED_APPS
│   └── urls.py            # User includes cacs.urls
└── cacs/                  # CACS app (what we build)
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── urls.py
    └── ...
```

**Installation Pattern**:
```bash
# Option 1: Local development
cp -r cacs/ /path/to/user-project/

# Option 2: Future pip install
pip install django-cacs
```

---

## 📋 Configuration (Strict Requirements)

### .env Configuration
```bash
# Required - Project paths
PROJECT_ROOT=/path/to/any-project
SUBAGENTS_DIR=/path/to/any-project/SUBAGENTS
PROJECT_NAME=my-project  # Optional, for UI display

# Required - Database
DATABASE_NAME=cacs_db
DATABASE_USER=cacs_user
DATABASE_PASSWORD=your-password-here
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Required - Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional - Zellij
ZELLIJ_BINARY=/usr/local/bin/zellij  # Default: 'zellij'
```

### File Structure Requirements (STRICT)

**Minimum Required Structure**:
```
PROJECT_ROOT/
└── SUBAGENTS/
    ├── AGENT_1/
    │   └── inbox/           # ✅ Required
    ├── AGENT_2/
    │   └── inbox/           # ✅ Required
    └── ...
```

**Optional but Recommended**:
```
PROJECT_ROOT/
└── SUBAGENTS/
    └── AGENT_NAME/
        ├── inbox/           # ✅ Required
        ├── TODO.txt         # ⚠️  Optional (warning if missing)
        └── .triggers/       # ⚠️  Optional (warning if missing)
            └── wake_up.txt
```

---

## 🔧 Agent Import Requirements (STRICT ALPHA)

### Required Agent Fields (All Mandatory)
```json
{
  "name": "AGENT_NAME",              // Required: String, all caps, underscores
  "directory_path": "/path/to/...",  // Required: Absolute path
  "role": "Agent's Role",            // Required: String
  "category": "category_name",       // Required: String (but can be anything)
  "zellij_session_name": "agent_name" // Required: String, lowercase
}
```

### Agent Import Methods

#### Method 1: Auto-Discovery (Quick Start)
```bash
python manage.py discover_agents --project-root /path/to/project
```
**Behavior**:
- Scans SUBAGENTS/ directory
- Finds directories with inbox/ folder
- **REQUIRES** corresponding entry in agents.json
- Extensive error messages if validation fails

#### Method 2: JSON Import (Full Configuration)
```bash
python manage.py import_agents --json-file /path/to/agents.json
```

**agents.json Format**:
```json
{
  "agents": [
    {
      "name": "ARCHITECT_AGENT",
      "directory_path": "/path/to/SUBAGENTS/ARCHITECT_AGENT",
      "role": "Chief Architect & System Designer",
      "category": "executive",
      "zellij_session_name": "architect_agent"
    },
    {
      "name": "MAIN_AGENT",
      "directory_path": "/path/to/SUBAGENTS/MAIN_AGENT",
      "role": "CTO & Development Driver",
      "category": "executive",
      "zellij_session_name": "main_agent"
    }
  ]
}
```

### Validation Rules (STRICT)
- ❌ Missing required field → **ERROR, import fails**
- ❌ Invalid directory path → **ERROR, import fails**
- ❌ Directory missing inbox/ → **ERROR, import fails**
- ⚠️  Missing TODO.txt → **WARNING, import succeeds**
- ⚠️  Missing .triggers/ → **WARNING, import succeeds**

### Error Messages (Extensive)
```
❌ Agent Import Failed: ARCHITECT_AGENT

Errors:
  - Missing required field: 'role'
  - Directory does not exist: /path/to/SUBAGENTS/ARCHITECT_AGENT
  - Missing required subdirectory: inbox/

Fix these issues and try again.

Expected agent.json format:
{
  "name": "AGENT_NAME",
  "directory_path": "/absolute/path",
  "role": "Agent Role",
  "category": "category",
  "zellij_session_name": "session_name"
}
```

---

## 🏗️ MVP v0.1 Scope (6-8 hours)

### Phase 1: Django App Setup (1 hour)
- [ ] Create cacs/ app directory structure
- [ ] Define 5 models (Agent, Communication, TODO, Activation, RateLimitEvent)
- [ ] Create migrations
- [ ] Configure Django admin
- [ ] Create .env.template
- [ ] Create requirements.txt

### Phase 2: Agent Import (1.5 hours)
- [ ] Management command: discover_agents
- [ ] Management command: import_agents
- [ ] Strict validation with extensive errors
- [ ] JSON schema validation
- [ ] Test with sample agents.json

### Phase 3: File Watcher (2 hours) **PRIORITY #1**
- [ ] Implement watchdog-based file watcher
- [ ] Monitor SUBAGENTS/*/inbox/ for .md files
- [ ] Parse communication files (FROM, TO, SUBJECT, content)
- [ ] Calculate file hash (SHA256)
- [ ] Sync to Communication model
- [ ] Handle file creation and modification
- [ ] Log warnings for protocol violations
- [ ] Management command: start_watcher

### Phase 4: Zellij Integration (1.5 hours) **PRIORITY #2**
- [ ] ZellijManager class
- [ ] Create session
- [ ] Check session exists
- [ ] Send message via zellij pipe
- [ ] Delete session
- [ ] Error handling with retries
- [ ] Test activation workflow

### Phase 5: Web UI (1.5 hours) **PRIORITY #3**
- [ ] Base template (Bootstrap 5)
- [ ] Agent list view
- [ ] Agent detail view
- [ ] Activate agent button (single)
- [ ] Simple dashboard (agent count, status)
- [ ] Basic CSS styling

### Phase 6: Testing & Documentation (1.5 hours)
- [ ] Unit tests (models)
- [ ] Integration test (file watcher)
- [ ] Integration test (zellij)
- [ ] README.md (5-minute quick start)
- [ ] INSTALLATION.md (detailed setup)
- [ ] Sample agents.json

---

## 📦 Deliverables

### Code
```
cacs/                          # Django app (installable)
├── __init__.py
├── models.py                  # 5 models
├── admin.py                   # Django admin config
├── views.py                   # Web views
├── urls.py                    # URL routing
├── apps.py                    # App config
│
├── management/
│   └── commands/
│       ├── discover_agents.py
│       ├── import_agents.py
│       └── start_watcher.py
│
├── services/
│   ├── watcher.py             # File system watcher
│   ├── zellij_manager.py      # Zellij integration
│   └── validators.py          # Strict validation
│
├── templates/
│   ├── cacs/
│   │   ├── base.html
│   │   ├── agent_list.html
│   │   └── agent_detail.html
│
├── static/
│   └── cacs/
│       ├── css/
│       │   └── cacs.css
│       └── js/
│           └── cacs.js
│
└── tests/
    ├── test_models.py
    ├── test_watcher.py
    └── test_zellij.py
```

### Documentation
- `README.md` - Quick start (5 minutes)
- `INSTALLATION.md` - Detailed setup guide
- `USAGE.md` - How to use CACS
- `AGENTS_JSON_SCHEMA.md` - agents.json format
- `TROUBLESHOOTING.md` - Common issues

### Scripts
- `scripts/setup_db.sh` - PostgreSQL setup
- `scripts/setup.sh` - Complete setup automation
- `example_agents.json` - Sample configuration

### Configuration
- `.env.template` - Environment variables template
- `requirements.txt` - Python dependencies

---

## 🚀 Installation Experience (User Perspective)

### Scenario 1: User has existing Django project
```bash
# 1. Copy CACS app into project
cp -r cacs/ /path/to/my-project/

# 2. Add to settings.py
INSTALLED_APPS = [
    ...
    'cacs',
]

# 3. Include URLs in urls.py
urlpatterns = [
    ...
    path('cacs/', include('cacs.urls')),
]

# 4. Configure environment
cp cacs/.env.template .env
nano .env  # Set PROJECT_ROOT, SUBAGENTS_DIR, database

# 5. Setup database
./scripts/setup_db.sh

# 6. Run migrations
python manage.py migrate

# 7. Import agents
python manage.py import_agents --json-file agents.json

# 8. Start servers
python manage.py runserver  # Terminal 1
python manage.py start_watcher  # Terminal 2

# 9. Open browser
open http://localhost:8000/cacs/
```

### Scenario 2: User starting from scratch
```bash
# 1. Create Django project
django-admin startproject myproject
cd myproject

# 2. Copy CACS app
cp -r /path/to/cacs ./

# 3. Follow steps 2-9 from Scenario 1
```

---

## ✅ Validation Checklist

### File Watcher Validation
- [ ] Create test communication file
- [ ] Verify file appears in database within 2 seconds
- [ ] Modify file, verify hash changes detected
- [ ] Check pending_messages incremented for recipient
- [ ] Verify warning logged for protocol violations

### Zellij Validation
- [ ] Run test_zellij_integration.sh
- [ ] Verify messages appear in session
- [ ] Test with Claude Code running
- [ ] Activate agent via web UI
- [ ] Verify session created and message sent
- [ ] Check activation logged in database

### Web UI Validation
- [ ] Agent list displays all agents
- [ ] Click "Activate" creates Zellij session
- [ ] Agent detail shows correct information
- [ ] Dashboard shows accurate counts
- [ ] UI renders correctly on desktop

---

## 🔒 Strict Requirements Summary

### Must Have (or import fails)
1. ✅ All 5 required fields in agents.json
2. ✅ Valid directory paths
3. ✅ inbox/ subdirectory exists
4. ✅ PROJECT_ROOT and SUBAGENTS_DIR in .env
5. ✅ PostgreSQL database configured

### Should Have (warnings only)
1. ⚠️  TODO.txt file
2. ⚠️  .triggers/ directory
3. ⚠️  Proper communication file naming

### Communication File Naming (Strict)
- Format: `YYYYMMDD_HHMMSS_FROM_TO_SUBJECT.md`
- Violation: Log warning, still sync to database

---

## 📊 Success Metrics

### MVP v0.1 is successful if:
1. ✅ File watcher syncs communications within 2 seconds
2. ✅ Zellij activates agents remotely
3. ✅ Web UI is usable (can list and activate agents)
4. ✅ Strict validation catches configuration errors
5. ✅ User can install and run in <10 minutes
6. ✅ Works with any Django project structure

---

## 🛤️ Post-MVP Roadmap

### v0.2 - Enhanced Features (after validation)
- Full REST API
- Outlook-style inbox UI
- Rate limiting with batching
- Protocol validation with compliance reports
- TODO.txt sync
- Dashboard with metrics

### v0.3 - Production Ready
- Comprehensive testing (≥80% coverage)
- Performance optimization
- Multi-project support
- Scheduled activations
- Notification system

### v1.0 - Public Release
- PyPI package (`pip install django-cacs`)
- Complete documentation
- Video tutorials
- Example projects
- Community support

---

## 📝 Notes

- **Alpha Version**: Strict validation, extensive errors
- **Fast Validation**: Build → Test → Iterate
- **Priority Order**: File Watcher → Zellij → Web UI
- **Generic**: Works with any multi-agent Claude project
- **Django App**: Not standalone project, installable app

---

**Document**: `CACS_IMPLEMENTATION_PLAN.md`
**Status**: Approved and Ready
**Next Step**: Run Zellij test, then start Phase 1

---

## Immediate Next Steps

1. **YOU RUN**: `./test_zellij_integration.sh` (validate approach)
2. **YOU REPORT**: Does Zellij pipe work as expected?
3. **I BUILD**: Start Phase 1 (Django app setup)
