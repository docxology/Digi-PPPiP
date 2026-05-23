"""Pytest configuration for Digi-PPPiP tests.

Mirrors projects/template_code_project/tests/conftest.py: headless matplotlib
and src/ on sys.path so project modules import without installation.
"""

import os
import sys

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
