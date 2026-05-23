"""Thin wrapper for DigiPPPiP manuscript output generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    """Generate project-local manuscript output artifacts."""
    from manuscript_outputs import generate_manuscript_outputs

    outputs = generate_manuscript_outputs(ROOT)
    print(outputs.variables_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
