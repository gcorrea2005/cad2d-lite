from src.model.layer import Layer


class LayerManager:
    def __init__(self):
        self.layers: dict[str, Layer] = {"0": Layer(name="0", color="7")}
        self._current = "0"

    @property
    def current_layer_name(self) -> str:
        return self._current

    def add_layer(self, name: str, color: str = "7", linetype: str = "CONTINUOUS") -> Layer:
        if name in self.layers:
            raise ValueError(f"Layer '{name}' already exists")
        layer = Layer(name=name, color=color, linetype=linetype)
        self.layers[name] = layer
        return layer

    def delete_layer(self, name: str) -> bool:
        if name == "0":
            return False
        if name not in self.layers:
            return False
        del self.layers[name]
        if self._current == name:
            self._current = "0"
        return True

    def set_current(self, name: str):
        if name not in self.layers:
            raise ValueError(f"Layer '{name}' does not exist")
        self._current = name

    def to_dict(self) -> dict:
        return {
            "layers": [l.to_dict() for l in self.layers.values()],
            "current": self._current,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LayerManager":
        lm = cls()
        lm.layers.clear()
        for d in data.get("layers", []):
            layer = Layer.from_dict(d)
            lm.layers[layer.name] = layer
        lm._current = data.get("current", "0")
        return lm
