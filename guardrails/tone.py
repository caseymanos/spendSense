"""
Tone Validation for SpendSense MVP V2

This module validates recommendation text for judgmental or shaming language.
All recommendations must use supportive, educational tone.

Core Functions:
- validate_tone(text): Check for prohibited phrases
- suggest_alternatives(violations): Map to preferred language
- scan_recommendations(recommendations): Batch validation

Design Principles:
- No shaming language (e.g., "overspending", "bad habits")
- Empowering, educational tone
- Supportive, neutral language
- Flag violations for operator review

Compliance:
- Implements PRD Part 2, Section 8: Tone Guardrails
- Uses PROHIBITED_PHRASES and PREFERRED_ALTERNATIVES from constants
"""

import re
from typing import List, Dict, Any, Tuple

from ingest.constants import PROHIBITED_PHRASES, PREFERRED_ALTERNATIVES


def validate_tone(text: str) -> List[Dict[str, Any]]:
    """
    Check recommendation text for prohibited phrases that violate tone guidelines.

    Args:
        text: Recommendation text to validate

    Returns:
        List of violation dictionaries, each containing:
        - phrase: the prohibited phrase found
        - position: character position in text
        - context: surrounding text (±30 chars)
        - suggestion: preferred alternative

        Empty list if no violations detected.

    Example:
        >>> violations = validate_tone("You're overspending on subscriptions")
        >>> violations[0]['phrase']
        'overspending'
        >>> violations[0]['suggestion']
        'consider reducing spending'
    """
    if not text:
        return []

    violations = []
    text_lower = text.lower()

    for phrase in PROHIBITED_PHRASES:
        # Use word boundaries to avoid partial matches
        # e.g., "discipline" shouldn't match "lack discipline"
        pattern = r"\b" + re.escape(phrase.lower()) + r"\b"

        for match in re.finditer(pattern, text_lower):
            start_pos = match.start()
            end_pos = match.end()

            # Get context (30 chars before and after)
            context_start = max(0, start_pos - 30)
            context_end = min(len(text), end_pos + 30)
            context = text[context_start:context_end]

            violation = {
                "phrase": phrase,
                "position": start_pos,
                "context": context.strip(),
                "suggestion": PREFERRED_ALTERNATIVES.get(phrase, "consider rephrasing"),
            }
            violations.append(violation)

    return violations


def suggest_alternatives(violations: List[Dict[str, Any]]) -> str:
    """
    Generate human-readable suggestions for fixing tone violations.

    Args:
        violations: List of violation dicts from validate_tone()

    Returns:
        Formatted string with suggestions for each violation

    Example:
        >>> violations = validate_tone("You have bad habits")
        >>> print(suggest_alternatives(violations))
        Found 1 tone violation(s):
        - "bad habits" → suggested: "habits to optimize"
    """
    if not violations:
        return "No tone violations detected."

    lines = [f"Found {len(violations)} tone violation(s):"]

    for v in violations:
        lines.append(f'- "{v["phrase"]}" → suggested: "{v["suggestion"]}"')

    return "\n".join(lines)


def scan_recommendations(recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scan a list of recommendations for tone violations.

    Args:
        recommendations: List of recommendation dicts, each with:
            - title: recommendation title
            - rationale: explanation text
            - (other fields)

    Returns:
        Dictionary with:
        - total_recommendations: count
        - violations_found: count of recommendations with violations
        - clean_recommendations: count of recommendations with no violations
        - details: list of dicts with:
            - recommendation_title
            - violations: list of violation dicts
        - passed: boolean (True if no violations)

    Example:
        >>> recs = [
        ...     {"title": "Budget Better", "rationale": "You're overspending"},
        ...     {"title": "Save More", "rationale": "Build your emergency fund"}
        ... ]
        >>> result = scan_recommendations(recs)
        >>> result['violations_found']
        1
        >>> result['passed']
        False
    """
    total = len(recommendations)
    violations_count = 0
    details = []

    for rec in recommendations:
        # Check both title and rationale
        title = rec.get("title", "")
        rationale = rec.get("rationale", "")
        combined_text = f"{title} {rationale}"

        violations = validate_tone(combined_text)

        if violations:
            violations_count += 1
            details.append(
                {
                    "recommendation_title": title,
                    "violations": violations,
                }
            )

    clean_count = total - violations_count

    return {
        "total_recommendations": total,
        "violations_found": violations_count,
        "clean_recommendations": clean_count,
        "details": details,
        "passed": violations_count == 0,
    }


def apply_tone_filter(
    recommendations: List[Dict[str, Any]], strict_mode: bool = True
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Filter recommendations that fail tone validation.

    Args:
        recommendations: List of recommendation dicts
        strict_mode: If True, remove recommendations with violations
                    If False, keep them but add warning flag

    Returns:
        Tuple of:
        - Filtered list of recommendations
        - Report dict with scan results

    Example:
        >>> recs = [{"title": "A", "rationale": "Good advice"}]
        >>> filtered, report = apply_tone_filter(recs)
        >>> report['passed']
        True
    """
    # Scan all recommendations
    scan_result = scan_recommendations(recommendations)

    if strict_mode and not scan_result["passed"]:
        # Remove recommendations with violations
        filtered = []
        violated_titles = {d["recommendation_title"] for d in scan_result["details"]}

        for rec in recommendations:
            if rec.get("title") not in violated_titles:
                filtered.append(rec)
            else:
                # Add to filtered list with warning flag
                rec_copy = rec.copy()
                rec_copy["_tone_warning"] = "REMOVED: Tone violation detected"
                # Don't include in output but log for audit
    else:
        # Keep all but add warning flags
        filtered = []
        violation_map = {d["recommendation_title"]: d["violations"] for d in scan_result["details"]}

        for rec in recommendations:
            rec_copy = rec.copy()
            title = rec.get("title", "")
            if title in violation_map:
                rec_copy["_tone_warning"] = violation_map[title]
            filtered.append(rec_copy)

    return filtered, scan_result


def check_text_safe(text: str) -> bool:
    """
    Quick boolean check if text passes tone validation.

    Args:
        text: Text to check

    Returns:
        True if no violations, False otherwise

    Example:
        >>> check_text_safe("Consider optimizing your spending")
        True
        >>> check_text_safe("You're overspending")
        False
    """
    violations = validate_tone(text)
    return len(violations) == 0
