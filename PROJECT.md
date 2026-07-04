# Paintable AI

Version: 0.1.0

---

# Mission

Paintable AI is a desktop application that automates commercial painting takeoffs and estimating.

The software is built specifically for commercial painting contractors.

The objective is to dramatically reduce the time required to estimate commercial painting projects while maintaining estimator-level accuracy.

---

# Product Vision

Paintable AI should become the industry's best software for commercial painting estimating.

The software should:

• Read blueprint PDFs

• Understand construction drawings

• Detect paintable surfaces

• Read finish schedules

• Calculate paintable wall area

• Detect deductions automatically

• Produce professional estimates

---

# Design Philosophy

Paintable AI is an integration-first platform.

We never rebuild mature software.

Instead, we integrate the best available technologies.

Examples include:

- PDFium

- PySide6

- OpenCV

- PaddleOCR

- YOLO

- SAM 2

- SQLite

- openpyxl

The only components built in-house are:

- Commercial Painting Intelligence

- Paintable Surface Detection

- Finish Schedule Intelligence

- Estimating Engine

- Reporting Engine

These components are the company's intellectual property and competitive advantage.



---



# Software Architecture

Application

↓

Viewer Engine

↓

Geometry Engine

↓

OCR Engine

↓

Vision Engine

↓

Paint Intelligence Engine

↓

Estimating Engine

---



# Current Sprint

Professional Blueprint Viewer

Goals:

- Professional PDF navigation
- Zoom
- Pan
- Smooth scrolling
- Fit Width
- Fit Page

---



# Long Term Roadmap

Phase 1

Professional Viewer

Phase 2

Scale Calibration

Phase 3

Measurement Tools

Phase 4

Geometry Engine

Phase 5

Construction Intelligence

Phase 6

Paint Intelligence

Phase 7

Commercial Estimating

---



# Coding Standards

Every class has one responsibility.

Business logic never belongs in UI classes.

Always use type hints.

Always write docstrings.

Keep methods short.

Avoid duplicate code.

Optimize for performance.

Maintain clean architecture.

Never break existing features.

---



# Success Metric

A commercial estimator should be able to upload a blueprint and produce an accurate painting estimate in minutes instead of hours.