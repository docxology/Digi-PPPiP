from pathlib import Path
import json

import pytest

from manuscript_variables import generate_variables, save_variables
from manuscript_outputs import (
    generate_manuscript_outputs,
    substitute_manuscript_tokens,
    write_resolved_manuscript_tree,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generate_variables_shape_and_fallbacks():
    variables = generate_variables(PROJECT_ROOT)
    assert variables
    assert all(k == k.upper() for k in variables)
    assert all("{{" not in k and "}}" not in k for k in variables)
    assert variables["CONFIG_TITLE"].startswith("DigiPPPiP")
    assert len(variables["CONFIG_HASH"]) == 16
    assert "GENERATION_TIMESTAMP" in variables
    assert "CONFIG_NUM_DIMENSIONS" in variables


def test_generate_variables_requires_metrics_for_render_mode(tmp_path):
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()
    (manuscript_dir / "config.yaml").write_text("paper:\n  title: DigiPPPiP\nexperiment: {}\n")
    with pytest.raises(FileNotFoundError):
        generate_variables(tmp_path, require_metrics=True)


def test_save_variables_writes_sorted_json(tmp_path):
    out = save_variables({"B": "2", "A": "1"}, tmp_path / "vars.json")
    assert out.exists()
    assert out.read_text().splitlines()[1].strip().startswith('"A"')


def test_substitute_manuscript_tokens_preserves_unresolved_tokens_visibly():
    text = "Known {{KNOWN_TOKEN}} and still {{UNKNOWN_TOKEN}} plus {{123}} {{_TOKEN}} {{lowercase}}."
    assert substitute_manuscript_tokens(text, {"KNOWN_TOKEN": "resolved"}) == (
        "Known resolved and still {{UNKNOWN_TOKEN}} plus {{123}} {{_TOKEN}} {{lowercase}}."
    )


def test_write_resolved_manuscript_tree_copies_render_inputs(tmp_path):
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()
    output_dir = tmp_path / "output" / "manuscript"
    output_dir.mkdir(parents=True)
    (output_dir / "stale_section.md").write_text("stale\n")
    (output_dir / "stale.bib").write_text("stale\n")
    (output_dir / "config.yaml").write_text("stale\n")
    (output_dir / "preamble.md").write_text("stale\n")
    (manuscript_dir / "00_abstract.md").write_text("Title {{TITLE_TOKEN}}\n")
    (manuscript_dir / "README.md").write_text("do not copy\n")
    (manuscript_dir / "SYNTAX.md").write_text("do not copy\n")
    (manuscript_dir / "config.yaml").write_text("paper: {}\n")
    (manuscript_dir / "preamble.md").write_text("% preamble\n")
    (manuscript_dir / "references.bib").write_text("@misc{x, title={X}}\n")

    out_dir = write_resolved_manuscript_tree(tmp_path, {"TITLE_TOKEN": "Resolved"})

    assert (out_dir / "00_abstract.md").read_text() == "Title Resolved\n"
    assert (out_dir / "config.yaml").read_text() == "paper: {}\n"
    assert (out_dir / "preamble.md").read_text() == "% preamble\n"
    assert (out_dir / "references.bib").read_text() == "@misc{x, title={X}}\n"
    assert not (out_dir / "README.md").exists()
    assert not (out_dir / "SYNTAX.md").exists()
    assert not (out_dir / "stale_section.md").exists()
    assert not (out_dir / "stale.bib").exists()


def test_generate_manuscript_outputs_writes_governance_artifacts():
    result = generate_manuscript_outputs(PROJECT_ROOT)

    assert result.variables_path == PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    assert result.resolved_manuscript_dir == PROJECT_ROOT / "output" / "manuscript"
    assert result.source_ledger_path.exists()
    assert result.study_audit_path.exists()
    assert result.provenance_manifest_path.exists()
    assert json.loads(result.source_ledger_path.read_text())["score"] == 1.0
    assert json.loads(result.study_audit_path.read_text())["score"] == 1.0
