"""
DWG Import/Export bridge via LibreDWG CLI tools.

DogCAD delegates DWG I/O to LibreDWG's battle-tested command-line tools:
- dwg2dxf: DWG → DXF (import)
- dxf2dwg: DXF → DWG (export)

This is an optional dependency. Without LibreDWG installed, DogCAD
degrades gracefully with a helpful error message.

Install:
  macOS:  brew install libredwg
  Linux:  apt install libredwg
  Win:    download binaries from github.com/LibreDWG/libredwg/releases
"""

import subprocess
import tempfile
import os
import shutil


def dwg_to_dxf(dwg_path: str) -> str | None:
    """
    Convert a DWG file to DXF using LibreDWG's dwg2dxf.

    Returns path to temporary DXF file, or None if conversion failed.
    Caller is responsible for deleting the temp file.
    """
    if not _has_libredwg():
        return None

    tmp = tempfile.NamedTemporaryFile(suffix='.dxf', delete=False)
    tmp.close()

    try:
        result = subprocess.run(
            ['dwg2dxf', dwg_path, '-o', tmp.name],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return tmp.name
        else:
            # Clean up failed conversion
            os.unlink(tmp.name)
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        return None


def dxf_to_dwg(dxf_path: str, dwg_path: str, version: str = "r2010") -> bool:
    """
    Convert a DXF file to DWG using LibreDWG's dxf2dwg.

    Args:
        dxf_path: Path to source DXF file
        dwg_path: Path for output DWG file
        version:  DWG version: r12, r14, r2000, r2010, r2013, r2018
                  r2010 is default (best compatibility with modern AutoCAD).
                  Note: r2004-r2018 are 'planned' in LibreDWG 0.13 — encoding
                  may have warnings but geometry is preserved.

    Returns True on success.
    """
    if not _has_libredwg():
        return False

    # Strip ezdxf-specific objects that LibreDWG can't handle
    _sanitize_dxf_for_libredwg(dxf_path)

    try:
        result = subprocess.run(
            ['dxf2dwg', dxf_path, '--as', version, '-y', '-o', dwg_path],
            capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def _has_libredwg() -> bool:
    """Check if LibreDWG CLI tools are available."""
    return shutil.which('dwg2dxf') is not None


def get_libredwg_version() -> str | None:
    """Get installed LibreDWG version string, or None."""
    if not _has_libredwg():
        return None
    try:
        result = subprocess.run(
            ['dwg2dxf', '--version'],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception:
        return None


def _sanitize_dxf_for_libredwg(dxf_path: str):
    """
    Strip DXF sections/objects that LibreDWG's dxf2dwg can't handle.
    ezdxf 1.4+ emits MATERIAL, MLEADERSTYLE, and extended HEADER vars
    that cause corruption in the DWG output.

    This modifies the file in-place.
    """
    with open(dxf_path, 'r') as f:
        content = f.read()

    # Remove MATERIAL objects (entire OBJECT section entries for MATERIAL)
    import re
    # Remove MATERIAL blocks: from "  0\nMATERIAL" to the next "  0\n" that's not MATERIAL
    content = re.sub(
        r'  0\nMATERIAL\n.*?(?=\n  0\n(?!MATERIAL))',
        '',
        content,
        flags=re.DOTALL
    )
    # Remove MLEADERSTYLE blocks
    content = re.sub(
        r'  0\nMLEADERSTYLE\n.*?(?=\n  0\n(?!MLEADERSTYLE))',
        '',
        content,
        flags=re.DOTALL
    )

    with open(dxf_path, 'w') as f:
        f.write(content)
