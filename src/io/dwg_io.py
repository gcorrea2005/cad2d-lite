"""
DWG Import bridge via LibreDWG CLI tools.

DogCAD delegates DWG reading to LibreDWG's battle-tested dwg2dxf:
  DWG → dwg2dxf → temporary DXF → DogCAD's ezdxf import

Optional dependency. Without LibreDWG, degrades gracefully.

Install:
  macOS:  brew install libredwg
  Linux:  apt install libredwg
  Win:    download from github.com/LibreDWG/libredwg/releases
"""

import subprocess
import tempfile
import os
import shutil
import struct


def dwg_to_dxf(dwg_path: str) -> tuple[str | None, str]:
    """
    Convert DWG to DXF. Returns (dxf_path, error_message).

    On success: dxf_path is the temp DXF file, error_message is empty.
    On failure: dxf_path is None, error_message explains why.
    """
    if not _has_libredwg():
        return None, "LibreDWG not installed. Install: brew install libredwg"

    # Detect DWG version for better error messages
    version = _detect_dwg_version(dwg_path)
    if version:
        if version.startswith("AC1032"):  # R2018
            return None, (
                f"DWG version: {version} (R2018+). "
                "LibreDWG 0.13 reads R12-R2013 only. "
                "Use ODA FileConverter to convert to DXF first."
            )

    # Patch oversized/corrupt preview sections before conversion
    # Work on a copy — never modify the user's original file
    import shutil
    tmp_dwg = tempfile.NamedTemporaryFile(suffix='.dwg', delete=False)
    tmp_dwg.close()
    shutil.copy2(dwg_path, tmp_dwg.name)
    from src.io.dwg_patcher import patch_dwg_preview_section
    patch_dwg_preview_section(tmp_dwg.name)
    dwg_path = tmp_dwg.name

    tmp = tempfile.NamedTemporaryFile(suffix='.dxf', delete=False)
    tmp.close()

    try:
        result = subprocess.run(
            ['dwg2dxf', '--minimal', dwg_path, '-o', tmp.name],
            capture_output=True, text=True, timeout=120
        )
        # Success = return 0 OR only "Skip section" warnings (preview too large)
        if result.returncode == 0:
            return tmp.name, ""
        elif _is_skip_section_only(result.stderr):
            # Preview section skipped but geometry imported fine
            return tmp.name, ""
        else:
            # Real error
            error = _extract_error(result.stderr)
            if version:
                error = f"DWG {version}: {error}" if error else f"DWG {version}: conversion failed"
            os.unlink(tmp.name)
            return None, error or "Conversion failed (unknown error)"
    except subprocess.TimeoutExpired:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        return None, "Conversion timed out (>120s). File may be too large or corrupted."
    except FileNotFoundError:
        return None, "dwg2dxf not found. Install LibreDWG: brew install libredwg"
    except OSError as e:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        return None, f"System error: {e}"
    finally:
        # Clean up the temporary DWG copy
        if os.path.exists(tmp_dwg.name):
            os.unlink(tmp_dwg.name)


def _detect_dwg_version(path: str) -> str | None:
    """Read DWG header bytes to detect version string (e.g. 'AC1027' for R2013)."""
    try:
        with open(path, 'rb') as f:
            header = f.read(128)
        # DWG signature: "AC" + version digits starting at byte 0
        if header[:2] == b'AC':
            # Find the version string (AC followed by 4 digits)
            for i in range(0, len(header) - 6):
                if header[i:i+2] == b'AC' and header[i+2:i+6].isdigit():
                    return header[i:i+6].decode('ascii')
        return None
    except Exception:
        return None


def _extract_error(stderr: str) -> str:
    """Extract the most relevant error line from dwg2dxf stderr, skipping Skip section warnings."""
    for line in stderr.split('\n'):
        line = line.strip()
        if not line or 'Skip section' in line:
            continue
        if 'ERROR' in line:
            return line
    for line in stderr.split('\n'):
        if line.strip() and 'Skip section' not in line:
            return line.strip()
    return ""


def _is_skip_section_only(stderr: str) -> bool:
    """Check if all errors are just preview-section warnings (safe to ignore)."""
    if not stderr.strip():
        return True
    for line in stderr.split('\n'):
        line = line.strip()
        if not line:
            continue
        if 'ERROR' not in line:
            continue
        # These preview-section errors are non-fatal — geometry still imports
        if 'AcDb:Preview' in line:
            continue
        if 'Skip section' in line:
            continue
        # Any other ERROR is fatal
        return False
    return True


def _has_libredwg() -> bool:
    """Check if LibreDWG CLI tools are available."""
    return shutil.which('dwg2dxf') is not None


def get_libredwg_version() -> str | None:
    """Get installed LibreDWG version string."""
    if not _has_libredwg():
        return None
    try:
        result = subprocess.run(
            ['dwg2dxf', '--version'],
            capture_output=True, text=True, timeout=5
        )
        return (result.stdout or result.stderr).strip()
    except Exception:
        return None
