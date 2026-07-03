from src.controller.tools.base_tool import BaseTool


class ToolManager:
    def __init__(self, view, document):
        self._view = view
        self._document = document
        self._tools: dict[str, BaseTool] = {}
        self._active_tool: BaseTool | None = None

    def register_tool(self, name: str, tool: BaseTool):
        self._tools[name] = tool

    def activate_tool(self, name: str):
        if self._active_tool:
            self._active_tool.deactivate()
        self._active_tool = self._tools.get(name)
        if self._active_tool:
            self._active_tool.activate()
            self._view.setCursor(self._active_tool.cursor())
