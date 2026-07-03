from src.controller.commands.base_command import BaseCommand
from src.model.entities.base import CadEntity


class DeleteEntityCommand(BaseCommand):
    def __init__(self, entity: CadEntity):
        self.entity = entity

    def execute(self, document) -> None:
        del document._entities[self.entity.uuid]
        document._entity_order.remove(self.entity.uuid)

    def undo(self, document) -> None:
        document._entities[self.entity.uuid] = self.entity
        document._entity_order.append(self.entity.uuid)
