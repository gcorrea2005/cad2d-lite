from src.model.layer import Layer
from src.model.layer_manager import LayerManager
import pytest


def test_layer_creation():
    l = Layer(name="walls", color="#00FF00")
    assert l.name == "walls"
    assert l.color == "#00FF00"
    assert l.visible is True
    assert l.locked is False

def test_layer_manager_default():
    lm = LayerManager()
    assert lm.current_layer_name == "0"
    assert "0" in lm.layers

def test_layer_manager_add_layer():
    lm = LayerManager()
    lm.add_layer("walls", "#FF0000")
    assert "walls" in lm.layers
    assert lm.layers["walls"].color == "#FF0000"

def test_layer_manager_set_current():
    lm = LayerManager()
    lm.add_layer("walls")
    lm.set_current("walls")
    assert lm.current_layer_name == "walls"

def test_layer_manager_cannot_delete_layer_0():
    lm = LayerManager()
    assert lm.delete_layer("0") is False

def test_layer_manager_delete_layer():
    lm = LayerManager()
    lm.add_layer("temp")
    assert lm.delete_layer("temp") is True
    assert "temp" not in lm.layers

def test_layer_manager_delete_layer_resets_current():
    lm = LayerManager()
    lm.add_layer("walls")
    lm.set_current("walls")
    lm.delete_layer("walls")
    assert lm.current_layer_name == "0"

def test_layer_manager_duplicate_layer_raises():
    lm = LayerManager()
    lm.add_layer("walls")
    with pytest.raises(ValueError):
        lm.add_layer("walls")

def test_layer_manager_set_nonexistent_raises():
    lm = LayerManager()
    with pytest.raises(ValueError):
        lm.set_current("nonexistent")

def test_layer_manager_to_dict():
    lm = LayerManager()
    lm.add_layer("walls", "#FF0000")
    d = lm.to_dict()
    lm2 = LayerManager.from_dict(d)
    assert lm2.layers["walls"].color == "#FF0000"
    assert lm2.current_layer_name == lm.current_layer_name
