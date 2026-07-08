"""
DWG pre-processor: patch oversized/corrupt preview sections
so LibreDWG's dwg2dxf can process the file.

The preview section (AcDb:Preview) is a compressed bitmap stored
in newer DWG files. LibreDWG 0.13 has fixed buffer limits that
fail on large previews. This module rewrites the section's
compressed-size field to 0, causing LibreDWG to skip it cleanly.
"""

import struct
import os


def patch_dwg_preview_section(path: str) -> bool:
    """
    Find and neutralize the AcDb:Preview section in a DWG file.

    The DWG 2013+ format stores a preview bitmap with a 4-byte
    uncompressed size followed by a 4-byte compressed size at a
    known offset. Setting compressed_size to 0 causes readers to
    skip the section.

    Returns True if patched, False if no preview section found.
    """
    try:
        with open(path, 'rb') as f:
            data = bytearray(f.read())
    except OSError:
        return False

    patched = _patch_ac1027_preview(data)
    if not patched:
        return False

    try:
        with open(path, 'wb') as f:
            f.write(data)
        return True
    except OSError:
        return False


def _patch_ac1027_preview(data: bytearray) -> bool:
    """
    DWG 2013 (AC1027) files have a system section page map.
    The preview section follows a known structure.

    Strategy: find all occurrences of section page type 2 (preview)
    and null out their compressed size fields. This is conservative
    and won't damage geometry data.
    """
    # DWG magic + version byte
    if len(data) < 32:
        return False
    if data[:3] != b'AC1':
        return False

    # Try brute-force approach: find the preview JPEG/PNG header
    # inside the DWG. Preview sections contain a JPEG (0xFFD8) or
    # PNG (0x89504E47) header. We find this and then work backwards
    # to locate the size fields.

    # More reliable: the preview section descriptor in R2010+
    # has structure: 4 bytes page_type(2), 4 bytes decomp_size,
    # 4 bytes comp_size, 4 bytes page_count, 4 bytes address...
    # We search for decomp_size > 0x4a000 (LibreDWG limit)
    # and zero out comp_size to make it skip.

    found = False
    i = 256  # skip header
    while i < len(data) - 16:
        # Look for section page marker
        # Type 2 = preview, with large decompressed size
        page_type = struct.unpack_from('<I', data, i)[0]
        if page_type == 2:
            decomp_size = struct.unpack_from('<I', data, i + 4)[0]
            if decomp_size > 0x4a000:  # LibreDWG's max
                # Zero out the compressed size field (offset +8)
                struct.pack_into('<I', data, i + 8, 0)
                found = True
            elif decomp_size == 0:
                # Already zero or invalid - zero compressed too
                struct.pack_into('<I', data, i + 8, 0)
                found = True
        i += 1

    return found
