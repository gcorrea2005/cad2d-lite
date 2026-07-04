from src.model.layer_manager import LayerManager
from src.model.entities.base import CadEntity
from src.model.sysvars import SysVars
from src.controller.commands.base_command import BaseCommand
from src.controller.commands.add_entity import AddEntityCommand
from src.controller.commands.delete_entity import DeleteEntityCommand


class Document:
    def __init__(self, filename: str | None = None):
        self.filename = filename
        self.layer_manager = LayerManager()
        self.sysvars = SysVars()
        self._entities: dict[str, CadEntity] = {}
        self._entity_order: list[str] = []
        self._undo_stack: list[BaseCommand] = []
        self._redo_stack: list[BaseCommand] = []
        self._dirty = False
        self.block_defs: dict = {}  # block name → BlockDefinition

    @property
    def entities(self) -> list[CadEntity]:
        return [self._entities[uuid] for uuid in self._entity_order]

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def add_entity(self, entity: CadEntity) -> None:
        self.execute(AddEntityCommand(entity))

    def remove_entity(self, uuid: str) -> None:
        entity = self._entities.get(uuid)
        if entity:
            self.execute(DeleteEntityCommand(entity))

    def execute(self, command: BaseCommand) -> None:
        command.execute(self)
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._dirty = True

    def undo(self) -> None:
        if not self._undo_stack:
            return
        cmd = self._undo_stack.pop()
        cmd.undo(self)
        self._redo_stack.append(cmd)
        self._dirty = True

    def redo(self) -> None:
        if not self._redo_stack:
            return
        cmd = self._redo_stack.pop()
        cmd.execute(self)
        self._undo_stack.append(cmd)
        self._dirty = True
