from abc import ABC, abstractmethod


class BaseCommand(ABC):
    @abstractmethod
    def execute(self, document) -> None:
        ...

    @abstractmethod
    def undo(self, document) -> None:
        ...
