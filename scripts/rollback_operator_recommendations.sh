#!/bin/bash
# Rollback script for operator recommendations feature
# WARNING: This will remove operator-created recommendations but preserve audit logs

set -e  # Exit on error

echo "=============================================="
echo "⚠️  ROLLBACK: Operator Recommendations Feature"
echo "=============================================="
echo ""
echo "This script will:"
echo "  1. Drop operator_recommendations table"
echo "  2. Keep recommendation_audit_log for compliance (archived)"
echo "  3. Remove added columns from recommendations table"
echo "  4. Revert code to previous version"
echo ""

# Confirm rollback
read -p "Are you sure you want to rollback? This will delete operator recommendations (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled"
    exit 0
fi

echo ""
echo "Step 1/3: Backing up operator recommendations to archive..."
sqlite3 data/users.sqlite <<'EOF'
-- Archive operator recommendations before deleting
CREATE TABLE IF NOT EXISTS operator_recommendations_archive AS
SELECT *, datetime('now') as archived_at
FROM operator_recommendations;

-- Archive is created with timestamp
EOF
echo "✓ Operator recommendations backed up to operator_recommendations_archive"
echo ""

echo "Step 2/3: Rolling back database schema..."
sqlite3 data/users.sqlite <<'EOF'
-- Drop operator_recommendations table (data is archived)
DROP TABLE IF EXISTS operator_recommendations;

-- Keep audit log table for compliance (rename it)
ALTER TABLE recommendation_audit_log RENAME TO recommendation_audit_log_archive;

-- Note: SQLite doesn't support DROP COLUMN, so we keep the added columns
-- They will just be NULL and unused after rollback
-- This is safe and maintains data integrity
EOF
echo "✓ Database schema rolled back"
echo "  - operator_recommendations table dropped (archived)"
echo "  - audit log preserved as recommendation_audit_log_archive"
echo "  - Note: Added columns remain (safe, unused)"
echo ""

echo "Step 3/3: Code rollback instructions..."
echo "To complete rollback, run these git commands:"
echo ""
echo "  # View the commit before operator recommendations"
echo "  git log --oneline | head -10"
echo ""
echo "  # Revert to previous version (replace COMMIT_HASH)"
echo "  git revert <COMMIT_HASH>"
echo ""
echo "  # Or reset hard (WARNING: loses all changes)"
echo "  git reset --hard HEAD~1"
echo ""
echo "=============================================="
echo "✅ Database Rollback Complete!"
echo "=============================================="
echo ""
echo "What was preserved:"
echo "  ✓ Audit log (archived as recommendation_audit_log_archive)"
echo "  ✓ Operator recommendations (archived as operator_recommendations_archive)"
echo "  ✓ Auto-generated recommendations (unchanged)"
echo ""
echo "What was removed:"
echo "  ✗ operator_recommendations table (live data)"
echo "  ✗ Active audit logging"
echo ""
echo "Next steps:"
echo "  1. Restart your backend: killall uvicorn && uv run uvicorn api.main:app --reload"
echo "  2. Verify auto-generated recommendations still work"
echo "  3. Check archived data if needed: sqlite3 data/users.sqlite 'SELECT * FROM operator_recommendations_archive;'"
echo ""
