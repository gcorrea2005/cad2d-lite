from src.controller.commands.base_command import BaseCommand


class ModifyEntityCommand(BaseCommand):
    """Stores old and new state to support undo/redo for entity modifications."""

    def __init__(self, entity, old_dict: dict, new_dict: dict):
        self.entity = entity
        self.old_dict = old_dict
        self.new_dict = new_dict

    def execute(self, document) -> None:
        cls = type(self.entity)
        restored = cls.from_dict(self.new_dict)
        # Copy all attributes back to the original entity
        for key, value in restored.__dict__.items():
            setattr(self.entity, key, value)

    def undo(self, document) -> None:
        cls = type(self.entity)
        restored = cls.from_dict(self.old_dict)
        for key, value in restored.__dict__.items():
            setattr(self.entity, key, value)
