"""
Structure Prediction Skills — Boltz-1 and AlphaFold3 Wrappers

Provides wrappers for Boltz-1 and AlphaFold3 CLI tools when they are installed,
and informative dry-run stubs when they are not.  A helper reports which
prediction tools are available in the current environment.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


# ─── Tool availability ────────────────────────────────────────────────────────

def check_tools_available() -> dict[str, bool | str]:
    """
    Report which structure prediction tools are installed and accessible.

    Returns:
        Dict mapping tool names to True (installed) or an install hint string.
    """
    results: dict[str, bool | str] = {}

    # Boltz-1
    if shutil.which("boltz") is not None:
        results["boltz"] = True
    else:
        try:
            subprocess.run(
                ["python", "-c", "import boltz"],
                capture_output=True, timeout=5
            )
            results["boltz"] = True
        except Exception:
            results["boltz"] = (
                "Not installed. Install: pip install boltz  "
                "(requires PyTorch; see https://github.com/jwohlwend/boltz)"
            )

    # AlphaFold3
    if shutil.which("alphafold3") is not None:
        results["alphafold3"] = True
    elif shutil.which("run_alphafold.py") is not None:
        results["alphafold3"] = True
    else:
        results["alphafold3"] = (
            "Not installed. AlphaFold3 requires academic access and ~1TB of weights. "
            "See https://github.com/google-deepmind/alphafold3 for setup instructions."
        )

    # ESMFold (local via fair-esm package)
    try:
        import esm  # noqa: F401
        results["esmfold_local"] = True
    except ImportError:
        results["esmfold_local"] = (
            "fair-esm not installed locally. Install: pip install fair-esm  "
            "(large model ~690MB). REST API available via esm_fold_skill."
        )

    # ColabFold (local mmseqs2-based)
    if shutil.which("colabfold_batch") is not None:
        results["colabfold"] = True
    else:
        results["colabfold"] = (
            "Not installed. Install: pip install colabfold  "
            "(see https://github.com/sokrypton/ColabFold)"
        )

    return results


# ─── Boltz-1 ─────────────────────────────────────────────────────────────────

def predict_with_boltz(fasta_path: str, output_dir: str) -> dict:
    """
    Run Boltz-1 structure prediction on a FASTA file.

    Boltz-1 is an open-source biomolecular structure predictor supporting
    proteins, RNA, DNA, and small molecules with AlphaFold3-level accuracy.

    If boltz is installed the real CLI is invoked; otherwise a dry-run dict
    is returned with the command that would have been executed.

    Args:
        fasta_path: Path to input FASTA file.
        output_dir: Directory for Boltz output files.

    Returns:
        Dict with keys:
            - 'status': 'success' | 'dry_run' | 'error'
            - 'command': CLI command that was / would be run
            - 'output_dir': resolved output directory
            - 'message': human-readable description
            - 'error' (only on failure): error text
    """
    fasta_path = str(Path(fasta_path).resolve())
    output_dir = str(Path(output_dir).resolve())
    command = f"boltz predict {fasta_path} --out_dir {output_dir} --device cpu"

    tools = check_tools_available()
    if tools.get("boltz") is not True:
        return {
            "status": "dry_run",
            "command": command,
            "output_dir": output_dir,
            "message": (
                "DRY RUN — Boltz-1 is not installed.\n"
                f"Install hint: {tools['boltz']}\n\n"
                "When installed the following command would be executed:\n"
                f"  {command}\n\n"
                "Boltz-1 supports proteins, RNA, DNA, and small molecules. "
                "It uses a diffusion architecture and produces confident "
                "structures comparable to AlphaFold3."
            ),
        }

    os.makedirs(output_dir, exist_ok=True)
    try:
        result = subprocess.run(
            ["boltz", "predict", fasta_path, "--out_dir", output_dir, "--device", "cpu"],
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if result.returncode != 0:
            return {
                "status": "error",
                "command": command,
                "output_dir": output_dir,
                "message": "Boltz-1 exited with an error.",
                "error": result.stderr,
            }
        return {
            "status": "success",
            "command": command,
            "output_dir": output_dir,
            "message": f"Boltz-1 completed. Results in: {output_dir}",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "command": command,
            "output_dir": output_dir,
            "message": "Boltz-1 timed out after 1 hour.",
        }
    except Exception as exc:
        return {
            "status": "error",
            "command": command,
            "output_dir": output_dir,
            "message": str(exc),
        }


# ─── AlphaFold3 ──────────────────────────────────────────────────────────────

def predict_with_af3(fasta_path: str, output_dir: str) -> dict:
    """
    Run AlphaFold3 structure prediction on a FASTA file.

    AlphaFold3 is Google DeepMind's generalist biomolecular predictor.
    Academic-use model weights require registration at
    https://github.com/google-deepmind/alphafold3.

    If the AF3 CLI (alphafold3 or run_alphafold.py) is installed the real
    command is executed; otherwise a dry-run dict is returned.

    Args:
        fasta_path: Path to input FASTA file.
        output_dir: Directory for AF3 output files.

    Returns:
        Dict with the same structure as predict_with_boltz.
    """
    fasta_path = str(Path(fasta_path).resolve())
    output_dir = str(Path(output_dir).resolve())

    # Detect which AF3 launcher is available
    launcher = shutil.which("alphafold3") or shutil.which("run_alphafold.py")
    command = (
        f"{launcher or 'run_alphafold.py'} "
        f"--input_dir {Path(fasta_path).parent} "
        f"--output_dir {output_dir}"
    )

    tools = check_tools_available()
    if tools.get("alphafold3") is not True:
        return {
            "status": "dry_run",
            "command": command,
            "output_dir": output_dir,
            "message": (
                "DRY RUN — AlphaFold3 is not installed.\n"
                f"Install hint: {tools['alphafold3']}\n\n"
                "When installed the following command would be executed:\n"
                f"  {command}\n\n"
                "AlphaFold3 produces all-atom structures including ligands, "
                "ions, DNA, RNA, and modified residues. Academic use only."
            ),
        }

    os.makedirs(output_dir, exist_ok=True)
    cli_parts = [launcher]
    if launcher and launcher.endswith(".py"):
        cli_parts = ["python", launcher]
    cli_parts += [
        "--input_dir", str(Path(fasta_path).parent),
        "--output_dir", output_dir,
    ]

    try:
        result = subprocess.run(
            cli_parts,
            capture_output=True,
            text=True,
            timeout=7200,
        )
        if result.returncode != 0:
            return {
                "status": "error",
                "command": command,
                "output_dir": output_dir,
                "message": "AlphaFold3 exited with an error.",
                "error": result.stderr,
            }
        return {
            "status": "success",
            "command": command,
            "output_dir": output_dir,
            "message": f"AlphaFold3 completed. Results in: {output_dir}",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "command": command,
            "output_dir": output_dir,
            "message": "AlphaFold3 timed out after 2 hours.",
        }
    except Exception as exc:
        return {
            "status": "error",
            "command": command,
            "output_dir": output_dir,
            "message": str(exc),
        }
