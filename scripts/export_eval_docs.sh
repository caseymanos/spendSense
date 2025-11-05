#!/bin/bash
# Export evaluation documentation files to Downloads for demo purposes

# Set colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT_DIR="$HOME/Downloads/SpendSenseEval"

echo -e "${BLUE}📦 Exporting SpendSense Evaluation Documentation${NC}"
echo "Project: $PROJECT_ROOT"
echo "Export to: $EXPORT_DIR"
echo ""

# Create export directory
mkdir -p "$EXPORT_DIR"

# Export evaluation results
echo -e "${GREEN}Copying evaluation results...${NC}"
cp "$PROJECT_ROOT/eval/results.csv" "$EXPORT_DIR/" 2>/dev/null || echo "  ⚠️  results.csv not found"
cp "$PROJECT_ROOT/eval/results.json" "$EXPORT_DIR/" 2>/dev/null || echo "  ⚠️  results.json not found"

# Export summary reports
echo -e "${GREEN}Copying summary reports...${NC}"
cp "$PROJECT_ROOT/docs/eval_summary.md" "$EXPORT_DIR/" 2>/dev/null || echo "  ⚠️  eval_summary.md not found"
cp "$PROJECT_ROOT/docs/fairness_report.md" "$EXPORT_DIR/" 2>/dev/null || echo "  ⚠️  fairness_report.md not found"

# Export sample trace files (first 10 for demo)
echo -e "${GREEN}Copying sample trace files (first 10)...${NC}"
mkdir -p "$EXPORT_DIR/traces"
ls "$PROJECT_ROOT/docs/traces/"*.json 2>/dev/null | head -10 | while read trace_file; do
    cp "$trace_file" "$EXPORT_DIR/traces/"
done

# Create README for the export
echo -e "${GREEN}Creating README...${NC}"
cat > "$EXPORT_DIR/README.md" << 'EOF'
# SpendSense Evaluation Documentation

This folder contains evaluation metrics and documentation for the SpendSense MVP V2 system.

## Contents

### Core Evaluation Files

- **results.csv** - Evaluation metrics in CSV format
- **results.json** - Detailed evaluation results in JSON format
- **eval_summary.md** - Human-readable summary of evaluation metrics
- **fairness_report.md** - Demographic fairness analysis report

### Trace Files

The `traces/` directory contains sample decision trace JSONs showing:
- How personas are assigned to users
- Which behavioral signals triggered each persona
- Recommendations generated and their rationales
- Full audit trail for explainability

## Evaluation Metrics

SpendSense is evaluated on these key dimensions:

1. **Coverage** - % of users with persona assignment + ≥3 behaviors (Target: 100%)
2. **Explainability** - % of recommendations with clear rationales (Target: 100%)
3. **Latency** - Processing time per user (Target: <5 seconds)
4. **Auditability** - % of users with complete trace logs (Target: 100%)
5. **Fairness** - Demographic parity across personas (Target: ±10%)

## Architecture

- **Consent-First**: All processing blocked without explicit user consent
- **Local Processing**: No external APIs, all data stays on-device
- **Educational Focus**: Recommendations are educational, not financial advice
- **Transparent**: Every recommendation includes "because" rationale with user data

## Personas (Priority Order)

1. **High Utilization** - Credit strain (utilization >60% or interest charges)
2. **Variable Income Budgeter** - Income instability (CV >0.3)
3. **Subscription Heavy** - 5+ recurring subscriptions
4. **Savings Builder** - Positive savings patterns
5. **General** - Default fallback

---

Generated: $(date)
SpendSense MVP V2 - Explainable, Consent-Aware Financial Behavior Analysis
EOF

# Count exported files
echo ""
echo -e "${BLUE}📊 Export Summary:${NC}"
echo "  Results files: $(ls "$EXPORT_DIR"/*.{csv,json} 2>/dev/null | wc -l | xargs)"
echo "  Report files: $(ls "$EXPORT_DIR"/*.md 2>/dev/null | wc -l | xargs)"
echo "  Trace files: $(ls "$EXPORT_DIR/traces"/*.json 2>/dev/null | wc -l | xargs)"

echo ""
echo -e "${GREEN}✅ Export complete!${NC}"
echo "📁 Location: $EXPORT_DIR"
echo ""
echo "To view:"
echo "  open $EXPORT_DIR"
