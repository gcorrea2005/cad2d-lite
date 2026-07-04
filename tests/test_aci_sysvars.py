"""Tests for ACI color palette and SETVAR engine."""
import pytest
from src.model.aci import aci_to_rgb, aci_to_hex, rgb_to_aci, parse_color, color_to_display, ACI_TABLE
from src.model.sysvars import SysVars


# ── ACI palette ─────────────────────────────────────────────

def test_aci_table_size():
    assert len(ACI_TABLE) >= 240, f"Expected >=240 colors, got {len(ACI_TABLE)}"


def test_aci_standard_colors():
    assert aci_to_rgb(1) == (255, 0, 0)      # Red
    assert aci_to_rgb(2) == (255, 255, 0)    # Yellow
    assert aci_to_rgb(3) == (0, 255, 0)      # Green
    assert aci_to_rgb(5) == (0, 0, 255)      # Blue
    assert aci_to_rgb(7) == (255, 255, 255)  # White
    assert aci_to_rgb(8) == (65, 65, 65)     # Dark Gray


def test_aci_to_hex():
    assert aci_to_hex(1) == "#FF0000"
    assert aci_to_hex(7) == "#FFFFFF"
    assert aci_to_hex(0) == "#000000"


def test_rgb_to_aci_exact():
    assert rgb_to_aci(255, 0, 0) == 1
    assert rgb_to_aci(0, 255, 0) == 3
    assert rgb_to_aci(0, 0, 255) == 5


def test_rgb_to_aci_approximate():
    # Near Red
    assert rgb_to_aci(250, 10, 5) == 1
    # Near Green
    assert rgb_to_aci(5, 248, 3) == 3


def test_parse_color_int():
    assert parse_color(1) == 1
    assert parse_color("3") == 3
    assert parse_color("255") == 255


def test_parse_color_name():
    assert parse_color("Red") == 1
    assert parse_color("red") == 1
    assert parse_color("BLUE") == 5
    assert parse_color("yellow") == 2


def test_parse_color_hex():
    assert parse_color("#FF0000") == 1
    assert parse_color("FF0000") == 1


def test_parse_color_invalid_returns_default():
    assert parse_color("notacolor") == 7
    assert parse_color(999) == 7


def test_color_to_display():
    assert "Red" in color_to_display(1)
    assert "Blue" in color_to_display(5)


# ── SETVAR Engine ───────────────────────────────────────────

def test_sysvars_defaults():
    sv = SysVars()
    assert sv["OSMODE"] == 0
    assert sv["CLAYER"] == "0"
    assert sv["FILLETRAD"] == 0.0
    assert sv["TEXTSIZE"] == 0.2
    assert sv["PDMODE"] == 3
    assert sv["PDSIZE"] == 0.0


def test_sysvars_read_write():
    sv = SysVars()
    sv["FILLETRAD"] = 2.5
    assert sv["FILLETRAD"] == 2.5


def test_sysvars_readonly_raises():
    sv = SysVars()
    with pytest.raises(ValueError, match="read-only"):
        sv["ACADVER"] = "R11"


def test_sysvars_unknown_raises():
    sv = SysVars()
    with pytest.raises(KeyError):
        _ = sv["NONEXISTENT"]


def test_sysvars_setvar_get():
    sv = SysVars()
    val, ro = sv.setvar("OSMODE")
    assert val == 0
    assert ro is False


def test_sysvars_setvar_readonly():
    sv = SysVars()
    val, ro = sv.setvar("ACADVER")
    assert val == "R10"
    assert ro is True


def test_sysvars_setvar_set():
    sv = SysVars()
    sv.setvar_set("FILLETRAD", "3.5")
    assert sv["FILLETRAD"] == 3.5


def test_sysvars_setvar_set_readonly_raises():
    sv = SysVars()
    with pytest.raises(ValueError, match="read-only"):
        sv.setvar_set("ACADVER", "R11")


def test_sysvars_list_all():
    sv = SysVars()
    all_vars = sv.list_vars("*")
    assert len(all_vars) >= 40


def test_sysvars_list_wildcard():
    sv = SysVars()
    dim_vars = sv.list_vars("DIM*")
    assert len(dim_vars) >= 8
    names = [n for n, _, _ in dim_vars]
    assert "DIMSCALE" in names
    assert "DIMTXT" in names


def test_sysvars_persistence_roundtrip():
    sv = SysVars()
    sv["FILLETRAD"] = 5.0
    sv["PDMODE"] = 35
    data = sv.to_dict()

    sv2 = SysVars.from_dict(data)
    assert sv2["FILLETRAD"] == 5.0
    assert sv2["PDMODE"] == 35


def test_sysvars_persistence_skips_readonly():
    sv = SysVars()
    data = {"ACADVER": "HACKED", "FILLETRAD": 3.0}
    sv2 = SysVars.from_dict(data)
    assert sv2["ACADVER"] == "R10"  # readonly ignored
    assert sv2["FILLETRAD"] == 3.0


def test_sysvars_orthomode_toggle():
    sv = SysVars()
    sv["ORTHOMODE"] = 1
    assert sv["ORTHOMODE"] == 1
    sv["ORTHOMODE"] = 0
    assert sv["ORTHOMODE"] == 0


def test_sysvars_osmode_bitmask():
    sv = SysVars()
    # END(1) + MID(2) + CEN(4) = 7
    sv["OSMODE"] = 7
    assert sv["OSMODE"] == 7


def test_sysvars_count():
    sv = SysVars()
    names = sv.names
    assert "OSMODE" in names
    assert "ACADVER" in names
    assert "PDMODE" in names
    assert "PDSIZE" in names
    assert len(names) == 43  # 41 original + PDMODE + PDSIZE
