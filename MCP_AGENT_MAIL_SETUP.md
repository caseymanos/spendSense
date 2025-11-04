# MCP Agent Mail Setup for SpendSense

## Overview
MCP Agent Mail has been successfully configured for the SpendSense MVP V2 project. This coordination layer enables multi-agent workflows with messaging, file reservations, and audit trails.

## Configuration Details

### Project Information
- **Project Key**: `/Users/caseymanos/GauntletAI/SpendSense`
- **Project Slug**: `users-caseymanos-gauntletai-spendsense`
- **Project ID**: 2
- **Created**: 2025-11-05T01:04:29.802796+00:00

### Agent Identity
- **Name**: WhiteCastle
- **Agent ID**: 6
- **Program**: ClaudeCode
- **Model**: claude-sonnet-4-5
- **Task**: Primary agent for SpendSense MVP V2 development - financial behavior analysis system
- **Inception**: 2025-11-05T01:04:48.440159+00:00
- **Contact Policy**: auto (default)
- **Attachments Policy**: auto

### MCP Server Configuration
- **URL**: http://127.0.0.1:8765/mcp/
- **Bearer Token**: Configured in `.env` file at `/Users/caseymanos/GauntletAI/mcp_agent_mail/.env`
- **Config Location**: `/Users/caseymanos/Library/Application Support/Claude/claude_desktop_config.json`

### File Reservations (Active)
Non-exclusive reservations established for 2 hours:
1. `ingest/**` - Data generation and ingestion
2. `features/**` - Behavioral signal detection
3. `personas/**` - Persona assignment logic
4. `recommend/**` - Recommendation engine
5. `guardrails/**` - Consent and compliance
6. `ui/**` - User interfaces
7. `eval/**` - Evaluation harness
8. `tests/**` - Test suite
9. `docs/**` - Documentation

**Expiry**: 2025-11-05T03:05:01+00:00 (2 hours from setup)
**Reason**: Initial setup and development of SpendSense MVP V2

## Usage Examples

### Using HTTP API Directly

#### Check Inbox
```bash
curl -X POST "http://127.0.0.1:8765/mcp/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "fetch_inbox",
      "arguments": {
        "project_key": "/Users/caseymanos/GauntletAI/SpendSense",
        "agent_name": "WhiteCastle",
        "limit": 10,
        "include_bodies": true
      }
    }
  }'
```

#### Send Message
```bash
curl -X POST "http://127.0.0.1:8765/mcp/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d @message.json
```

#### Reserve Files (Exclusive)
```bash
curl -X POST "http://127.0.0.1:8765/mcp/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "file_reservation_paths",
      "arguments": {
        "project_key": "/Users/caseymanos/GauntletAI/SpendSense",
        "agent_name": "WhiteCastle",
        "paths": ["ingest/data_generator.py"],
        "ttl_seconds": 3600,
        "exclusive": true,
        "reason": "Implementing synthetic data generation enhancements"
      }
    }
  }'
```

#### Release File Reservations
```bash
curl -X POST "http://127.0.0.1:8765/mcp/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "release_file_reservations",
      "arguments": {
        "project_key": "/Users/caseymanos/GauntletAI/SpendSense",
        "agent_name": "WhiteCastle",
        "paths": ["ingest/data_generator.py"]
      }
    }
  }'
```

## Web UI Access

Visit the web interface at: **http://127.0.0.1:8765/mail**

Features:
- Browse all projects and agents
- View inbox/outbox for each agent
- Search messages with FTS5
- View file reservations
- Review attachments
- Send messages as HumanOverseer

## Available Tools

### Core Tools
- `ensure_project` - Register/ensure project exists
- `register_agent` - Create or update agent identity
- `send_message` - Send messages to other agents
- `reply_message` - Reply to existing messages
- `fetch_inbox` - Check agent's inbox
- `acknowledge_message` - Acknowledge received messages

### File Coordination
- `file_reservation_paths` - Reserve files to signal editing intent
- `release_file_reservations` - Release file reservations
- `renew_file_reservations` - Extend TTL on reservations

### Contact Management
- `request_contact` - Request permission to message another agent
- `respond_contact` - Approve/deny contact requests
- `list_contacts` - List approved contacts
- `set_contact_policy` - Set policy (open/auto/contacts_only/block_all)

### Search & Discovery
- `search_messages` - Full-text search with FTS5
- `summarize_thread` - Get thread summary with key points
- `summarize_threads` - Summarize multiple threads
- `whois` - Get agent profile information

### Macros (Convenience)
- `macro_start_session` - Bundle: ensure project + register agent + inbox fetch
- `macro_prepare_thread` - Bundle: register + thread summary + inbox
- `macro_file_reservation_cycle` - Bundle: reserve + work + release
- `macro_contact_handshake` - Bundle: request + respond + welcome message

## Multi-Agent Workflow Example

### Scenario: Two Agents Working on Different Features

**Agent 1: WhiteCastle** (this agent)
- Working on: Data ingestion and feature detection
- Reserves: `ingest/**`, `features/**`

**Agent 2: BlueLake** (hypothetical)
- Working on: UI and recommendations
- Reserves: `ui/**`, `recommend/**`

### Communication Flow
1. BlueLake requests contact with WhiteCastle
2. WhiteCastle approves (or auto-approved if policy is 'auto')
3. BlueLake sends message: "API contract needed for feature detection"
4. WhiteCastle replies with API spec in message thread
5. Both agents work on their respective modules without conflicts
6. File reservations prevent accidental overlaps

## Best Practices

1. **Reserve Before Editing**: Always call `file_reservation_paths` before making significant changes
2. **Use Threads**: Keep related discussions in the same thread_id (e.g., "PR-001", "FEAT-123")
3. **Set AGENT_NAME**: Export `AGENT_NAME=WhiteCastle` so pre-commit hooks can verify reservations
4. **Release Reservations**: Call `release_file_reservations` when done to free up paths
5. **Check Inbox Regularly**: Use `fetch_inbox` to stay coordinated with other agents
6. **Use Importance Flags**: Mark urgent messages with `importance: "high"`

## Environment Setup

To enable pre-commit hooks for file reservation enforcement:

```bash
export AGENT_NAME=WhiteCastle
```

Add to your shell profile:
```bash
echo 'export AGENT_NAME=WhiteCastle' >> ~/.zshrc  # or ~/.bashrc
```

## Troubleshooting

### "sender_name not registered"
- Ensure you've called `register_agent` for the project
- Verify project_key matches exactly

### File Reservation Conflicts
- Check active reservations: View `/mail/{project}/file_reservations`
- Wait for expiry or contact the holding agent
- Use non-exclusive reservations for read-only access

### Inbox Empty
- Verify agent name matches exactly (case-sensitive)
- Check `since_ts` and `limit` parameters
- Ensure messages were sent to this agent

### Cannot Send Messages
- Check contact policy: May need to request contact first
- Verify recipient agent is registered in the project
- Check for `CONTACT_BLOCKED` errors

## Storage Locations

### Git Archive
Messages and artifacts are stored at:
```
~/.mcp_agent_mail_git_mailbox_repo/projects/users-caseymanos-gauntletai-spendsense/
├── agents/WhiteCastle/
│   ├── profile.json
│   ├── inbox/2025/11/
│   └── outbox/2025/11/
├── messages/2025/11/
├── file_reservations/
└── attachments/
```

### SQLite Database
Index and search data:
```
/Users/caseymanos/GauntletAI/mcp_agent_mail/storage.sqlite3
```

## Next Steps

1. **Add More Agents**: Register additional agents for specialized tasks
   - Example: `TestRunner` for running tests
   - Example: `DocWriter` for documentation

2. **Set Up Cross-Project Links**: If coordinating with other repos
   - Use `request_contact` with `to_project` parameter
   - Example: Link to a frontend repo

3. **Install Pre-Commit Guard**: Prevent conflicting commits
   ```bash
   uv run python -m mcp_agent_mail.cli guard install \
     /Users/caseymanos/GauntletAI/SpendSense \
     /Users/caseymanos/GauntletAI/SpendSense
   ```

4. **Explore Web UI**: Browse http://127.0.0.1:8765/mail to see all activity

## Resources

- **MCP Agent Mail Repository**: `/Users/caseymanos/GauntletAI/mcp_agent_mail`
- **Documentation**: `/Users/caseymanos/GauntletAI/mcp_agent_mail/README.md`
- **Example Scripts**: `/Users/caseymanos/GauntletAI/mcp_agent_mail/examples/`
- **Web UI**: http://127.0.0.1:8765/mail

## Test Results

✅ Project registered successfully
✅ Agent "WhiteCastle" created
✅ 9 file reservations granted (no conflicts)
✅ Test message sent and received
✅ Inbox verified with message content

**Status**: Fully operational and ready for multi-agent coordination!
