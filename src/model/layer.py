from dataclasses import dataclass


@dataclass
class Layer:
    name: str
    color: str = "7"
    linetype: str = "CONTINUOUS"
    visible: bool = True
    locked: bool = False
    lineweight: float = 0.25

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "linetype": self.linetype,
            "visible": self.visible,
            "locked": self.locked,
            "lineweight": self.lineweight,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Layer":
        return cls(**data)
