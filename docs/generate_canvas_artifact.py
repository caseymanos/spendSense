#!/usr/bin/env python3
"""Generate systematic precision canvas artifact for SpendSense evaluation."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import json

# PEAK6 Brand Colors (as Color objects)
NAVY_DARK = Color(13/255, 27/255, 62/255)
CELLO = Color(28/255, 48/255, 85/255)
BANNER_NAVY = Color(24/255, 40/255, 88/255)
ANZAC_GOLD = Color(221/255, 186/255, 82/255)
SELECTIVE_YELLOW = Color(255/255, 185/255, 0/255)
EMERALD_GREEN = Color(16/255, 185/255, 129/255)
NEUTRAL_GRAY = Color(157/255, 158/255, 160/255)
WHITE = Color(1, 1, 1)
BLACK = Color(0, 0, 0)

def draw_metric_grid(c, x, y, count, color, size=4):
    """Draw a grid of small circles representing metrics."""
    cols = 10
    rows = (count + cols - 1) // cols

    for i in range(count):
        row = i // cols
        col = i % cols

        cx = x + (col * size * 2.5)
        cy = y - (row * size * 2.5)

        c.setFillColor(color)
        c.setStrokeColor(color)
        c.circle(cx, cy, size, fill=1, stroke=0)

def draw_precision_bar(c, x, y, width, height, value, color, label):
    """Draw a precise measurement bar with value."""
    # Background rule
    c.setStrokeColor(NEUTRAL_GRAY)
    c.setLineWidth(0.5)
    c.line(x, y, x + width, y)

    # Value bar
    fill_width = width * (value / 100)
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.rect(x, y - 2, fill_width, height, fill=1, stroke=0)

    # Label
    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 7)
    c.drawString(x, y - 14, label)

    # Value
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(x + width, y - 14, f"{value:.1f}%")

def draw_temporal_marker(c, x, y, text, subtext):
    """Draw temporal reference marker."""
    c.setFillColor(ANZAC_GOLD)
    c.setFont("Helvetica", 6)
    c.drawString(x, y, text)

    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 5)
    c.drawString(x, y - 8, subtext)

def create_canvas_artifact():
    """Create the systematic precision artifact."""
    # Load data
    with open('eval/results_2025-11-08T21-53-10.json', 'r') as f:
        data = json.load(f)

    # Canvas setup
    pdf_path = 'docs/SpendSense_Evaluation_Canvas_PEAK6.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Background
    c.setFillColor(NAVY_DARK)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # === TITLE ZONE ===
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.75*inch, height - 0.6*inch, "EVALUATION METRICS")

    c.setFillColor(SELECTIVE_YELLOW)
    c.setFont("Helvetica", 6)
    c.drawString(0.75*inch, height - 0.75*inch, "System Analysis — Behavioral Profiling Architecture")

    # Temporal marker
    draw_temporal_marker(c, width - 2.5*inch, height - 0.6*inch,
                        "2025-11-08T21:53:10", "evaluation timestamp")

    # === PRIMARY METRICS GRID ===
    y_start = height - 1.5*inch

    # Coverage - 100 circles (10x10 grid)
    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 6)
    c.drawString(0.75*inch, y_start + 0.2*inch, "Coverage Distribution")

    draw_metric_grid(c, 0.75*inch, y_start, 100, EMERALD_GREEN, size=3)

    c.setFillColor(EMERALD_GREEN)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(3.5*inch, y_start - 0.3*inch, "100")

    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 7)
    c.drawString(3.5*inch, y_start - 0.5*inch, "users with persona")

    # === PRECISION BARS ===
    bar_y = y_start - 1.5*inch
    bar_width = 3*inch
    bar_height = 4

    metrics = [
        ("Coverage", 100.0, EMERALD_GREEN),
        ("Explainability", 100.0, EMERALD_GREEN),
        ("Relevance", 100.0, EMERALD_GREEN),
        ("Auditability", 100.0, EMERALD_GREEN),
    ]

    for i, (label, value, color) in enumerate(metrics):
        draw_precision_bar(c, 0.75*inch, bar_y - (i * 0.4*inch),
                          bar_width, bar_height, value, color, label)

    # === LATENCY MEASUREMENT ===
    latency_y = bar_y - 2*inch

    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 6)
    c.drawString(0.75*inch, latency_y + 0.2*inch, "Latency Analysis")

    # Draw latency visualization (circles for each percentile)
    latency_data = [
        ("MIN", 9.4, 0.75*inch),
        ("MEAN", 10.5, 1.5*inch),
        ("MEDIAN", 10.2, 2.25*inch),
        ("P95", 11.9, 3*inch),
        ("MAX", 20.1, 3.75*inch),
    ]

    for label, value, x_pos in latency_data:
        # Circle size proportional to value
        radius = 8 + (value / 3)

        c.setFillColor(SELECTIVE_YELLOW)
        c.setStrokeColor(SELECTIVE_YELLOW)
        c.circle(x_pos, latency_y - 0.3*inch, radius, fill=0, stroke=1)

        # Value
        c.setFillColor(SELECTIVE_YELLOW)
        c.setFont("Helvetica-Bold", 8)
        text_width = c.stringWidth(f"{value:.1f}", "Helvetica-Bold", 8)
        c.drawString(x_pos - text_width/2, latency_y - 0.35*inch, f"{value:.1f}")

        # Label
        c.setFillColor(NEUTRAL_GRAY)
        c.setFont("Helvetica", 5)
        label_width = c.stringWidth(label, "Helvetica", 5)
        c.drawString(x_pos - label_width/2, latency_y - 0.6*inch, label)

    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 5)
    c.drawString(0.75*inch, latency_y - 0.9*inch, "milliseconds per user")

    # === FAIRNESS DEMOGRAPHICS ===
    demo_y = latency_y - 1.8*inch

    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 6)
    c.drawString(0.75*inch, demo_y + 0.2*inch, "Production Fairness: 5 violations (see report)")

    demographics = [
        ("Gender", 4, 0.75*inch, True),   # Has violations
        ("Income", 3, 1.8*inch, False),   # No violations
        ("Region", 4, 2.7*inch, True),    # Has violations
        ("Age", 3, 3.6*inch, True),       # Has violations
    ]

    for demo, count, x_pos, has_violation in demographics:
        # Draw small grid for each demographic
        for i in range(count):
            if has_violation:
                c.setFillColor(SELECTIVE_YELLOW)
                c.setStrokeColor(SELECTIVE_YELLOW)
            else:
                c.setFillColor(EMERALD_GREEN)
                c.setStrokeColor(EMERALD_GREEN)
            c.rect(x_pos + (i * 12), demo_y - 0.2*inch, 8, 8, fill=1, stroke=0)

        # Label
        c.setFillColor(NEUTRAL_GRAY)
        c.setFont("Helvetica", 5)
        c.drawString(x_pos, demo_y - 0.45*inch, demo)

        # Status
        if has_violation:
            c.setFillColor(SELECTIVE_YELLOW)
            c.setFont("Helvetica-Bold", 6)
            c.drawString(x_pos, demo_y - 0.6*inch, "FAIL")
        else:
            c.setFillColor(EMERALD_GREEN)
            c.setFont("Helvetica-Bold", 6)
            c.drawString(x_pos, demo_y - 0.6*inch, "PASS")

    # === PERSONA DISTRIBUTION ===
    persona_y = demo_y - 1.3*inch

    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 6)
    c.drawString(0.75*inch, persona_y + 0.2*inch, "Persona Assignment")

    personas = [
        ("Cash Flow Optimizer", 57, EMERALD_GREEN),
        ("High Utilization", 27, SELECTIVE_YELLOW),
        ("General", 8, NEUTRAL_GRAY),
        ("Subscription-Heavy", 6, ANZAC_GOLD),
        ("Savings Builder", 2, EMERALD_GREEN),
    ]

    x_offset = 0.75*inch
    for name, count, color in personas:
        # Count
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_offset, persona_y - 0.15*inch, str(count))

        # Name
        c.setFillColor(NEUTRAL_GRAY)
        c.setFont("Helvetica", 5)
        c.drawString(x_offset, persona_y - 0.35*inch, name)

        x_offset += 1.1*inch

    # === SYSTEM IDENTIFIER ===
    c.setFillColor(ANZAC_GOLD)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(0.75*inch, 1.2*inch, "SpendSense")

    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 7)
    c.drawString(0.75*inch, 1*inch, "Consent-aware behavioral analysis system")

    # === REFERENCE MARKERS ===
    c.setFillColor(NEUTRAL_GRAY)
    c.setFont("Helvetica", 5)
    c.drawString(0.75*inch, 0.6*inch, "PLATINUM PROJECT")
    c.drawString(0.75*inch, 0.5*inch, "PEAK6 Investment Group")

    c.setFillColor(ANZAC_GOLD)
    c.setFont("Helvetica", 4)
    c.drawRightString(width - 0.75*inch, 0.5*inch, "We're in the Business of What Ought To Be")

    # === GRID OVERLAY (subtle) ===
    c.setStrokeColor(Color(1, 1, 1, alpha=0.05))
    c.setLineWidth(0.25)

    # Vertical lines
    for i in range(8):
        x = (i + 1) * inch
        c.line(x, 0, x, height)

    # Horizontal lines
    for i in range(11):
        y = (i + 1) * inch
        c.line(0, y, width, y)

    c.save()
    print(f"✓ Canvas artifact saved: {pdf_path}")

if __name__ == '__main__':
    create_canvas_artifact()
