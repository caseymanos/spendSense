"""
Guardrails Orchestrator for SpendSense MVP V2

This module coordinates all guardrail checks before recommendations are finalized.

Core Functions:
- run_all_guardrails(user_id, recommendations, user_context): Execute all checks
- log_guardrail_decision(user_id, decision_type, details): Audit trail

Design Principles:
- Consent checked first (blocks all processing)
- Tone validation on all text
- Eligibility filtering on all offers
- Full audit trail logged to trace files

Compliance:
- Implements PRD Part 2, Section 8: Guardrails & Tone Checks
- Ensures 100% compliance with consent, tone, and eligibility rules
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from guardrails.consent import check_consent, get_consent_history
from guardrails.tone import scan_recommendations, check_text_safe
from guardrails.eligibility import apply_all_filters


# Trace file path
TRACE_DIR = Path("docs/traces")


def run_all_guardrails(
    user_id: str,
    recommendations: List[Dict[str, Any]],
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run all guardrail checks on recommendations for a user.

    Args:
        user_id: User identifier
        recommendations: List of recommendation dicts (education + offers)
        user_context: Full user context dict from recommendation engine

    Returns:
        Dictionary with:
        - user_id: user identifier
        - passed: True if all guardrails passed
        - filtered_recommendations: List of recommendations that passed
        - guardrail_results: Dict with results from each guardrail:
            - consent: consent check result
            - tone: tone validation result
            - eligibility: eligibility filter result
        - timestamp: when guardrails were run
        - summary: human-readable summary

    Raises:
        ValueError: If consent not granted (blocks processing)
    """
    timestamp = datetime.now().isoformat()
    results = {
        "user_id": user_id,
        "timestamp": timestamp,
        "guardrail_results": {},
        "passed": True,  # Will be set to False if any check fails
    }

    # GUARDRAIL 1: Consent Check (blocking)
    consent_granted = check_consent(user_id)
    consent_history = get_consent_history(user_id)

    results["guardrail_results"]["consent"] = {
        "granted": consent_granted,
        "status": consent_history["current_status"],
        "consent_timestamp": consent_history["consent_timestamp"],
        "revoked_timestamp": consent_history["revoked_timestamp"],
    }

    if not consent_granted:
        results["passed"] = False
        results["filtered_recommendations"] = []
        results["summary"] = "Consent not granted - processing blocked"

        # Log to trace file
        log_guardrail_decision(user_id, "consent_blocked", {
            "reason": "User has not granted consent",
            "consent_status": consent_history["current_status"],
        })

        return results

    # GUARDRAIL 2: Tone Validation
    tone_scan = scan_recommendations(recommendations)
    results["guardrail_results"]["tone"] = tone_scan

    if not tone_scan["passed"]:
        results["passed"] = False
        # Log violations
        log_guardrail_decision(user_id, "tone_violations", {
            "violations_count": tone_scan["violations_found"],
            "details": tone_scan["details"],
        })

    # GUARDRAIL 3: Eligibility Filtering
    # Separate education items from offers
    education_items = [r for r in recommendations if r.get("type") == "education"]
    # Accept both legacy 'offer' and current 'partner_offer' types
    offers = [r for r in recommendations if r.get("type") in ("offer", "partner_offer")]

    # Apply eligibility filters to offers only
    eligibility_result = apply_all_filters(offers, user_context)
    results["guardrail_results"]["eligibility"] = {
        "total_offers": eligibility_result["total_offers"],
        "eligible_count": eligibility_result["eligible_count"],
        "blocked_count": eligibility_result["blocked_count"],
        "filters_applied": eligibility_result["filters_applied"],
    }

    if eligibility_result["blocked_count"] > 0:
        # Log blocked offers
        log_guardrail_decision(user_id, "offers_blocked", {
            "blocked_count": eligibility_result["blocked_count"],
            "blocked_offers": [
                {
                    "title": b["offer"].get("title"),
                    "reason": b["reason"],
                    "blocked_at": b["blocked_at"],
                }
                for b in eligibility_result["blocked_offers"]
            ],
        })

    # Combine education items (no filtering) with eligible offers
    filtered_recommendations = education_items + eligibility_result["eligible_offers"]

    results["filtered_recommendations"] = filtered_recommendations
    results["summary"] = _generate_summary(results)

    # Log final guardrail results to trace file
    log_guardrail_decision(user_id, "guardrails_complete", {
        "total_recommendations": len(recommendations),
        "filtered_count": len(filtered_recommendations),
        "tone_passed": tone_scan["passed"],
        "eligibility_blocks": eligibility_result["blocked_count"],
    })

    return results


def log_guardrail_decision(
    user_id: str,
    decision_type: str,
    details: Dict[str, Any]
) -> None:
    """
    Log a guardrail decision to the user's trace file.

    Args:
        user_id: User identifier
        decision_type: Type of decision (e.g., "consent_blocked", "tone_violations")
        details: Dict with decision details

    Creates or updates: docs/traces/{user_id}.json
    """
    TRACE_DIR.mkdir(exist_ok=True)
    trace_file = TRACE_DIR / f"{user_id}.json"

    # Load existing trace if it exists
    if trace_file.exists():
        with open(trace_file, "r") as f:
            trace = json.load(f)
    else:
        trace = {
            "user_id": user_id,
            "guardrail_decisions": [],
        }

    # Add new decision
    decision_entry = {
        "timestamp": datetime.now().isoformat(),
        "decision_type": decision_type,
        "details": details,
    }

    # Ensure guardrail_decisions list exists
    if "guardrail_decisions" not in trace:
        trace["guardrail_decisions"] = []

    trace["guardrail_decisions"].append(decision_entry)

    # Write updated trace
    with open(trace_file, "w") as f:
        json.dump(trace, f, indent=2)


def _generate_summary(results: Dict[str, Any]) -> str:
    """Generate human-readable summary of guardrail results."""
    if not results["passed"]:
        if not results["guardrail_results"]["consent"]["granted"]:
            return "Processing blocked: Consent not granted"

        tone_violations = results["guardrail_results"]["tone"]["violations_found"]
        blocked_offers = results["guardrail_results"]["eligibility"]["blocked_count"]

        issues = []
        if tone_violations > 0:
            issues.append(f"{tone_violations} tone violation(s)")
        if blocked_offers > 0:
            issues.append(f"{blocked_offers} ineligible offer(s)")

        return f"Guardrails applied: {', '.join(issues)}"

    return "All guardrails passed"


# Export main functions
__all__ = [
    "run_all_guardrails",
    "log_guardrail_decision",
]
