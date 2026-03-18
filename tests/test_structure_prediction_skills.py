"""Tests for structure prediction skills (Boltz, AF3, tool detection)."""
import pytest
from proteintoolbox.skills.structure_prediction_skills import (
    check_tools_available,
    predict_with_boltz,
    predict_with_af3,
)


def test_check_tools_returns_dict():
    result = check_tools_available()
    assert isinstance(result, dict)
    assert "boltz" in result
    assert "alphafold3" in result
    assert "esmfold_local" in result
    assert "colabfold" in result


def test_check_tools_values_are_bool_or_str():
    result = check_tools_available()
    for key, val in result.items():
        assert isinstance(val, (bool, str)), f"Unexpected type for {key}: {type(val)}"


def test_boltz_dry_run_returns_dict(tmp_path):
    """Boltz is almost certainly not installed; expect a dry_run result."""
    result = predict_with_boltz("/fake/seq.fasta", str(tmp_path / "out"))
    assert "status" in result
    assert result["status"] in ("dry_run", "error", "success")
    assert "command" in result
    assert "message" in result


def test_boltz_dry_run_contains_command(tmp_path):
    result = predict_with_boltz("/fake/seq.fasta", str(tmp_path / "out"))
    if result["status"] == "dry_run":
        assert "boltz" in result["command"]


def test_af3_dry_run_returns_dict(tmp_path):
    """AF3 is almost certainly not installed; expect a dry_run result."""
    result = predict_with_af3("/fake/seq.fasta", str(tmp_path / "out"))
    assert "status" in result
    assert result["status"] in ("dry_run", "error", "success")
    assert "command" in result
    assert "message" in result


def test_af3_dry_run_contains_useful_message(tmp_path):
    result = predict_with_af3("/fake/seq.fasta", str(tmp_path / "out"))
    if result["status"] == "dry_run":
        assert "AlphaFold3" in result["message"] or "alphafold" in result["message"].lower()
